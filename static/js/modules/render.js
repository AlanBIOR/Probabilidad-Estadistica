/**
 * Módulo: render.js
 * Tablas univariadas, tarjetas KPI, matriz de covarianza
 * y diagrama de dispersión bivariado interactivo con soporte de temas.
 */

let scatterChartInstance = null;
let lastBivariatePayload = null;

const formatVal = (v) => {
  if (v === null || v === undefined || isNaN(v)) return "--";
  return Number(v).toFixed(4);
};

export function renderSummaryTable(allData) {
  const tableSection = document.getElementById("summarySection");
  const tbody = document.querySelector("#summaryTable tbody");
  if (!tbody || !tableSection) return;

  tbody.innerHTML = "";
  const cols = Object.keys(allData);

  if (cols.length <= 1 && cols[0] === "Entrada Manual") {
    tableSection.classList.add("panel--hidden");
    tableSection.dataset.hasData = "false";
    return;
  }

  cols.forEach((colName) => {
    const res = allData[colName].results;
    const n = allData[colName].chart.n;
    const tr = document.createElement("tr");

    tr.innerHTML = `
      <td><strong>${colName}</strong></td>
      <td>${n}</td>
      <td>${formatVal(res.mean)}</td>
      <td>${formatVal(res.quartiles?.q2)}</td>
      <td>${formatVal(res.sample_variance)}</td>
      <td>${formatVal(res.sample_std)}</td>
      <td>${formatVal(res.quartiles?.iqr)}</td>
    `;
    tbody.appendChild(tr);
  });

  tableSection.classList.remove("panel--hidden");
  tableSection.dataset.hasData = "true";
}

export function renderColumnPills(columns, activeCol, onSelectCol) {
  const container = document.getElementById("columnPills");
  if (!container) return;
  container.innerHTML = "";

  if (columns.length <= 1) {
    container.classList.add("panel--hidden");
    return;
  }

  container.classList.remove("panel--hidden");
  columns.forEach((col) => {
    const btn = document.createElement("button");
    btn.className = `tabs__btn ${col === activeCol ? "tabs__btn--active" : ""}`;
    btn.textContent = col;
    btn.type = "button";
    btn.addEventListener("click", () => onSelectCol(col));
    container.appendChild(btn);
  });
}

export function renderColumnCards(columnPayload, container) {
  if (!container) return;
  container.innerHTML = "";
  const { results, warnings, chart } = columnPayload;

  // 1. Diagnóstico de Sesgo
  const skewCard = document.createElement("div");
  skewCard.className = "metric-card";
  skewCard.style.borderLeft = "4px solid var(--primary-hover)";
  skewCard.innerHTML = `
    <span class="metric-card__title">Distribución y Asimetría</span>
    <span class="metric-card__val" style="font-size: 1.1rem;">${chart.skewness}</span>
    <span class="metric-card__warn" style="color: var(--primary-hover);">Muestras: N = ${chart.n}</span>
  `;
  container.appendChild(skewCard);

  // 2. Centralidad
  if ("mean" in results) container.appendChild(createCard("Media Aritmética (X̄)", formatVal(results.mean)));
  if ("harmonic" in results) container.appendChild(createCard("Media Armónica (H)", formatVal(results.harmonic), warnings.harmonic));
  if ("geometric" in results) container.appendChild(createCard("Media Geométrica (G)", formatVal(results.geometric), warnings.geometric));
  
  if ("mode" in results) {
    const modas = results.mode;
    const val = modas && modas.length ? modas.map((m) => Number(m).toFixed(2)).join(", ") : "Amodal";
    container.appendChild(createCard("Moda", val, warnings.mode));
  }
  
  if ("quartiles" in results) {
    const q = results.quartiles;
    container.appendChild(createCard("Mediana / Q2", formatVal(q.q2)));
    container.appendChild(createCard("Rango Intercuartílico (IQR)", formatVal(q.iqr), `Q1: ${q.q1.toFixed(2)} | Q3: ${q.q3.toFixed(2)}`));
  }

  // 3. Dispersión
  if ("sample_variance" in results) container.appendChild(createCard("Varianza Muestral (s²)", formatVal(results.sample_variance)));
  if ("population_variance" in results) container.appendChild(createCard("Varianza Poblacional (σ²)", formatVal(results.population_variance)));
  if ("sample_std" in results) container.appendChild(createCard("Desv. Estándar Muestral (s)", formatVal(results.sample_std)));
  if ("population_std" in results) container.appendChild(createCard("Desv. Estándar Poblac. (σ)", formatVal(results.population_std)));
}

export function renderCovarianceMatrix(covPayload) {
  const emptyMsg = document.getElementById("covMatrixEmpty");
  const wrapper = document.getElementById("covMatrixWrapper");
  const thead = document.querySelector("#covMatrixTable thead");
  const tbody = document.querySelector("#covMatrixTable tbody");

  if (!covPayload || !covPayload.columns || covPayload.columns.length < 2) {
    if (emptyMsg) emptyMsg.classList.remove("panel--hidden");
    if (wrapper) wrapper.classList.add("panel--hidden");
    return;
  }

  if (emptyMsg) emptyMsg.classList.add("panel--hidden");
  if (wrapper) {
    wrapper.classList.remove("panel--hidden");
    wrapper.dataset.hasData = "true";
  }

  const { columns, matrix } = covPayload;

  let headHtml = "<tr><th>Variables</th>";
  columns.forEach((col) => {
    headHtml += `<th>${col}</th>`;
  });
  headHtml += "</tr>";
  thead.innerHTML = headHtml;

  let bodyHtml = "";
  matrix.forEach((fila, i) => {
    bodyHtml += `<tr><td><strong>${columns[i]}</strong></td>`;
    fila.forEach((val, j) => {
      const isDiagonal = i === j;
      const estilo = isDiagonal ? "style='color: var(--primary-hover); font-weight: 700;'" : "";
      bodyHtml += `<td ${estilo}>${Number(val).toFixed(4)}</td>`;
    });
    bodyHtml += "</tr>";
  });
  tbody.innerHTML = bodyHtml;
}

export function renderBivariateScatter(bivariatePayload) {
  lastBivariatePayload = bivariatePayload;

  const panel = document.getElementById("scatterPanel");
  const statsText = document.getElementById("scatterStatsText");
  const imgElement = document.getElementById("pltScatterImg");
  const canvas = document.getElementById("interactiveScatterChart");

  const btnInteractive = document.getElementById("btnShowInteractiveScatter");
  const btnPlt = document.getElementById("btnShowPltImage");
  const contInteractive = document.getElementById("interactiveScatterContainer");
  const contPlt = document.getElementById("pltImageContainer");

  if (!bivariatePayload || !panel) {
    if (panel) panel.classList.add("panel--hidden");
    return;
  }

  panel.classList.remove("panel--hidden");
  if (statsText) {
    statsText.textContent = `Cov = ${bivariatePayload.cov.toFixed(4)} | r (Pearson) = ${bivariatePayload.r.toFixed(4)} | Tendencia: ${bivariatePayload.equation}`;
  }
  if (imgElement) {
    imgElement.src = bivariatePayload.image_base64;
  }

  if (btnInteractive && btnPlt && contInteractive && contPlt) {
    btnInteractive.onclick = () => {
      btnInteractive.classList.add("tabs__btn--active");
      btnPlt.classList.remove("tabs__btn--active");
      contInteractive.classList.remove("panel--hidden");
      contPlt.classList.add("panel--hidden");
    };

    btnPlt.onclick = () => {
      btnPlt.classList.add("tabs__btn--active");
      btnInteractive.classList.remove("tabs__btn--active");
      contPlt.classList.remove("panel--hidden");
      contInteractive.classList.add("panel--hidden");
    };
  }

  if (!canvas) return;
  if (scatterChartInstance) scatterChartInstance.destroy();

  // Detección estricta del tema actual
  const isDark = (document.documentElement.getAttribute("data-theme") || "dark") === "dark";
  const textColor = isDark ? "#ffffff" : "#1e1f24";
  const gridColor = isDark ? "rgba(39, 72, 125, 0.45)" : "rgba(205, 206, 215, 0.6)";

  scatterChartInstance = new Chart(canvas, {
    type: "scatter",
    data: {
      datasets: [
        {
          label: "Observaciones (x, y)",
          data: bivariatePayload.points,
          backgroundColor: "#8cb7fc",
          borderColor: isDark ? "#ffffff" : "#3b66ac",
          borderWidth: 1.2,
          pointRadius: 6,
          pointHoverRadius: 9
        },
        {
          label: `Línea de tendencia (${bivariatePayload.equation})`,
          data: bivariatePayload.trend_line,
          type: "line",
          borderColor: "#ff6b6b",
          borderWidth: 2,
          borderDash: [6, 6],
          pointRadius: 0,
          fill: false
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        tooltip: {
          callbacks: {
            label: (ctx) => `(${bivariatePayload.col_x}: ${ctx.parsed.x.toFixed(2)}, ${bivariatePayload.col_y}: ${ctx.parsed.y.toFixed(2)})`
          }
        },
        legend: {
          labels: {
            color: textColor,
            font: { size: 12, weight: "bold" }
          }
        }
      },
      scales: {
        x: {
          title: {
            display: true,
            text: bivariatePayload.col_x,
            color: textColor,
            font: { size: 12, weight: "bold" }
          },
          ticks: {
            color: textColor,
            font: { size: 11, weight: "600" }
          },
          grid: { color: gridColor }
        },
        y: {
          title: {
            display: true,
            text: bivariatePayload.col_y,
            color: textColor,
            font: { size: 12, weight: "bold" }
          },
          ticks: {
            color: textColor,
            font: { size: 11, weight: "600" }
          },
          grid: { color: gridColor }
        }
      }
    }
  });
}

/**
 * Actualiza los colores del gráfico de dispersión cuando cambia el tema
 */
export function updateScatterTheme(isDark) {
  if (!scatterChartInstance) return;

  const textColor = isDark ? "#ffffff" : "#1e1f24";
  const gridColor = isDark ? "rgba(39, 72, 125, 0.45)" : "rgba(205, 206, 215, 0.6)";

  // Actualizar leyenda
  scatterChartInstance.options.plugins.legend.labels.color = textColor;

  // Actualizar ejes X e Y
  scatterChartInstance.options.scales.x.title.color = textColor;
  scatterChartInstance.options.scales.x.ticks.color = textColor;
  scatterChartInstance.options.scales.x.grid.color = gridColor;

  scatterChartInstance.options.scales.y.title.color = textColor;
  scatterChartInstance.options.scales.y.ticks.color = textColor;
  scatterChartInstance.options.scales.y.grid.color = gridColor;

  // Actualizar borde de puntos para contraste
  if (scatterChartInstance.data.datasets[0]) {
    scatterChartInstance.data.datasets[0].borderColor = isDark ? "#ffffff" : "#3b66ac";
  }

  scatterChartInstance.update();
}

function createCard(title, val, warn = null) {
  const card = document.createElement("div");
  card.className = "metric-card";
  card.innerHTML = `
    <span class="metric-card__title">${title}</span>
    <span class="metric-card__val">${val}</span>
    ${warn ? `<span class="metric-card__warn">⚠ ${warn}</span>` : ""}
  `;
  return card;
}