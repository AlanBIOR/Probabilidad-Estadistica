import base64
import io
import os
import matplotlib
matplotlib.use('Agg')  # Backend para servidores web (evita bloqueos de Tkinter)
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from flask import Flask, jsonify, render_template, request

app = Flask(__name__)


def calcular_cuartil_posicion(valores_ordenados, k):
    n = len(valores_ordenados)
    posicion = (k * (n + 1)) / 4.0
    if posicion <= 1.0:
        return float(valores_ordenados[0])
    if posicion >= float(n):
        return float(valores_ordenados[-1])
    indice_entero = int(posicion)
    parte_decimal = posicion - indice_entero
    x_inferior = valores_ordenados[indice_entero - 1]
    x_superior = valores_ordenados[indice_entero]
    return float(x_inferior + (parte_decimal * (x_superior - x_inferior)))


def calcular_moda_inteligente(valores_ordenados, s_pandas, num_bins):
    conteo = s_pandas.value_counts()
    max_frecuencia = int(conteo.max())

    if max_frecuencia > 1:
        valor_modal = conteo[conteo == max_frecuencia].index[0]
        unicos = np.sort(s_pandas.unique())
        posicion_modal = int(np.where(unicos == valor_modal)[0][0])
        fm = float(max_frecuencia)
        L = float(unicos[posicion_modal - 1]) if posicion_modal > 0 else float(valor_modal)
        f1 = float((valores_ordenados == L).sum()) if posicion_modal > 0 else 0.0
        siguiente = float(unicos[posicion_modal + 1]) if posicion_modal < (len(unicos) - 1) else float(valor_modal)
        f2 = float((valores_ordenados == siguiente).sum()) if posicion_modal < (len(unicos) - 1) else 0.0
        h = siguiente - L
        delta_1 = fm - f1
        delta_2 = fm - f2
        den = delta_1 + delta_2
        moda_final = L + ((delta_1 * h) / den) if den != 0 else L + (h / 2.0)
        return float(moda_final), f"Dato modal {valor_modal} (fm={int(fm)})."
    else:
        frecuencias, bordes = np.histogram(valores_ordenados, bins=num_bins)
        indice_modal = int(np.argmax(frecuencias))
        fm = float(frecuencias[indice_modal])
        L = float(bordes[indice_modal])
        h = float(bordes[indice_modal + 1] - bordes[indice_modal])
        f1 = float(frecuencias[indice_modal - 1]) if indice_modal > 0 else 0.0
        f2 = float(frecuencias[indice_modal + 1]) if indice_modal < (len(frecuencias) - 1) else 0.0
        delta_1 = fm - f1
        delta_2 = fm - f2
        den = delta_1 + delta_2
        moda_final = L + ((delta_1 * h) / den) if den != 0 else L + (h / 2.0)
        return float(moda_final), "Intervalo modal agrupado."


def calcular_metricas_vector(datos_crudos, metricas_solicitadas):
    serie = pd.Series(datos_crudos, dtype=float).dropna()
    n = len(serie)
    if n == 0:
        return None

    valores = np.sort(serie.values)
    resultados = {}
    advertencias = {}

    media = float(np.mean(valores))
    mediana = float(np.median(valores))
    minimo = float(valores[0])
    maximo = float(valores[-1])
    rango = float(maximo - minimo)

    var_muestral = float(np.var(valores, ddof=1)) if n > 1 else 0.0
    var_poblacional = float(np.var(valores, ddof=0))
    std_muestral = float(np.std(valores, ddof=1)) if n > 1 else 0.0
    std_poblacional = float(np.std(valores, ddof=0))

    if "mean" in metricas_solicitadas or "all" in metricas_solicitadas:
        resultados["mean"] = media
    if "sample_variance" in metricas_solicitadas or "all" in metricas_solicitadas:
        resultados["sample_variance"] = var_muestral
    if "population_variance" in metricas_solicitadas or "all" in metricas_solicitadas:
        resultados["population_variance"] = var_poblacional
    if "sample_std" in metricas_solicitadas or "all" in metricas_solicitadas:
        resultados["sample_std"] = std_muestral
    if "population_std" in metricas_solicitadas or "all" in metricas_solicitadas:
        resultados["population_std"] = std_poblacional

    if "harmonic" in metricas_solicitadas or "all" in metricas_solicitadas:
        if (valores == 0).any():
            resultados["harmonic"] = None
            advertencias["harmonic"] = "Indefinida: Contiene ceros."
        elif (valores < 0).any():
            resultados["harmonic"] = None
            advertencias["harmonic"] = "Contiene negativos."
        else:
            suma_inv = float(np.sum(1.0 / valores))
            resultados["harmonic"] = float(n / suma_inv) if suma_inv != 0 else None

    if "geometric" in metricas_solicitadas or "all" in metricas_solicitadas:
        if (valores <= 0).any():
            resultados["geometric"] = None
            advertencias["geometric"] = "Requiere valores mayores a cero."
        else:
            resultados["geometric"] = float(np.exp(np.mean(np.log(valores))))

    num_bins = int(np.clip(np.sqrt(n), 6, 15))

    if "mode" in metricas_solicitadas or "all" in metricas_solicitadas:
        moda_calculada, adv_moda = calcular_moda_inteligente(valores, serie, num_bins)
        resultados["mode"] = [moda_calculada]
        advertencias["mode"] = adv_moda

    if "quartiles" in metricas_solicitadas or "all" in metricas_solicitadas:
        q1 = calcular_cuartil_posicion(valores, 1)
        q2 = calcular_cuartil_posicion(valores, 2)
        q3 = calcular_cuartil_posicion(valores, 3)
        resultados["quartiles"] = {
            "q1": q1, "q2": q2, "q3": q3,
            "iqr": float(q3 - q1), "range": float(rango),
            "min": minimo, "max": maximo
        }

    sesgo = "Distribución simétrica"
    if std_muestral > 0:
        dif = media - mediana
        if dif > (0.05 * std_muestral):
            sesgo = "Sesgo positivo (Media > Mediana)"
        elif dif < -(0.05 * std_muestral):
            sesgo = "Sesgo negativo (Media < Mediana)"

    frecuencias, bordes = np.histogram(valores, bins=num_bins)
    labels_bins = [f"{round(bordes[i], 2)} - {round(bordes[i+1], 2)}" for i in range(len(frecuencias))]
    bin_centers = [(bordes[i] + bordes[i + 1]) / 2.0 for i in range(len(frecuencias))]
    posicion_media = int(np.clip(np.digitize(media, bordes) - 1, 0, len(frecuencias) - 1))

    curva_teorica = []
    if std_muestral > 0:
        ancho = bordes[1] - bordes[0]
        raiz = std_muestral * np.sqrt(2 * np.pi)
        for c in bin_centers:
            d = (1.0 / raiz) * np.exp(-0.5 * (((c - media) / std_muestral) ** 2))
            curva_teorica.append(float(d * n * ancho))

    return {
        "results": resultados,
        "warnings": advertencias,
        "chart": {
            "labels": labels_bins,
            "counts": [int(f) for f in frecuencias],
            "curve": curva_teorica,
            "mean_bin_index": posicion_media,
            "mean_value": round(media, 4),
            "median_value": round(mediana, 4),
            "skewness": sesgo,
            "n": n
        }
    }


def generar_grafico_matplotlib(x_vals, y_vals, col_x="X", col_y="Y"):
    """Genera la figura de dispersión con recta de regresión usando Matplotlib."""
    df_par = pd.DataFrame({"X": x_vals, "Y": y_vals}).dropna()
    if len(df_par) < 2:
        return None, None

    cov_muestral = float(df_par["X"].cov(df_par["Y"]))
    r_pearson = float(df_par["X"].corr(df_par["Y"]))

    # Recta de regresión: y = mx + b
    m, b = np.polyfit(df_par["X"], df_par["Y"], 1)

    # 1. Renderizado en Matplotlib
    fig, ax = plt.subplots(figsize=(7.5, 4.8), facecolor="#0a111d")
    ax.set_facecolor("#112340")

    ax.scatter(df_par["X"], df_par["Y"], color="#8cb7fc", edgecolors="#ffffff", s=65, alpha=0.9, zorder=3, label="Observaciones")

    x_linea = np.linspace(df_par["X"].min(), df_par["X"].max(), 100)
    y_linea = m * x_linea + b
    ax.plot(x_linea, y_linea, color="#ff6b6b", linestyle="--", linewidth=2, label=f"Tendencia: y = {m:.2f}x + {b:.2f}")

    ax.set_title(f"Diagrama de Dispersión (Matplotlib)\nCov = {cov_muestral:.4f} | r = {r_pearson:.4f}", color="#eeeeef", fontsize=11, pad=12)
    ax.set_xlabel(col_x, color="#b4b3b7", labelpad=8)
    ax.set_ylabel(col_y, color="#b4b3b7", labelpad=8)
    ax.tick_params(colors="#b4b3b7")
    for spine in ax.spines.values():
        spine.set_color("#27487d")
    ax.grid(True, linestyle=":", alpha=0.4, color="#27487d")
    ax.legend(facecolor="#0a111d", edgecolor="#27487d", labelcolor="#eeeeef")
    fig.tight_layout()

    buffer = io.BytesIO()
    fig.savefig(buffer, format="png", dpi=130, facecolor=fig.get_facecolor(), edgecolor="none")
    plt.close(fig)
    buffer.seek(0)
    imagen_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")

    # 2. Datos vectorizados para el visor interactivo (coordenadas con hover)
    puntos_interactivos = [{"x": float(row["X"]), "y": float(row["Y"])} for _, row in df_par.iterrows()]
    linea_tendencia = [
        {"x": float(df_par["X"].min()), "y": float(m * df_par["X"].min() + b)},
        {"x": float(df_par["X"].max()), "y": float(m * df_par["X"].max() + b)}
    ]

    payload_bivariado = {
        "image_base64": f"data:image/png;base64,{imagen_base64}",
        "points": puntos_interactivos,
        "trend_line": linea_tendencia,
        "cov": cov_muestral,
        "r": r_pearson,
        "equation": f"y = {m:.4f}x + {b:.4f}",
        "col_x": col_x,
        "col_y": col_y
    }
    return payload_bivariado


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/process", methods=["POST"])
def process():
    metricas = request.form.getlist("metrics") or ["all"]
    columnas_analizadas = {}
    df_numerico = None

    if "file" in request.files:
        archivo = request.files["file"]
        if not archivo.filename:
            return jsonify({"success": False, "error": "No se seleccionó ningún archivo."}), 400

        contenido = archivo.read().decode("utf-8")
        if archivo.filename.lower().endswith(".csv"):
            lineas = [
                l.strip()[1:-1].replace('""', '"') if l.strip().startswith('"') and l.strip().endswith('"') and '""' in l.strip() else l.strip()
                for l in contenido.splitlines()
            ]
            df = pd.read_csv(io.StringIO("\n".join(lineas)), sep=None, engine="python")
            df.columns = [str(c).strip() for c in df.columns]
            cols_validas = [c for c in df.columns if pd.to_numeric(df[c], errors="coerce").dropna().count() > 0]
            if not cols_validas:
                return jsonify({"success": False, "error": "Sin columnas numéricas."}), 400
            df_numerico = df[cols_validas].apply(pd.to_numeric, errors="coerce").dropna()
            for c in cols_validas:
                analisis = calcular_metricas_vector(df_numerico[c].values, metricas)
                if analisis:
                    columnas_analizadas[c] = analisis
        else:
            numeros = [float(item) for item in contenido.replace(",", " ").replace(";", " ").split() if pd.to_numeric(pd.Series([item]), errors="coerce").notna().iloc[0]]
            if not numeros:
                return jsonify({"success": False, "error": "Sin datos numéricos válidos."}), 400
            analisis = calcular_metricas_vector(numeros, metricas)
            if analisis:
                columnas_analizadas["Texto Plano"] = analisis
    else:
        body = request.get_json(silent=True) or {}
        crudos = [float(x) for x in body.get("data", []) if pd.to_numeric(pd.Series([x]), errors="coerce").notna().iloc[0]]
        if not crudos:
            return jsonify({"success": False, "error": "Arreglo manual sin números válidos."}), 400
        analisis = calcular_metricas_vector(crudos, body.get("metrics", ["all"]))
        if analisis:
            columnas_analizadas["Entrada Manual"] = analisis

    if not columnas_analizadas:
        return jsonify({"success": False, "error": "No se pudieron procesar las variables."}), 400

    # Matriz de Covarianza y Gráfica Bivariada de Matplotlib
    cov_payload = None
    bivariado_payload = None

    if df_numerico is not None and df_numerico.shape[1] >= 2 and len(df_numerico) >= 2:
        # Matriz
        cov_matrix = np.cov(df_numerico.values, rowvar=False, ddof=1)
        if cov_matrix.ndim == 0:
            cov_matrix = np.array([[float(cov_matrix)]])
        cov_payload = {
            "columns": list(df_numerico.columns),
            "matrix": [[float(v) for v in row] for row in cov_matrix]
        }
        # Gráfica de dispersión del primer par disponible (X e Y)
        col_x, col_y = df_numerico.columns[0], df_numerico.columns[1]
        bivariado_payload = generar_grafico_matplotlib(df_numerico[col_x], df_numerico[col_y], col_x, col_y)

    return jsonify({
        "success": True,
        "columns": list(columnas_analizadas.keys()),
        "data": columnas_analizadas,
        "covariance": cov_payload,
        "bivariate": bivariado_payload
    })


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)