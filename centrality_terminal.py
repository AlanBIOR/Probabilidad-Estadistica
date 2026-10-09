import io
import numpy as np
import pandas as pd


def calcular_cuartil(valores_ordenados, k):
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
    n = len(valores_ordenados)
    conteo = serie.value_counts()
    max_freq = int(conteo.max())
    
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
    serie = pd.Series(datos_lista, dtype=float).dropna()
    n = len(serie)
    
    if n == 0:
        print(f"\n[!] La variable '{nombre_variable}' no contiene datos validos.")
        return
        
    valores = np.sort(serie.values)
    
    suma_datos = 0.0
    for x in valores:
        suma_datos = suma_datos + x
    media = suma_datos / n

    mediana = float(np.median(valores))
    minimo = float(valores[0])
    maximo = float(valores[-1])
    rango = maximo - minimo
    desviacion_estandar = float(np.std(valores))
    desviacion_estandar_cuadrada = desviacion_estandar ** 2
    
    if n > 1:
        desviacion = float(np.std(valores, ddof=1))
        desviacion_cuadrada = desviacion ** 2
    else:
        desviacion = 0.0
        desviacion_cuadrada = 0.0

    print("\n" + "=" * 65)
    print(f" ANALISIS ESTADISTICO: {nombre_variable.upper()}")
    print("=" * 65)
    print(f"Muestras validas (n)   : {n}")
    print(f"Datos ordenados        : {valores.tolist()}")
    print("-" * 65)

    print(f"[*] Media Aritmetica (X_bar) : {media:.4f}")

    tiene_ceros = False
    tiene_negativos = False

    for x in valores:
        if x == 0:
            tiene_ceros = True
        if x < 0:
            tiene_negativos = True

    if tiene_ceros:
        print("[*] Media Armonica (H)      : Indefinida (Contiene ceros)")
    else:
        if tiene_negativos:
            print("[*] Media Armonica (H)      : No recomendada (Contiene negativos)")
        else:
            suma_inv = 0.0
            for x in valores:
                suma_inv = suma_inv + (1.0 / x)
                
            if suma_inv != 0:
                h_mean = n / suma_inv
                print(f"[*] Media Armonica (H)      : {h_mean:.4f}")
            else:
                print("[*] Media Armonica (H)      : Indefinida (Suma de inversos igual a 0)")

    tiene_no_positivos = False

    for x in valores:
        if x <= 0:
            tiene_no_positivos = True
            break

    if tiene_no_positivos:
        print("[*] Media Geometrica (G)    : Indefinida (Valores <= 0)")
    else:
        suma_ln = 0.0
        for x in valores:
            suma_ln = suma_ln + np.log(x)
            
        g_mean = float(np.exp(suma_ln / n))
        print(f"[*] Media Geometrica (G)    : {g_mean:.4f}")

    moda, info_moda = calcular_moda(valores, serie)
    print(f"[*] Moda Agrupada (Mo)      : {moda:.4f}")
    print(f"    - Metodo                : {info_moda['metodo']}")
    print(f"    - Limite inferior (L)   : {info_moda['L']}")
    print(f"    - Amplitud (h)          : {info_moda['h']}")
    print(f"    - Frecuencias           : fm={info_moda['fm']}, f1={info_moda['f1']}, f2={info_moda['f2']}")
    print(f"    - Diferencias           : d1={info_moda['d1']}, d2={info_moda['d2']}")

    print(f'desviacion estandar (σ)     : {desviacion_estandar:.4f}')
    print(f'desviacion muestral (s)     : {desviacion:.4f}')
    print(f'desviacion estandar (σ^2)     : {desviacion_estandar_cuadrada:.4f}')
    print(f'desviacion muestral (s^2)     : {desviacion_cuadrada:.4f}')
    
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
            ruta = input("\nRuta del archivo CSV (ejemplo: db/generacion_liquidada_ago.csv): ").strip()
            
            with open(ruta, "r", encoding="utf-8", errors="ignore") as f:
                lineas = f.read().splitlines()
                
            lineas_limpias = []
            for l in lineas:
                l_str = l.strip()
                if l_str.startswith('"') and l_str.endswith('"') and '""' in l_str:
                    l_str = l_str[1:-1].replace('""', '"')
                lineas_limpias.append(l_str)
                
            stream = io.StringIO("\n".join(lineas_limpias))
            df = pd.read_csv(stream, sep=None, engine="python")
            df.columns = [str(col).strip() for col in df.columns]
            
            columnas_todas = df.columns
            columnas_numericas = []
            
            for col in columnas_todas:
                serie_num = pd.to_numeric(df[col], errors="coerce")
                if serie_num.dropna().count() > 0:
                    columnas_numericas.append(col)
            
            if len(columnas_numericas) == 0:
                print("[!] El CSV no contiene columnas numericas.")
            else:
                print(f"\n[+] Se encontraron {len(columnas_numericas)} columnas numericas:")
                for col in columnas_numericas:
                    serie_limpia = pd.to_numeric(df[col], errors="coerce").dropna().tolist()
                    analizar_muestra_consola(col, serie_limpia)
                    
        elif opcion == "4":
            ruta = input("\nRuta del archivo TXT: ").strip()
            with open(ruta, "r", encoding="utf-8", errors="ignore") as f:
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