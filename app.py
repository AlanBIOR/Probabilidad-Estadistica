import io
import numpy as np
import pandas as pd
from flask import Flask, jsonify, render_template, request

app = Flask(__name__)


def calcular_metricas_vector(s, metricas_solicitadas):
    """Calcula las métricas de un vector/columna individual y genera metadatos para la gráfica."""
    s = pd.Series(s, dtype=float).dropna()
    n = len(s)
    if n == 0:
        return None

    resultados = {}
    advertencias = {}

    media = float(np.mean(s))
    mediana = float(np.median(s))
    desv = float(np.std(s, ddof=1)) if n > 1 else 0.0

    # 1. Media Aritmética
    if "mean" in metricas_solicitadas or "all" in metricas_solicitadas:
        resultados["mean"] = media

    # 2. Media Armónica: H = n / sum(1/x)
    if "harmonic" in metricas_solicitadas or "all" in metricas_solicitadas:
        if (s == 0).any():
            resultados["harmonic"] = None
            advertencias["harmonic"] = "Indefinida: Contiene ceros (división por cero)."
        elif (s < 0).any():
            resultados["harmonic"] = None
            advertencias["harmonic"] = "No recomendada: Contiene valores negativos."
        else:
            resultados["harmonic"] = float(n / np.sum(1.0 / s))

    # 3. Media Geométrica: exp( (1/n) * sum(ln(x)) )
    if "geometric" in metricas_solicitadas or "all" in metricas_solicitadas:
        if (s <= 0).any():
            resultados["geometric"] = None
            advertencias["geometric"] = "Indefinida: Requiere valores estrictamente positivos (x > 0)."
        else:
            resultados["geometric"] = float(np.exp(np.mean(np.log(s))))

    # 4. Moda
    if "mode" in metricas_solicitadas or "all" in metricas_solicitadas:
        conteo = s.value_counts()
        max_freq = conteo.max()
        if max_freq == 1 and n > 1:
            resultados["mode"] = []
            advertencias["mode"] = "Amodal (sin repeticiones)."
        else:
            modas = conteo[conteo == max_freq].index.tolist()
            resultados["mode"] = [float(m) for m in modas]
            if len(modas) > 1:
                advertencias["mode"] = f"Multimodal ({len(modas)} modas)."

    # 5. Cuartiles y Rango Intercuartílico (IQR = Q3 - Q1)
    if "quartiles" in metricas_solicitadas or "all" in metricas_solicitadas:
        q1 = float(np.percentile(s, 25))
        q2 = mediana
        q3 = float(np.percentile(s, 75))
        resultados["quartiles"] = {
            "q1": q1,
            "q2": q2,
            "q3": q3,
            "iqr": float(q3 - q1),
            "min": float(np.min(s)),
            "max": float(np.max(s)),
        }

    # Sesgo / Asimetría (Relación Media vs Mediana)
    if desv > 0:
        diferencia = media - mediana
        umbral = 0.05 * desv
        if diferencia > umbral:
            sesgo = "Sesgo positivo (A la derecha: Media > Mediana)"
        elif diferencia < -umbral:
            sesgo = "Sesgo negativo (A la izquierda: Media < Mediana)"
        else:
            sesgo = "Distribución simétrica (Media ≈ Mediana)"
    else:
        sesgo = "Varianza nula (Datos constantes)"

    # Metadatos para el gráfico (Histograma y marcadores)
    num_bins = min(15, max(6, int(np.sqrt(n))))
    frecuencias, bordes = np.histogram(s, bins=num_bins)

    labels_bins = [f"{round(bordes[i], 2)} - {round(bordes[i+1], 2)}" for i in range(len(frecuencias))]
    bin_centers = [(bordes[i] + bordes[i + 1]) / 2 for i in range(len(frecuencias))]

    # Localizar el índice del contenedor (bin) donde se ubica la Media
    bin_media_idx = int(np.clip(np.digitize(media, bordes) - 1, 0, len(frecuencias) - 1))

    # Curva teórica normal escalada al histograma
    curva_teorica = []
    if desv > 0:
        ancho_bin = bordes[1] - bordes[0]
        curva_densidad = (1 / (desv * np.sqrt(2 * np.pi))) * np.exp(-0.5 * ((np.array(bin_centers) - media) / desv) ** 2)
        curva_teorica = (curva_densidad * n * ancho_bin).tolist()

    chart_payload = {
        "labels": labels_bins,
        "counts": frecuencias.tolist(),
        "curve": curva_teorica,
        "mean_bin_index": bin_media_idx,
        "mean_value": round(media, 4),
        "median_value": round(mediana, 4),
        "skewness": sesgo,
        "n": n,
    }

    return {
        "results": resultados,
        "warnings": advertencias,
        "chart": chart_payload,
    }


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/process", methods=["POST"])
def process():
    """Recibe datos manuales (JSON) o un archivo .csv / .txt (multipart/form-data) y calcula todo en bloque."""
    metricas = request.form.getlist("metrics") or ["all"]

    columnas_analizadas = {}

    if "file" in request.files:
        archivo = request.files["file"]
        nombre = archivo.filename.lower()

        try:
            contenido = archivo.read().decode("utf-8")
            stream = io.StringIO(contenido)

            if nombre.endswith(".csv"):
                df = pd.read_csv(stream)
                columnas_num = df.select_dtypes(include=[np.number]).columns.tolist()

                if not columnas_num:
                    return jsonify({"success": False, "error": "El CSV no tiene columnas numéricas."}), 400

                for col in columnas_num:
                    calc = calcular_metricas_vector(df[col], metricas)
                    if calc:
                        columnas_analizadas[col] = calc

            else:  # Archivo de texto plano
                lineas = contenido.replace(",", " ").replace(";", " ").split()
                datos = [float(x) for x in lineas if x.strip()]
                calc = calcular_metricas_vector(datos, metricas)
                if calc:
                    columnas_analizadas["Texto Plano"] = calc

        except Exception as e:
            return jsonify({"success": False, "error": f"Error al procesar el archivo: {str(e)}"}), 400

    else:
        # Petición manual vía JSON
        body = request.get_json(silent=True) or {}
        datos = body.get("data", [])
        metricas = body.get("metrics", ["all"])

        if not datos:
            return jsonify({"success": False, "error": "No se enviaron datos numéricos."}), 400

        try:
            calc = calcular_metricas_vector(datos, metricas)
            if calc:
                columnas_analizadas["Entrada Manual"] = calc
        except Exception as e:
            return jsonify({"success": False, "error": str(e)}), 400

    if not columnas_analizadas:
        return jsonify({"success": False, "error": "No se pudieron calcular métricas con los datos provistos."}), 400

    return jsonify({
        "success": True,
        "columns": list(columnas_analizadas.keys()),
        "data": columnas_analizadas,
    })


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)