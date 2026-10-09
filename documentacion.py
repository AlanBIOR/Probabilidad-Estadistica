"""
===============================================================================
SISTEMA DE ANALISIS ESTADISTICO DESCRIPTIVO (BACKEND FLASK)
===============================================================================
Modulo de servidor web que expone una API REST para procesar vectores numericos
provenientes de entradas manuales o archivos tabulares (.csv / .txt).

Metricas implementadas:
    - Media Aritmetica: X_bar = sum(x) / n
    - Media Armonica: H = n / sum(1/x)
    - Media Geometrica: G = exp( (1/n) * sum(ln(x)) )
    - Moda Inteligente:
        * Caso 1 (Con repeticiones): Interpolacion con vecinos adyacentes.
        * Caso 2 (Amodal puntual): Interpolacion sobre el intervalo modal del histograma.
    - Cuartiles y RIC: Posicion L_k = (k * (n + 1)) / 4 con interpolacion lineal.
    - Rango: R = Max - Min
    - Deteccion de Sesgo / Asimetria: Comparacion Media vs Mediana.
===============================================================================
"""

import io
import numpy as np
import pandas as pd
from flask import Flask, jsonify, render_template, request

app = Flask(__name__)


def calcular_cuartil_posicion(valores_ordenados, k):
    """
    Calcula el k-esimo cuartil (k = 1, 2, 3) a partir de la formula de posicion:
        L_k = (k * (n + 1)) / 4
    
    Si la posicion L_k no es entera, aplica interpolacion lineal entre los datos
    adyacentes de la muestra ordenada:
        Q_k = x_inferior + parte_decimal * (x_superior - x_inferior)
    
    Parametros:
        valores_ordenados (ndarray): Array de numeros ordenados ascendentemente.
        k (int): Numero de cuartil deseado (1 para Q1, 2 para Mediana, 3 para Q3).
        
    Retorna:
        float: Valor interpolado del cuartil.
    """
    n = len(valores_ordenados)
    
    # Calculo de la posicion teorica segun la formula academica
    posicion = (k * (n + 1)) / 4.0
    
    # Cota inferior: si la posicion es menor o igual al primer elemento
    if posicion <= 1.0:
        return float(valores_ordenados[0])
    
    # Cota superior: si la posicion excede o iguala el tamano de la muestra
    if posicion >= float(n):
        return float(valores_ordenados[-1])
    
    # Descomposicion de la posicion en indice base y fraccion decimal
    indice_entero = int(posicion)
    parte_decimal = posicion - indice_entero
    
    # Mapeo a indices de Python (base 0):
    # El dato inferior se ubica en el indice (indice_entero - 1)
    # El dato superior se ubica en el indice (indice_entero)
    x_inferior = valores_ordenados[indice_entero - 1]
    x_superior = valores_ordenados[indice_entero]
    
    # Interpolacion lineal proporcional
    cuartil = x_inferior + (parte_decimal * (x_superior - x_inferior))
    
    return float(cuartil)


def calcular_moda_inteligente(valores_ordenados, s_pandas, num_bins):
    """
    Calcula la moda aproximada utilizando la formula de interpolacion modal:
        Mo = L + [ (fm - f1) * h ] / [ (fm - f1) + (fm - f2) ]
        
    Bifurcacion de logica:
        - Caso 1 (Existen datos repetidos con frecuencia > 1):
          Toma el valor de mayor frecuencia puntual, su dato anterior como limite
          inferior L, la distancia al siguiente dato como amplitud h, y las frecuencias
          de ambos vecinos como f1 y f2.
        - Caso 2 (Todos los datos son unicos, frecuencia = 1):
          Agrupa los datos en cajas de histograma continuas y aplica la formula sobre
          el intervalo con mayor concentracion de observaciones.
          
    Parametros:
        valores_ordenados (ndarray): Vector ordenado de observaciones.
        s_pandas (pd.Series): Serie de Pandas para conteo rapido de frecuencias.
        num_bins (int): Cantidad de divisiones para el histograma de respaldo.
        
    Retorna:
        tuple: (moda_final: float, advertencia: str)
    """
    n = len(valores_ordenados)
    
    # Conteo de repeticiones por cada valor numerico individual
    conteo = s_pandas.value_counts()
    max_frecuencia = int(conteo.max())
    
    # -------------------------------------------------------------------------
    # CASO 1: Existen datos que se repiten (Frecuencia > 1)
    # -------------------------------------------------------------------------
    if max_frecuencia > 1:
        # Extraemos el valor puntual de mayor ocurrencia
        valor_modal = conteo[conteo == max_frecuencia].index[0]
        
        # Obtenemos los valores unicos ordenados para identificar vecinos inmediatos
        unicos = np.sort(s_pandas.unique())
        posicion_modal = int(np.where(unicos == valor_modal)[0][0])
        
        fm = float(max_frecuencia)
        
        # Identificacion del vecino inferior (L y f1)
        if posicion_modal > 0:
            L = float(unicos[posicion_modal - 1])
            f1 = float((valores_ordenados == L).sum())
        else:
            L = float(valor_modal)
            f1 = 0.0
            
        # Identificacion del vecino superior (siguiente y f2)
        if posicion_modal < (len(unicos) - 1):
            siguiente = float(unicos[posicion_modal + 1])
            f2 = float((valores_ordenados == siguiente).sum())
        else:
            siguiente = float(valor_modal)
            f2 = 0.0
            
        # Amplitud del intervalo modal definido por los vecinos
        h = siguiente - L
        
        # Diferencias de frecuencia relativas
        delta_1 = fm - f1
        delta_2 = fm - f2
        denominador = delta_1 + delta_2
        
        # Sustitucion en la formula modal
        if denominador != 0:
            moda_final = L + ((delta_1 * h) / denominador)
        else:
            moda_final = L + (h / 2.0)
            
        advertencia = f"Calculada con dato modal {valor_modal} (fm={int(fm)}) y vecinos L={L}, sig={siguiente}."
        return float(moda_final), advertencia

    # -------------------------------------------------------------------------
    # CASO 2: Ningun dato se repite (Frecuencia individual = 1)
    # -------------------------------------------------------------------------
    else:
        # Generamos la tabla de frecuencias continuas mediante el histograma
        frecuencias, bordes = np.histogram(valores_ordenados, bins=num_bins)
        
        indice_modal = int(np.argmax(frecuencias))
        
        fm = float(frecuencias[indice_modal])
        L = float(bordes[indice_modal])
        h = float(bordes[indice_modal + 1] - bordes[indice_modal])
        
        # Frecuencia de la clase previa
        if indice_modal > 0:
            f1 = float(frecuencias[indice_modal - 1])
        else:
            f1 = 0.0
            
        # Frecuencia de la clase posterior
        if indice_modal < (len(frecuencias) - 1):
            f2 = float(frecuencias[indice_modal + 1])
        else:
            f2 = 0.0
            
        delta_1 = fm - f1
        delta_2 = fm - f2
        denominador = delta_1 + delta_2
        
        # Sustitucion en la formula modal para intervalos continuos
        if denominador != 0:
            moda_final = L + ((delta_1 * h) / denominador)
        else:
            moda_final = L + (h / 2.0)
            
        advertencia = "Calculada por intervalos de histograma al no haber datos repetidos."
        return float(moda_final), advertencia


def calcular_metricas_vector(datos_crudos, metricas_solicitadas):
    """
    Funcion nucleo de procesamiento estadistico. Recibe un vector de datos,
    lo depura y computa de forma independiente cada medida seleccionada,
    construyendo adicionalmente los datos del histograma y la curva normal.
    """
    # Conversion a serie de pandas y depuracion de valores ausentes (NaN / None)
    serie = pd.Series(datos_crudos, dtype=float)
    serie = serie.dropna()
    
    n = len(serie)
    
    # Validacion de datos vacios
    if n == 0:
        return None

    # Array ordenado para facilitar cuartiles y extremos
    valores = np.sort(serie.values)
    
    resultados = {}
    advertencias = {}

    media = float(np.mean(valores))
    mediana = float(np.median(valores))
    
    minimo = float(valores[0])
    maximo = float(valores[-1])
    rango = float(maximo - minimo)
    
    # Desviacion estandar muestral (grados de libertad ddof=1)
    if n > 1:
        desviacion = float(np.std(valores, ddof=1))
    else:
        desviacion = 0.0

    # -------------------------------------------------------------------------
    # 1. Media Aritmetica
    # -------------------------------------------------------------------------
    if "mean" in metricas_solicitadas or "all" in metricas_solicitadas:
        resultados["mean"] = media

    # -------------------------------------------------------------------------
    # 2. Media Armonica
    #    H = n / sum(1 / x) -> Requiere x != 0 y no admite numeros negativos
    # -------------------------------------------------------------------------
    if "harmonic" in metricas_solicitadas or "all" in metricas_solicitadas:
        tiene_ceros = False
        tiene_negativos = False

        for x in valores:
            if x == 0:
                tiene_ceros = True
            if x < 0:
                tiene_negativos = True

        if tiene_ceros:
            resultados["harmonic"] = None
            advertencias["harmonic"] = "Indefinida: El conjunto contiene ceros (division entre cero)."
        else:
            if tiene_negativos:
                resultados["harmonic"] = None
                advertencias["harmonic"] = "No recomendada: Contiene valores negativos."
            else:
                suma_inversos = 0.0
                for x in valores:
                    suma_inversos = suma_inversos + (1.0 / x)
                
                if suma_inversos != 0:
                    resultados["harmonic"] = float(n / suma_inversos)
                else:
                    resultados["harmonic"] = None
                    advertencias["harmonic"] = "La suma de inversos resulta igual a cero."

    # -------------------------------------------------------------------------
    # 3. Media Geometrica
    #    G = exp( (1/n) * sum(ln(x)) ) -> Formula logaritmica contra desbordamiento
    # -------------------------------------------------------------------------
    if "geometric" in metricas_solicitadas or "all" in metricas_solicitadas:
        es_valido_geom = True

        for x in valores:
            if x <= 0:
                es_valido_geom = False
                break

        if not es_valido_geom:
            resultados["geometric"] = None
            advertencias["geometric"] = "Indefinida: Requiere valores estrictamente positivos (x > 0)."
        else:
            suma_logaritmos = 0.0
            for x in valores:
                suma_logaritmos = suma_logaritmos + np.log(x)
            
            promedio_log = suma_logaritmos / n
            resultados["geometric"] = float(np.exp(promedio_log))

    # -------------------------------------------------------------------------
    # 4. Dimensionamiento de Bins del Histograma (Regla de la raiz cuadrada)
    # -------------------------------------------------------------------------
    num_bins = int(np.sqrt(n))
    if num_bins < 6:
        num_bins = 6
    if num_bins > 15:
        num_bins = 15

    # -------------------------------------------------------------------------
    # 5. Moda Inteligente
    # -------------------------------------------------------------------------
    if "mode" in metricas_solicitadas or "all" in metricas_solicitadas:
        moda_calculada, adv_moda = calcular_moda_inteligente(valores, serie, num_bins)
        
        resultados["mode"] = [moda_calculada]
        advertencias["mode"] = adv_moda

    # -------------------------------------------------------------------------
    # 6. Cuartiles y Rango Intercuartilico (RIC / IQR)
    # -------------------------------------------------------------------------
    if "quartiles" in metricas_solicitadas or "all" in metricas_solicitadas:
        q1 = calcular_cuartil_posicion(valores, 1)
        q2 = calcular_cuartil_posicion(valores, 2)
        q3 = calcular_cuartil_posicion(valores, 3)
        
        ric = q3 - q1

        resultados["quartiles"] = {
            "q1": q1,
            "q2": q2,
            "q3": q3,
            "iqr": float(ric),
            "range": float(rango),
            "min": minimo,
            "max": maximo
        }

    # -------------------------------------------------------------------------
    # 7. Diagnostico de Sesgo / Asimetria (Posicion relativa Media vs Mediana)
    # -------------------------------------------------------------------------
    if desviacion > 0:
        diferencia = media - mediana
        umbral = 0.05 * desviacion

        if diferencia > umbral:
            sesgo = "Sesgo positivo (A la derecha: Media > Mediana)"
        else:
            if diferencia < -umbral:
                sesgo = "Sesgo negativo (A la izquierda: Media < Mediana)"
            else:
                sesgo = "Distribucion simetrica (Media ≈ Mediana)"
    else:
        sesgo = "Varianza nula (Datos constantes)"

    # -------------------------------------------------------------------------
    # 8. Generacion de Bins y Curva Normal para Chart.js
    # -------------------------------------------------------------------------
    frecuencias, bordes = np.histogram(valores, bins=num_bins)

    labels_bins = []
    bin_centers = []

    for i in range(len(frecuencias)):
        lim_inf = round(bordes[i], 2)
        lim_sup = round(bordes[i + 1], 2)
        labels_bins.append(f"{lim_inf} - {lim_sup}")

        centro = (bordes[i] + bordes[i + 1]) / 2.0
        bin_centers.append(centro)

    # Identificacion de la barra donde se ubica la Media
    posicion_media = int(np.digitize(media, bordes) - 1)
    if posicion_media < 0:
        posicion_media = 0
    if posicion_media >= len(frecuencias):
        posicion_media = len(frecuencias) - 1

    # Construccion de la campana normal escalada a las frecuencias
    curva_teorica = []
    if desviacion > 0:
        ancho_bin = bordes[1] - bordes[0]
        factor_raiz = desviacion * np.sqrt(2 * np.pi)

        for centro in bin_centers:
            exponente = -0.5 * (((centro - media) / desviacion) ** 2)
            densidad = (1.0 / factor_raiz) * np.exp(exponente)
            altura_curva = densidad * n * ancho_bin
            curva_teorica.append(float(altura_curva))

    lista_frecuencias = []
    for f in frecuencias:
        lista_frecuencias.append(int(f))

    # Objeto estructurado para el renderizado del frontend
    chart_payload = {
        "labels": labels_bins,
        "counts": lista_frecuencias,
        "curve": curva_teorica,
        "mean_bin_index": posicion_media,
        "mean_value": round(media, 4),
        "median_value": round(mediana, 4),
        "skewness": sesgo,
        "n": n
    }

    respuesta_final = {
        "results": resultados,
        "warnings": advertencias,
        "chart": chart_payload
    }

    return respuesta_final


@app.route("/")
def index():
    """Ruta principal del servidor web."""
    return render_template("index.html")


@app.route("/api/process", methods=["POST"])
def process():
    """
    Endpoint principal de calculo:
    Determina si la peticion contiene un archivo subido (FormData) o un JSON
    con datos manuales, procesando todas las variables numericas encontradas.
    """
    metricas = request.form.getlist("metrics")
    if not metricas:
        metricas = ["all"]

    columnas_analizadas = {}

    # -------------------------------------------------------------------------
    # ENTRADA VIA ARCHIVO (.CSV / .TXT)
    # -------------------------------------------------------------------------
    if "file" in request.files:
        archivo = request.files["file"]
        nombre = archivo.filename.lower()

        if nombre == "":
            return jsonify({
                "success": False,
                "error": "No se selecciono ningun archivo para procesar."
            }), 400

        contenido_bytes = archivo.read()
        contenido = contenido_bytes.decode("utf-8")
        stream = io.StringIO(contenido)

        # Caso archivo CSV: procesa todas las columnas numericas
        if nombre.endswith(".csv"):
            df = pd.read_csv(stream)
            
            columnas_todas = df.columns
            columnas_numericas = []

            for col in columnas_todas:
                serie_num = pd.to_numeric(df[col], errors="coerce")
                if serie_num.dropna().count() > 0:
                    columnas_numericas.append(col)

            if len(columnas_numericas) == 0:
                return jsonify({
                    "success": False,
                    "error": "El archivo CSV no contiene columnas con datos numericos."
                }), 400

            for col in columnas_numericas:
                serie_limpia = pd.to_numeric(df[col], errors="coerce").dropna().tolist()
                analisis = calcular_metricas_vector(serie_limpia, metricas)
                if analisis is not None:
                    columnas_analizadas[col] = analisis

        # Caso archivo de texto plano: parsea todos los numeros separados
        else:
            texto_limpio = contenido.replace(",", " ").replace(";", " ")
            palabras = texto_limpio.split()
            
            datos_numericos = []
            for item in palabras:
                item = item.strip()
                if item != "":
                    val_serie = pd.to_numeric(pd.Series([item]), errors="coerce")
                    if not val_serie.isna().iloc[0]:
                        datos_numericos.append(float(val_serie.iloc[0]))

            if len(datos_numericos) == 0:
                return jsonify({
                    "success": False,
                    "error": "El archivo de texto no contiene datos numericos legibles."
                }), 400

            analisis = calcular_metricas_vector(datos_numericos, metricas)
            if analisis is not None:
                columnas_analizadas["Texto Plano"] = analisis

    # -------------------------------------------------------------------------
    # ENTRADA VIA CAPTURA MANUAL (JSON)
    # -------------------------------------------------------------------------
    else:
        body = request.get_json(silent=True)
        if not body:
            return jsonify({
                "success": False,
                "error": "No se recibieron datos en el cuerpo de la peticion."
            }), 400

        datos_crudos = body.get("data", [])
        metricas_body = body.get("metrics", ["all"])

        if len(datos_crudos) == 0:
            return jsonify({
                "success": False,
                "error": "El arreglo de muestras manuales esta vacio."
            }), 400

        datos_numericos = []
        for x in datos_crudos:
            val_serie = pd.to_numeric(pd.Series([x]), errors="coerce")
            if not val_serie.isna().iloc[0]:
                datos_numericos.append(float(val_serie.iloc[0]))

        if len(datos_numericos) == 0:
            return jsonify({
                "success": False,
                "error": "Ninguno de los valores manuales ingresados corresponde a un numero valido."
            }), 400

        analisis = calcular_metricas_vector(datos_numericos, metricas_body)
        if analisis is not None:
            columnas_analizadas["Entrada Manual"] = analisis

    # Validacion general de salida
    if len(columnas_analizadas) == 0:
        return jsonify({
            "success": False,
            "error": "No fue posible calcular las metricas con la informacion provista."
        }), 400

    lista_nombres_columnas = list(columnas_analizadas.keys())

    return jsonify({
        "success": True,
        "columns": lista_nombres_columnas,
        "data": columnas_analizadas
    })


if __name__ == "__main__":
    app.run(
        debug=True,
        host="0.0.0.0",
        port=5000
    )

# Terminal

"""
===============================================================================
CALCULADORA ESTADISTICA DESCRIPTIVA (CONSOLA / TERMINAL)
===============================================================================
Script interactivo en linea de comandos para calculos estadisticos puros.
Implementa:
    - Media Aritmetica, Armonica y Geometrica.
    - Cuartiles e Interpolacion con la formula L_k = (k * (n + 1)) / 4.
    - Rango (R) y Rango Intercuartilico (RIC = Q3 - Q1).
    - Moda Inteligente (Vecinos adyacentes si hay repeticion, o histograma).
    - Diagnostico de asimetria / sesgo.
===============================================================================
"""

import numpy as np
import pandas as pd


def calcular_cuartil(valores_ordenados, k):
    """Calcula la posicion L_k = k(n+1)/4 y aplica interpolacion lineal."""
    n = len(valores_ordenados)
    posicion = (k * (n + 1)) / 4.0
    
    if posicion <= 1.0:
        return float(valores_ordenados[0]), posicion
    
    if posicion >= float(n):
        return float(valores_ordenados[-1]), posicion
    
    indice_entero = int(posicion)
    parte_decimal = posicion - indice_entero
    
    x_inf = valores_ordenados[indice_entero - 1]
    x_sup = valores_ordenados[indice_entero]
    
    cuartil = x_inf + (parte_decimal * (x_sup - x_inf))
    return float(cuartil), posicion


def calcular_moda(valores_ordenados, serie):
    """Calcula la moda usando vecinos si existen repeticiones o histograma si no."""
    n = len(valores_ordenados)
    conteo = serie.value_counts()
    max_freq = int(conteo.max())
    
    # Caso 1: Hay datos repetidos (como el 88 en la muestra de clase)
    if max_freq > 1:
        valor_modal = conteo[conteo == max_freq].index[0]
        unicos = np.sort(serie.unique())
        idx = int(np.where(unicos == valor_modal)[0][0])
        
        fm = float(max_freq)
        
        if idx > 0:
            L = float(unicos[idx - 1])
            f1 = float((valores_ordenados == L).sum())
        else:
            L = float(valor_modal)
            f1 = 0.0
            
        if idx < (len(unicos) - 1):
            sig = float(unicos[idx + 1])
            f2 = float((valores_ordenados == sig).sum())
        else:
            sig = float(valor_modal)
            f2 = 0.0
            
        h = sig - L
        d1 = fm - f1
        d2 = fm - f2
        den = d1 + d2
        
        if den != 0:
            moda = L + ((d1 * h) / den)
        else:
            moda = L + (h / 2.0)
            
        detalles = {
            "metodo": "Vecinos Adyacentes (Datos con repeticion)",
            "valor_modal": valor_modal,
            "L": L,
            "h": h,
            "fm": fm,
            "f1": f1,
            "f2": f2,
            "d1": d1,
            "d2": d2
        }
        return float(moda), detalles
        
    # Caso 2: Ningun dato se repite
    else:
        num_bins = int(np.sqrt(n))
        if num_bins < 6:
            num_bins = 6
            
        frecuencias, bordes = np.histogram(valores_ordenados, bins=num_bins)
        idx_modal = int(np.argmax(frecuencias))
        
        fm = float(frecuencias[idx_modal])
        L = float(bordes[idx_modal])
        h = float(bordes[idx_modal + 1] - bordes[idx_modal])
        
        if idx_modal > 0:
            f1 = float(frecuencias[idx_modal - 1])
        else:
            f1 = 0.0
            
        if idx_modal < (len(frecuencias) - 1):
            f2 = float(frecuencias[idx_modal + 1])
        else:
            f2 = 0.0
            
        d1 = fm - f1
        d2 = fm - f2
        den = d1 + d2
        
        if den != 0:
            moda = L + ((d1 * h) / den)
        else:
            moda = L + (h / 2.0)
            
        detalles = {
            "metodo": "Intervalos de Histograma (Sin repeticiones)",
            "valor_modal": "Amodal puntual",
            "L": round(L, 2),
            "h": round(h, 2),
            "fm": fm,
            "f1": f1,
            "f2": f2,
            "d1": d1,
            "d2": d2
        }
        return float(moda), detalles


def analizar_muestra_consola(nombre_variable, datos_lista):
    """Imprime el desglose estadistico completo en consola."""
    serie = pd.Series(datos_lista, dtype=float).dropna()
    n = len(serie)
    
    if n == 0:
        print(f"\n[!] La variable '{nombre_variable}' no contiene datos validos.")
        return
        
    valores = np.sort(serie.values)
    
    media = float(np.mean(valores))
    mediana = float(np.median(valores))
    minimo = float(valores[0])
    maximo = float(valores[-1])
    rango = maximo - minimo
    
    if n > 1:
        desviacion = float(np.std(valores, ddof=1))
    else:
        desviacion = 0.0

    print("\n" + "=" * 65)
    print(f" ANALISIS ESTADISTICO: {nombre_variable.upper()}")
    print("=" * 65)
    print(f"Muestras validas (n)   : {n}")
    print(f"Datos ordenados        : {valores.tolist()}")
    print("-" * 65)

    # 1. Media Aritmetica
    print(f"[*] Media Aritmetica (X_bar) : {media:.4f}")

    # 2. Media Armonica
    if (valores == 0).any():
        print("[*] Media Armonica (H)      : Indefinida (Contiene ceros)")
    else:
        if (valores < 0).any():
            print("[*] Media Armonica (H)      : No recomendada (Contiene negativos)")
        else:
            suma_inv = sum(1.0 / x for x in valores)
            h_mean = n / suma_inv
            print(f"[*] Media Armonica (H)      : {h_mean:.4f}")

    # 3. Media Geometrica
    if (valores <= 0).any():
        print("[*] Media Geometrica (G)    : Indefinida (Valores <= 0)")
    else:
        suma_ln = sum(np.log(x) for x in valores)
        g_mean = np.exp(suma_ln / n)
        print(f"[*] Media Geometrica (G)    : {g_mean:.4f}")

    # 4. Moda Inteligente
    moda, info_moda = calcular_moda(valores, serie)
    print(f"[*] Moda Agrupada (Mo)      : {moda:.4f}")
    print(f"    - Metodo                : {info_moda['metodo']}")
    print(f"    - Limite inferior (L)   : {info_moda['L']}")
    print(f"    - Amplitud (h)          : {info_moda['h']}")
    print(f"    - Frecuencias           : fm={info_moda['fm']}, f1={info_moda['f1']}, f2={info_moda['f2']}")
    print(f"    - Diferencias           : d1={info_moda['d1']}, d2={info_moda['d2']}")

    # 5. Cuartiles y RIC
    q1, pos1 = calcular_cuartil(valores, 1)
    q2, pos2 = calcular_cuartil(valores, 2)
    q3, pos3 = calcular_cuartil(valores, 3)
    ric = q3 - q1

    print("-" * 65)
    print(f"[*] Minimo                  : {minimo:.2f}")
    print(f"[*] Cuartil 1 (Q1)          : {q1:.4f}  (Posicion L1 = {pos1:.2f})")
    print(f"[*] Mediana   (Q2)          : {q2:.4f}  (Posicion L2 = {pos2:.2f})")
    print(f"[*] Cuartil 3 (Q3)          : {q3:.4f}  (Posicion L3 = {pos3:.2f})")
    print(f"[*] Maximo                  : {maximo:.2f}")
    print(f"[*] Rango (Max - Min)       : {rango:.4f}")
    print(f"[*] Rango Intercuartil (RIC): {ric:.4f}  (Q3 - Q1)")

    # 6. Sesgo / Asimetria
    print("-" * 65)
    if desviacion > 0:
        diferencia = media - mediana
        umbral = 0.05 * desviacion
        if diferencia > umbral:
            sesgo = "Sesgo positivo (A la derecha: Media > Mediana)"
        else:
            if diferencia < -umbral:
                sesgo = "Sesgo negativo (A la izquierda: Media < Mediana)"
            else:
                sesgo = "Distribucion simetrica (Media ≈ Mediana)"
    else:
        sesgo = "Varianza nula (Datos identicos)"
        
    print(f"[*] Diagnostico de Sesgo    : {sesgo}")
    print("=" * 65 + "\n")


def menu():
    """Menu interactivo de consola."""
    while True:
        print("\n=== PANEL DE CONTROL ESTADISTICO EN TERMINAL ===")
        print("1. Ejecutar con los datos del ejemplo de clase (n=18)")
        print("2. Ingresar datos manualmente por teclado")
        print("3. Analizar archivo CSV completo")
        print("4. Analizar archivo de texto plano (.txt)")
        print("5. Salir")
        
        opcion = input("Selecciona una opcion (1-5): ").strip()
        
        if opcion == "1":
            datos_clase = [24, 58, 61, 67, 71, 73, 76, 79, 82, 83, 85, 87, 88, 88, 92, 93, 94, 97]
            analizar_muestra_consola("Ejemplo de Clase", datos_clase)
            
        elif opcion == "2":
            entrada = input("\nIngresa los numeros separados por coma o espacio:\n> ")
            texto = entrada.replace(",", " ").replace(";", " ")
            numeros = []
            for item in texto.split():
                s = pd.to_numeric(pd.Series([item]), errors="coerce")
                if not s.isna().iloc[0]:
                    numeros.append(float(s.iloc[0]))
                    
            if len(numeros) > 0:
                analizar_muestra_consola("Entrada Manual", numeros)
            else:
                print("[!] No se detectaron valores numericos validos.")
                
        elif opcion == "3":
            ruta = input("\nRuta del archivo CSV (ejemplo: db/iris.csv): ").strip()
            df = pd.read_csv(ruta)
            cols_num = df.select_dtypes(include=[np.number]).columns.tolist()
            
            if len(cols_num) == 0:
                print("[!] El CSV no contiene columnas numericas.")
            else:
                print(f"\n[+] Se encontraron {len(cols_num)} columnas numericas:")
                for col in cols_num:
                    analizar_muestra_consola(col, df[col].dropna().tolist())
                    
        elif opcion == "4":
            ruta = input("\nRuta del archivo TXT: ").strip()
            with open(ruta, "r", encoding="utf-8") as f:
                contenido = f.read()
                
            texto = contenido.replace(",", " ").replace(";", " ")
            numeros = []
            for item in texto.split():
                s = pd.to_numeric(pd.Series([item]), errors="coerce")
                if not s.isna().iloc[0]:
                    numeros.append(float(s.iloc[0]))
                    
            if len(numeros) > 0:
                analizar_muestra_consola(f"Archivo TXT ({ruta})", numeros)
            else:
                print("[!] El archivo no contiene datos numericos.")
                
        elif opcion == "5":
            print("\nFinalizando ejecucion.")
            break
        else:
            print("[!] Opcion no valida. Intenta de nuevo.")


if __name__ == "__main__":
    menu()