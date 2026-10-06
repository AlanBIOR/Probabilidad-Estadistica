# Data Analytics Studio: Medidas de Centralidad y Variabilidad

Plataforma web analítica desarrollada con **Flask**, **Pandas**, **NumPy** y **JavaScript (ES Modules)** para el cálculo, inspección multivariable y modelado gráfico de medidas estadísticas descriptivas a partir de entradas manuales o archivos de datos (`.csv` y `.txt`).

---

## Características Principales

- **Procesamiento Multivariable en Lote:** Filtra automáticamente columnas no numéricas en datasets tabulares (como `iris.csv`), calculando todas las métricas en una sola petición y generando una tabla resumen comparativa.
- **Entrada Flexible de Datos:**
  - **Modo Manual:** Generación dinámica de $N$ celdas de captura con validación numérica estricta en el cliente.
  - **Modo Archivo:** Soporte Drag & Drop para archivos delimitados (`.csv`) o texto plano (`.txt`).
- **Métricas a la Carta:** Selector interactivo para computar la totalidad de las medidas o un subconjunto específico.
- **Visualización de Distribución y Sesgo:**
  - Histograma interactivo con **Chart.js** donde se resalta la barra correspondiente a la Media Aritmética.
  - Curva de densidad estimada superpuesta.
  - Clasificación automatizada del sesgo: **Simétrico**, **Sesgo positivo (a la derecha: $\bar{X} > Me$)** o **Sesgo negativo (a la izquierda: $\bar{X} < Me$)**.
- **Arquitectura Modular:**
  - Estructura CSS basada en el patrón **Sass 7-1** compilada con Dart Sass.
  - Frontend desacoplado con **ES Modules** nativos sin necesidad de bundlers adicionales.
- **Modo Oscuro / Claro:** Paleta de colores persistente adaptada para visualización técnica con tokens CSS.

---

## Fundamentos Matemáticos y Control de Errores

| Métrica | Definición Matemática | Consideraciones Numéricas |
| :--- | :--- | :--- |
| **Media Aritmética ($\bar{X}$)** | $\bar{X} = \frac{1}{n} \sum_{i=1}^{n} x_i$ | Cálculo vectorial directo con NumPy. |
| **Media Armónica ($H$)** | $H = \frac{n}{\sum_{i=1}^{n} \frac{1}{x_i}}$ | Validación de indeterminación por división entre cero ($x_i = 0$) y advertencia ante valores negativos. |
| **Media Geométrica ($G$)** | $G = \exp\left(\frac{1}{n} \sum_{i=1}^{n} \ln(x_i)\right)$ | Implementación logarítmica numéricamente estable para prevenir desbordamiento aritmético (*overflow*). Restringida a $x_i > 0$. |
| **Moda ($Mo$)** | Valor(es) con mayor frecuencia absoluta | Manejo dinámico para distribuciones unimodales, multimodales o amodales. |
| **Cuartiles & IQR** | $Q_1 (25\%),\ Q_2 (50\%),\ Q_3 (75\%)$<br>$IQR = Q_3 - Q_1$ | Cálculo por percentiles de NumPy con determinación de dispersión intercuartílica. |

---

## Estructura del Repositorio

```text
probabilidad_y_estadistica/
├── db/                                # Datasets de prueba (.csv)
│   ├── generacion_liquidada_ago.csv
│   └── iris.csv
├── static/
│   ├── css/
│   │   └── style.css                  # Hoja de estilos compilada
│   ├── js/
│   │   ├── modules/
│   │   │   ├── api.js                 # Peticiones Fetch asíncronas
│   │   │   ├── chartManager.js        # Configuración y temas de Chart.js
│   │   │   ├── dataInput.js           # Captura manual y Drag & Drop
│   │   │   ├── metrics.js             # Gestión del checklist de cálculo
│   │   │   ├── modal.js               # Control de ventanas <dialog>
│   │   │   ├── render.js              # Inyección de tarjetas y tablas DOM
│   │   │   ├── tabs.js                # Alternancia de pestañas
│   │   │   └── theme.js               # Toggle Dark/Light Mode
│   │   └── main.js                    # Orquestador principal de la UI
│   └── sass/                          # Arquitectura Sass 7-1
│       ├── abstracts/                 # _variables.scss, _mixins.scss, etc.
│       ├── base/                      # _reset.scss, _typography.scss
│       ├── components/                # _buttons.scss, _cards.scss, _modal.scss
│       ├── layout/                    # _header.scss, _footer.scss, _forms.scss, _grid.scss
│       ├── themes/                    # _default.scss (CSS Custom Properties)
│       └── style.scss                 # Manifiesto central
├── templates/
│   └── index.html                     # Plantilla base semántica (HTML5)
├── app.py                             # API REST y servidor web Flask
├── requirements.txt                   # Dependencias de Python
└── README.md 
```

## Instalación y Despliegue Local
1. Clonar el repositorio y configurar el entorno virtual

git clone [https://github.com/AlanBIOR/Probabilidad-Estadistica](https://github.com/AlanBIOR/Probabilidad-Estadistica)
cd probabilidad_y_estadistica

# Crear y activar entorno virtual
python -m venv venv

# En Windows:
venv\Scripts\activate
# En Linux/macOS:
source venv/bin/activate

2. Instalar dependencias de Python
pip install -r requirements.txt

3. Compilación de estilos Sass
Si deseas modificar los archivos Sass, ejecuta el observador de Dart Sass:
sass --watch static/sass/style.scss static/css/style.css

4. Ejecución del servidor de desarrollo
python app.py

bre tu navegador en http://127.0.0.1:5000/.

Tecnologías Utilizadas
Backend: Python 3, Flask, Pandas, NumPy.

Frontend: HTML5 semántico, Sass (Dart Sass), Vanilla JavaScript (ES Modules).

Visualización: Chart.js.

Autor
Alan Alfonso Rodríguez Ibarra

Programa de Maestría en Sistemas Computacionales / Electrónica & Automatización