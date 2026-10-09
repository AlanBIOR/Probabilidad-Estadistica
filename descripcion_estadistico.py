import io
import os
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# Si presentas el error de Tkinter en Laragon, descomenta estas dos líneas:
# os.environ['TCL_LIBRARY'] = r'C:\laragon\bin\python\python-3.13\tcl\tcl8.6'
# os.environ['TK_LIBRARY'] = r'C:\laragon\bin\python\python-3.13\tcl\tk8.6'


def leer_desde_consola():
    """Captura dos listas de valores independientes escritas en línea."""
    print("\n--- Entrada manual ---")
    raw_x = input("Valores de X (separados por espacio o coma): ").strip()
    raw_y = input("Valores de Y (separados por espacio o coma): ").strip()

    x = [float(v) for v in raw_x.replace(",", " ").split()]
    y = [float(v) for v in raw_y.replace(",", " ").split()]

    if len(x) != len(y):
        raise ValueError(
            f"Las listas deben tener el mismo tamaño (X tiene {len(x)}, Y tiene {len(y)})."
        )

    return pd.Series(x, name="X"), pd.Series(y, name="Y")


def leer_desde_texto_plano():
    """Captura datos pegados en bloque renglón por renglón."""
    print("\n--- Pegar texto plano ---")
    print(
        "Pega las columnas de datos y presiona [Enter] en una línea vacía al terminar:"
    )

    lineas = []
    while True:
        linea = input()
        if not linea.strip():
            break
        lineas.append(linea.strip())

    if not lineas:
        raise ValueError("No se ingresaron datos.")

    bloque = "\n".join(lineas)
    df = pd.read_csv(
        io.StringIO(bloque), sep=r"[\s,]+", engine="python", header=None
    )

    # Si la primera fila contiene texto (encabezados pegados por error), la descarta
    df = df.apply(pd.to_numeric, errors="coerce").dropna()

    if df.shape[1] < 2:
        raise ValueError("Se necesitan al menos 2 columnas para el análisis.")

    return df.iloc[:, 0], df.iloc[:, 1]


def leer_desde_archivo():
    """Carga un archivo CSV o TXT delimitado."""
    print("\n--- Cargar archivo (.csv / .txt) ---")
    ruta = input("Ruta o nombre del archivo: ").strip().strip('"').strip("'")

    if not os.path.exists(ruta):
        raise FileNotFoundError(f"No se encontró el archivo: '{ruta}'")

    # Infiere automáticamente si está separado por comas, espacios o tabuladores
    df = pd.read_csv(ruta, sep=None, engine="python")

    # Convierte todo a numérico y elimina filas inválidas
    df_num = df.apply(pd.to_numeric, errors="coerce").dropna()

    columnas = list(df.columns)
    print(f"\nColumnas disponibles: {columnas}")

    if len(columnas) == 2:
        col_x, col_y = columnas[0], columnas[1]
    else:
        col_x = input(f"Selecciona columna X [{columnas[0]}]: ").strip()
        if not col_x or col_x not in df.columns:
            col_x = columnas[0]

        col_y = input(f"Selecciona columna Y [{columnas[1]}]: ").strip()
        if not col_y or col_y not in df.columns:
            col_y = columnas[1]

    return df_num[col_x], df_num[col_y]


def procesar_y_graficar(x, y):
    """Calcula estadísticos descriptivos, covarianza, correlación y genera la gráfica."""
    df = pd.DataFrame({"X": x, "Y": y}).dropna()

    if len(df) < 2:
        print("\n[!] Error: Se requieren al menos 2 pares de datos válidos.")
        return

    n = len(df)
    media_x, media_y = df["X"].mean(), df["Y"].mean()
    cov_muestral = df["X"].cov(df["Y"])  # Divide entre N - 1
    r = df["X"].corr(df["Y"])

    print("\n" + "=" * 50)
    print("             RESUMEN ESTADÍSTICO")
    print("=" * 50)
    print(f"Número de observaciones (n):  {n}")
    print(f"Media de X:                   {media_x:.4f}")
    print(f"Media de Y:                   {media_y:.4f}")
    print(f"Varianza de X (s²):           {df['X'].var():.4f}")
    print(f"Varianza de Y (s²):           {df['Y'].var():.4f}")
    print("-" * 50)
    print(f"Covarianza muestral (Cov):    {cov_muestral:.4f}")
    print(f"Correlación de Pearson (r):   {r:.4f}")
    print("=" * 50)

    # Gráfica
    plt.figure(figsize=(7, 5))
    plt.scatter(
        df["X"],
        df["Y"],
        color="hotpink",
        edgecolor="black",
        s=65,
        zorder=3,
        label="Datos",
    )

    # Recta de tendencia / regresión
    m, b = np.polyfit(df["X"], df["Y"], 1)
    x_vals = np.linspace(df["X"].min(), df["X"].max(), 100)
    plt.plot(
        x_vals,
        m * x_vals + b,
        color="crimson",
        linestyle="--",
        label=f"Tendencia: y = {m:.2f}x + {b:.2f}",
    )

    plt.title(
        f"Diagrama de Dispersión\nCov = {cov_muestral:.2f} | r = {r:.4f}",
        fontsize=11,
    )
    plt.xlabel(df["X"].name if df["X"].name else "Variable X")
    plt.ylabel(df["Y"].name if df["Y"].name else "Variable Y")
    plt.grid(True, linestyle=":", alpha=0.6)
    plt.legend()
    plt.tight_layout()
    plt.show()


def menu():
    while True:
        print("\n" + "=" * 40)
        print("    ANÁLISIS ESTADÍSTICO BIVARIADO    ")
        print("=" * 40)
        print("1. Entrada manual (listas X e Y)")
        print("2. Pegar bloque de texto plano")
        print("3. Cargar archivo (.csv / .txt)")
        print("4. Salir")

        opcion = input("\nElige una opción (1-4): ").strip()

        if opcion == "4":
            print("\nFinalizando programa...")
            break

        try:
            if opcion == "1":
                x, y = leer_desde_consola()
            elif opcion == "2":
                x, y = leer_desde_texto_plano()
            elif opcion == "3":
                x, y = leer_desde_archivo()
            else:
                print("\n[!] Opción no válida. Intenta de nuevo.")
                continue

            procesar_y_graficar(x, y)

        except Exception as error:
            print(f"\n[!] Error: {error}")


if __name__ == "__main__":
    menu()