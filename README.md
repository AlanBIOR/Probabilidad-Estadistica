# Data Analytics Studio: Medidas de Centralidad, Variabilidad y Covarianza

Plataforma web analítica desarrollada con **Flask**, **Pandas**, **NumPy**, **Matplotlib** y **JavaScript (ES Modules)** para el análisis estadístico descriptivo univariado (medidas de centralidad y dispersión) y multivariado (matriz de covarianza, correlación de Pearson y regresión lineal bivariada) a partir de entradas manuales en tabla editable o archivos tabulares (`.csv` y `.txt`).

---

## 🚀 Características Principales

- **Bifurcación Estricta de Análisis:**
  - **Estadística Descriptiva Univariada:** Medidas de tendencia central (media aritmética, armónica, geométrica, moda inteligente), medidas de dispersión/posición (cuartiles, rango intercuartílico, varianza muestral/poblacional, desviación estándar muestral/poblacional), diagnóstico de asimetría y ajuste a curva normal teórica.
  - **Matriz de Covarianza Multivariada:** Cálculo de la matriz completa de dispersión conjunta $k \times k$ ($n - 1$ grados de libertad) para conjuntos de 2 o más variables[cite: 48, 49].
- **Procesamiento de Datos Heterogéneos:**
  - Filtra y extrae automáticamente columnas numéricas en datasets mixtos (como `iris.csv`), descartando columnas de texto/etiquetas sin interrumpir el procesamiento.
  - Limpieza automática de comillas dobles escapadas en exportaciones complejas (como `generacion_liquidada_ago.csv`).
  - Reconocimiento de texto plano delimitado por espacios, comas o tabuladores sin necesidad de encabezados previos (como `datos_x_y_z.txt` y `estadistica_des.txt`).
- **Entrada Flexible de Datos:**
  - **Modo Archivo:** Carga por Drag & Drop para archivos delimitados (`.csv` y `.txt`).
  - **Modo Manual en Tabla:** Constructor dinámico de hojas de cálculo editables en pantalla con dimensiones personalizables de filas y columnas, además de soporte para pegado rápido de bloques de texto.
- **Visor Bivariado 1 a 1 de Alta Resolución:**
  - Cálculo simultáneo de todas las combinaciones bivariadas $\binom{k}{2}$.
  - Selector desplegable y botones de navegación ($Ant$ / $Sig$) para explorar pares individuales sin sobrecargar la interfaz gráfica.
  - Modalidad dual: vista interactiva con **Chart.js** (inspección de coordenadas exactas en hover) y renderizado estático de alta fidelidad exportado directamente desde **Matplotlib** en Base64.
  - Asignación de paletas cromáticas diferenciadas por par para una interpretación visual inmediata[cite: 51, 52].
- **Persistencia de Sesión (`localStorage`):** Almacenamiento local optimizado para restaurar el estado y las métricas calculadas tras recargas de página o cambios de tema.
- **Diseño Editorial & Accesibilidad:**
  - Arquitectura CSS basada en la metodología **Sass 7-1** compilada con Dart Sass.
  - Modo Oscuro y Modo Claro con variables CSS adaptativas y alto contraste en tipografía, ejes y gráficos.
  - Modal flotante (`<dialog>`) para parametrización selectiva de métricas.

---

## 📐 Fundamentos Matemáticos y Control de Errores

| Métrica / Parámetro | Formulación Matemática | Implementación y Validación Numérica |
| :--- | :--- | :--- |
| **Media Aritmética ($\bar{X}$)** | $\bar{X} = \frac{1}{n} \sum_{i=1}^{n} x_i$[cite: 20] | Vectorizada directamente con `np.mean()`. |
| **Media Armónica ($H$)** | $H = \frac{n}{\sum_{i=1}^{n} \frac{1}{x_i}}$[cite: 21] | Validación estricta de indeterminación por cero ($x_i = 0$) y advertencia ante valores negativos. |
| **Media Geométrica ($G$)** | $G = \exp\left(\frac{1}{n} \sum_{i=1}^{n} \ln(x_i)\right)$[cite: 22] | Implementación logarítmica numéricamente estable contra desbordamiento (*overflow*). Restringida a $x_i > 0$. |
| **Moda Inteligente ($Mo$)** | Discreta o Intervalo modal agrupado: $L + \left(\frac{\Delta_1}{\Delta_1 + \Delta_2}\right)h$[cite: 23] | Detección de frecuencias repetidas o aproximación por histograma de clases cuando todas las muestras son únicas. |
| **Cuartiles & IQR** | $Q_k = \text{pos}\left(\frac{k(n+1)}{4}\right)$<br>$IQR = Q_3 - Q_1$[cite: 28, 29] | Interpolación lineal exacta entre posiciones ordinales y rango intercuartílico. |
| **Varianza Muestral ($s^2$)** | $s^2 = \frac{\sum (x_i - \bar{X})^2}{n - 1}$[cite: 30, 32] | Computada con `np.var(valores, ddof=1)` (corrección de Bessel con $n - 1$ grados de libertad). |
| **Varianza Poblacional ($\sigma^2$)** | $\sigma^2 = \frac{\sum (x_i - \mu)^2}{N}$[cite: 30, 31] | Computada con `np.var(valores, ddof=0)` con divisor poblacional $N$. |
| **Desviación Estándar Muestral ($s$)** | $s = \sqrt{s^2}$[cite: 33, 35] | Raíz cuadrada de la varianza muestral calculada mediante `np.std(valores, ddof=1)`. |
| **Desviación Estándar Poblacional ($\sigma$)** | $\sigma = \sqrt{\sigma^2}$[cite: 33, 34] | Raíz cuadrada de la varianza poblacional calculada mediante `np.std(valores, ddof=0)`. |
| **Covarianza Muestral ($Cov(X, Y)$)** | $Cov(X, Y) = \frac{\sum (x_i - \bar{X})(y_i - \bar{Y})}{n - 1}$[cite: 46, 47] | Medida de la dirección y variación lineal conjunta entre dos variables con divisor $n - 1$[cite: 44, 46]. |
| **Matriz de Covarianza** | Matriz simétrica $k \times k$[cite: 48, 49] | Diagonal principal: varianzas individuales ($s^2$); componentes no diagonales: covarianzas cruzadas calculadas con `np.cov(rowvar=False, ddof=1)`[cite: 48, 49]. |
| **Correlación de Pearson ($r$)** | $r = \frac{Cov(X, Y)}{s_X s_Y}$[cite: 56, 57] | Coeficiente adimensional estandarizado en el rango $[-1, 1]$ obtenido con `df.corr()`. |
| **Recta de Regresión** | $y = mx + b$[cite: 57] | Ajuste de mínimos cuadrados lineales de primer orden mediante `np.polyfit(x, y, 1)`. |

---

## 📁 Estructura del Repositorio

```text
probabilidad_y_estadistica/
├── db/                                # Conjuntos de datos de prueba
│   ├── datos_x_y_z.txt                # Dataset multivariable (X, Y, Z)
│   ├── estadistica_des.txt            # Dataset bivariado (X, Y)
│   ├── generacion_liquidada_ago.csv   # Dataset temporal multivariable
│   └── iris.csv                       # Dataset canónico multivariable mixto
├── static/
│   ├── css/
│   │   └── style.css                  # Hoja de estilos compilada
│   ├── js/
│   │   ├── modules/
│   │   │   ├── api.js                 # Peticiones Fetch asíncronas a la API Flask
│   │   │   ├── chartManager.js        # Configuración de temas e histograma Chart.js
│   │   │   ├── dataInput.js           # Drag & Drop, tabla editable y selectores
│   │   │   ├── metrics.js             # Modal y checklist de métricas
│   │   │   ├── modal.js               # Control de ventanas modales <dialog>
│   │   │   ├── render.js              # Inyección DOM: tablas, tarjetas y visor bivariado
│   │   │   ├── storage.js             # Persistencia local con localStorage
│   │   │   ├── tabs.js                # Control de vistas y navegación del sidebar
│   │   │   └── theme.js               # Toggle Dark/Light Mode
│   │   └── main.js                    # Orquestador principal de eventos del cliente
│   └── sass/                          # Arquitectura Sass 7-1
│       ├── abstracts/                 # _variables.scss, _mixins.scss, _functions.scss
│       ├── base/                      # _reset.scss, _typography.scss, _base.scss
│       ├── components/                # _buttons.scss, _cards.scss, _modal.scss
│       ├── layout/                    # _header.scss, _footer.scss, _forms.scss, _sidebar.scss
│       ├── themes/                    # _default.scss (tokens de variables CSS)
│       └── style.scss                 # Manifiesto central
├── templates/
│   ├── layouts/
│   │   └── base.html                  # Esqueleto HTML5 y carga de recursos
│   ├── partials/
│   │   ├── _footer.html               # Pie de página técnico y metadatos
│   │   ├── _header.html               # Encabezado, badge y conmutador de tema
│   │   ├── _modal.html                # Modal de alerta de errores
│   │   └── _navbar.html               # Barra lateral de módulos de navegación
│   └── index.html                     # Plantilla unificada de dashboards y vistas
├── app.py                             # API REST y servidor web Flask (NumPy/Pandas/Matplotlib)
├── requirements.txt                   # Dependencias de Python del proyecto
└── README.md                          # Documentación técnica
```

## 🚀 Instalación y Despliegue Local

### 1. Clonar el repositorio y configurar el entorno virtual

```bash
git clone [https://github.com/AlanBIOR/Probabilidad-Estadistica.git](https://github.com/AlanBIOR/Probabilidad-Estadistica.git)
cd probabilidad_y_estadistica

# Crear entorno virtual
python -m venv venv

# Activar en Windows:
venv\Scripts\activate

# Activar en Linux/macOS:
source venv/bin/activate
```

### 2. Instalar dependencias de Python

```bash
pip install -r requirements.txt
```

### 3. Compilación de estilos Sass

Si deseas modificar los archivos Sass, ejecuta el observador de Dart Sass:

```bash
sass --watch static/sass/style.scss static/css/style.css
```

### 4. Ejecución del servidor de desarrollo

```bash
python app.py
```

Abre tu navegador en: [http://127.0.0.1:5000/](http://127.0.0.1:5000/)

---

## 🛠️ Tecnologías Utilizadas

- **Backend:** Python 3, Flask, NumPy, Pandas, Matplotlib (Agg headless).
- **Frontend:** HTML5 semántico (Jinja2 Templates), Sass (Dart Sass), Vanilla JavaScript (ES Modules), Web Storage API (localStorage).
- **Visualización:** Chart.js, Matplotlib.

---

## 👤 Autor

- **Alan Alfonso Rodríguez Ibarra**
  - *Ingeniería Electrónica en Control y Automatización Industrial*
  - *Maestría en Sistemas Computacionales / Inteligencia Artificial*