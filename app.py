import base64
import io
from itertools import combinations
import os
import matplotlib
matplotlib.use('Agg')  # Configura Matplotlib para renderizar en memoria sin abrir ventanas de escritorio
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

        if posicion_modal > 0:
            L = float(unicos[posicion_modal - 1])
            f1 = float((valores_ordenados == L).sum())
        else:
            L = float(valor_modal)
            f1 = 0.0

        if posicion_modal < (len(unicos) - 1):
            siguiente = float(unicos[posicion_modal + 1])
            f2 = float((valores_ordenados == siguiente).sum())
        else:
            siguiente = float(valor_modal)
            f2 = 0.0

        h = siguiente - L
        delta_1 = fm - f1
        delta_2 = fm - f2
        den = delta_1 + delta_2

        if den != 0:
            moda_final = L + ((delta_1 * h) / den)
        else:
            moda_final = L + (h / 2.0)

        return float(moda_final), f"Dato modal {valor_modal} (fm={int(fm)})."
    else:
        frecuencias, bordes = np.histogram(valores_ordenados, bins=num_bins)
        indice_modal = int(np.argmax(frecuencias))
        fm = float(frecuencias[indice_modal])
        L = float(bordes[indice_modal])
        h = float(bordes[indice_modal + 1] - bordes[indice_modal])

        if indice_modal > 0:
            f1 = float(frecuencias[indice_modal - 1])
        else:
            f1 = 0.0

        if indice_modal < (len(frecuencias) - 1):
            f2 = float(frecuencias[indice_modal + 1])
        else:
            f2 = 0.0

        delta_1 = fm - f1
        delta_2 = fm - f2
        den = delta_1 + delta_2

        if den != 0:
            moda_final = L + ((delta_1 * h) / den)
        else:
            moda_final = L + (h / 2.0)

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

    # ddof=1 aplica n - 1 grados de libertad (muestra); ddof=0 aplica divisor N (población)[cite: 51, 52, 53, 55, 56]
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
            advertencias["harmonic"] = "Contiene valores negativos."
        else:
            suma_inv = float(np.sum(1.0 / valores))
            resultados["harmonic"] = float(n / suma_inv) if suma_inv != 0 else None

    if "geometric" in metricas_solicitadas or "all" in metricas_solicitadas:
        if (valores <= 0).any():
            resultados["geometric"] = None
            advertencias["geometric"] = "Requiere valores mayores a cero."
        else:
            resultados["geometric"] = float(np.exp(np.mean(np.log(valores))))

    # np.clip restringe el número de intervalos entre un mínimo de 6 y un máximo de 15
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

    # np.digitize localiza en qué intervalo cae la media aritmética
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


def parse_tabular_data(content_str, filename=""):
    lineas = [l.strip() for l in content_str.strip().splitlines() if l.strip()]
    if not lineas:
        return None

    lineas_limpias = []
    for l in lineas:
        if l.startswith('"') and l.endswith('"') and '""' in l:
            l = l[1:-1].replace('""', '"')
        lineas_limpias.append(l)
    clean_content = "\n".join(lineas_limpias)

    primeros_tokens = lineas_limpias[0].replace(",", " ").replace(";", " ").replace("\t", " ").split()
    tiene_encabezado = False
    for tok in primeros_tokens:
        tok_clean = tok.strip('\'"')
        # pd.isna con errors="coerce" identifica si el token es texto en vez de número
        if pd.isna(pd.to_numeric(tok_clean, errors="coerce")):
            tiene_encabezado = True
            break

    header_val = 0 if tiene_encabezado else None

    if filename.lower().endswith(".csv"):
        df = pd.read_csv(io.StringIO(clean_content), sep=None, engine="python", header=header_val)
    else:
        # Regex r"[\s,;]+" agrupa múltiples espacios, tabulaciones o comas como un solo separador
        df = pd.read_csv(io.StringIO(clean_content), sep=r"[\s,;]+", engine="python", header=header_val)

    if not tiene_encabezado:
        ncols = df.shape[1]
        if ncols == 1:
            df.columns = ["Variable"]
        elif ncols == 2:
            df.columns = ["X", "Y"]
        elif ncols == 3:
            df.columns = ["X", "Y", "Z"]
        else:
            df.columns = [f"Var_{i+1}" for i in range(ncols)]
    else:
        df.columns = [str(c).strip().strip('"').strip("'") for c in df.columns]

    # Conserva exclusivamente columnas numéricas válidas descartando columnas de texto
    df_numerico = pd.DataFrame()
    for col in df.columns:
        # errors="coerce" convierte strings no numéricos en NaN sin disparar excepciones
        serie_num = pd.to_numeric(df[col], errors="coerce")
        if serie_num.dropna().count() >= 1:
            df_numerico[str(col).strip()] = serie_num

    if df_numerico.empty:
        return None

    return df_numerico


def generar_grafico_matplotlib(x_vals, y_vals, col_x="X", col_y="Y", color_scheme=None, theme="dark"):
    if color_scheme is None:
        color_scheme = {"point": "#ff6b6b", "line": "#339af0"}

    df_par = pd.DataFrame({"X": x_vals, "Y": y_vals}).dropna()
    if len(df_par) < 2:
        return None

    cov_muestral = float(df_par["X"].cov(df_par["Y"]))
    r_pearson = float(df_par["X"].corr(df_par["Y"]))

    # np.polyfit con grado 1 calcula la pendiente m y la ordenada b para y = mx + b
    m, b = np.polyfit(df_par["X"], df_par["Y"], 1)

    is_dark = (theme == "dark")
    bg_fig = "#0a111d" if is_dark else "#ffffff"
    bg_ax = "#112340" if is_dark else "#edf2fe"
    text_color = "#eeeeef" if is_dark else "#14171f"
    subtext_color = "#b4b3b7" if is_dark else "#595b66"
    border_color = "#27487d" if is_dark else "#cdced7"

    fig, ax = plt.subplots(figsize=(7.5, 4.8), facecolor=bg_fig)
    ax.set_facecolor(bg_ax)

    pt_color = color_scheme.get("point", "#ff6b6b")
    ln_color = color_scheme.get("line", "#339af0")

    ax.scatter(df_par["X"], df_par["Y"], color=pt_color, edgecolors="#ffffff" if is_dark else "#14171f", s=70, alpha=0.9, zorder=3, label=f"Muestras ({col_x}, {col_y})")

    x_linea = np.linspace(df_par["X"].min(), df_par["X"].max(), 100)
    y_linea = m * x_linea + b
    ax.plot(x_linea, y_linea, color=ln_color, linestyle="--", linewidth=2.2, label=f"y = {m:.4f}x + {b:.4f}")

    ax.set_title(f"{col_x} vs {col_y}\nCov = {cov_muestral:.4f} | r = {r_pearson:.4f}", color=text_color, fontsize=11, pad=12)
    ax.set_xlabel(col_x, color=subtext_color, labelpad=8)
    ax.set_ylabel(col_y, color=subtext_color, labelpad=8)
    ax.tick_params(colors=subtext_color)
    for spine in ax.spines.values():
        spine.set_color(border_color)
    ax.grid(True, linestyle=":", alpha=0.5, color=border_color)
    ax.legend(facecolor=bg_fig, edgecolor=border_color, labelcolor=text_color, fontsize=9)
    fig.tight_layout()

    buffer = io.BytesIO()
    fig.savefig(buffer, format="png", dpi=130, facecolor=fig.get_facecolor(), edgecolor="none")
    plt.close(fig)
    buffer.seek(0)
    imagen_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")

    return {
        "pair_name": f"{col_x} vs {col_y}",
        "image_base64": f"data:image/png;base64,{imagen_base64}",
        "points": [{"x": float(row["X"]), "y": float(row["Y"])} for _, row in df_par.iterrows()],
        "trend_line": [
            {"x": float(df_par["X"].min()), "y": float(m * df_par["X"].min() + b)},
            {"x": float(df_par["X"].max()), "y": float(m * df_par["X"].max() + b)}
        ],
        "cov": cov_muestral,
        "r": r_pearson,
        "equation": f"y = {m:.4f}x + {b:.4f}",
        "col_x": col_x,
        "col_y": col_y,
        "colors": color_scheme
    }


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/process", methods=["POST"])
def process():
    analysis_type = request.form.get("analysis_type")
    metricas = request.form.getlist("metrics")
    if not metricas:
        metricas = ["all"]
        
    theme = "dark"
    df_numerico = None

    if "file" in request.files:
        archivo = request.files["file"]
        if not archivo.filename:
            return jsonify({"success": False, "error": "No se seleccionó ningún archivo."}), 400

        # errors="ignore" omite bytes corruptos sin generar excepción UnicodeDecodeError
        contenido = archivo.read().decode("utf-8", errors="ignore")
        theme = request.form.get("theme", "dark")
        df_numerico = parse_tabular_data(contenido, archivo.filename)
    else:
        body = request.get_json(silent=True)
        if not body:
            body = {}
            
        analysis_type = body.get("analysis_type", analysis_type)
        if not analysis_type:
            analysis_type = "descriptive"
            
        metricas = body.get("metrics", ["all"])
        theme = body.get("theme", "dark")

        if "table_matrix" in body:
            matrix = body.get("table_matrix", [])
            headers = body.get("headers", [])
            if matrix:
                df_numerico = pd.DataFrame(matrix, columns=headers if headers else None)
                df_numerico = df_numerico.apply(pd.to_numeric, errors="coerce").dropna()
        elif "raw_text" in body:
            df_numerico = parse_tabular_data(body.get("raw_text", ""))

    if df_numerico is None or df_numerico.empty:
        return jsonify({"success": False, "error": "No se encontraron datos numéricos procesables."}), 400

    # Rama 1: Análisis de Covarianza Multivariada
    if analysis_type == "covariance":
        df_cov = df_numerico.dropna()
        if df_cov.shape[1] < 2:
            return jsonify({
                "success": False,
                "error": f"Para la Matriz de Covarianza se requieren al menos 2 variables numéricas. El conjunto tiene {df_cov.shape[1]} variable(s)."
            }), 400

        if len(df_cov) < 2:
            return jsonify({
                "success": False,
                "error": "Se requieren al menos 2 observaciones para calcular la covarianza."
            }), 400

        # rowvar=False indica que las columnas representan las variables; ddof=1 aplica n - 1[cite: 51, 52]
        cov_matrix = np.cov(df_cov.values, rowvar=False, ddof=1)
        if cov_matrix.ndim == 0:
            cov_matrix = np.array([[float(cov_matrix)]])

        cov_payload = {
            "columns": list(df_cov.columns),
            "matrix": [[float(v) for v in row] for row in cov_matrix]
        }

        columnas = list(df_cov.columns)
        pares_combinaciones = list(combinations(columnas, 2))

        # Paletas de color coordinadas con las diapositivas de clase[cite: 55, 56]
        paletas = [
            {"point": "#ff6b6b", "line": "#339af0"},  # Par 1: Puntos rojos / Recta azul[cite: 55]
            {"point": "#339af0", "line": "#ff6b6b"},  # Par 2: Puntos azules / Recta roja[cite: 55]
            {"point": "#20c997", "line": "#e64980"},  # Par 3: Puntos verdes / Recta rosa[cite: 56]
            {"point": "#fcc419", "line": "#845ef7"},
            {"point": "#ff922b", "line": "#22b8cf"},
            {"point": "#94d82d", "line": "#d6336c"}
        ]

        bivariate_pairs = []
        for idx, (col_x, col_y) in enumerate(pares_combinaciones):
            color_sel = paletas[idx % len(paletas)]
            grafico_par = generar_grafico_matplotlib(df_cov[col_x], df_cov[col_y], col_x, col_y, color_sel, theme)
            if grafico_par:
                bivariate_pairs.append(grafico_par)

        return jsonify({
            "success": True,
            "analysis_type": "covariance",
            "covariance": cov_payload,
            "bivariate_pairs": bivariate_pairs
        })

    # Rama 2: Estadística Descriptiva Univariada
    else:
        columnas_analizadas = {}
        for col in df_numerico.columns:
            serie_col = df_numerico[col].dropna()
            if not serie_col.empty:
                analisis = calcular_metricas_vector(serie_col.values, metricas)
                if analisis:
                    columnas_analizadas[col] = analisis

        return jsonify({
            "success": True,
            "analysis_type": "descriptive",
            "columns": list(columnas_analizadas.keys()),
            "data": columnas_analizadas
        })


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)