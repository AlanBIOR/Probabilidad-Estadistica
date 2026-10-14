/**
 * Módulo: render.js
 * Renderizado de tablas, tarjetas KPI, matriz de covarianza
 * y visor interactivo 1 a 1 de pares bivariados con selector y navegación.
 */

let activeScatterChart = null;
let currentBivariatePairs = [];
let currentPairIndex = 0;

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

  const skewCard = document.createElement("div");
  skewCard.className = "metric-card";
  skewCard.style.borderLeft = "4px solid var(--primary-hover)";
  skewCard.innerHTML = `
    <span class="metric-card__title">Distribución y Asimetría</span>
    <span class="metric-card__val" style="font-size: 1.1rem;">${chart.skewness}</span>
    <span class="metric-card__warn" style="color: var(--primary-hover);">Muestras analizadas: N = ${chart.n}</span>
  `;
  container.appendChild(skewCard);

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

/**
 * Inicializa el visor bivariado poblando la lista desplegable y activando el primer par
 */
export function renderAllBivariatePlots(pairsList) {
  const panel = document.getElementById("scatterViewerPanel");
  const dropdown = document.getElementById("pairSelectDropdown");
  const badge = document.getElementById("scatterPairsBadge");
  const btnPrev = document.getElementById("btnPrevPair");
  const btnNext = document.getElementById("btnNextPair");

  const btnInteractive = document.getElementById("btnShowInteractiveScatter");
  const btnPlt = document.getElementById("btnShowPltImage");
  const contInteractive = document.getElementById("interactiveScatterContainer");
  const contPlt = document.getElementById("pltImageContainer");

  if (!pairsList || !pairsList.length || !panel) {
    if (panel) panel.classList.add("panel--hidden");
    return;
  }

  currentBivariatePairs = pairsList;
  currentPairIndex = 0;

  panel.classList.remove("panel--hidden");
  if (badge) badge.textContent = `${pairsList.length} Pares Disponibles`;

  // Poblar la lista desplegable con los nombres de los pares y su valor de correlación
  if (dropdown) {
    dropdown.innerHTML = "";
    pairsList.forEach((pair, idx) => {
      const opt = document.createElement("option");
      opt.value = idx;
      opt.textContent = `${idx + 1}. ${pair.pair_name}  (r = ${pair.r.toFixed(4)})`;
      dropdown.appendChild(opt);
    });

    dropdown.onchange = () => {
      renderSpecificBivariateIndex(parseInt(dropdown.value, 10));
    };
  }

  // Controles de navegación Anterior / Siguiente
  if (btnPrev && btnNext) {
    btnPrev.onclick = () => {
      if (currentPairIndex > 0) {
        renderSpecificBivariateIndex(currentPairIndex - 1);
      }
    };

    btnNext.onclick = () => {
      if (currentPairIndex < currentBivariatePairs.length - 1) {
        renderSpecificBivariateIndex(currentPairIndex + 1);
      }
    };
  }

  // Conmutador entre Interactivo y Matplotlib
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

  // Renderizar el primer par seleccionado
  renderSpecificBivariateIndex(0);
}

/**
 * Renderiza la gráfica y estadísticas del par seleccionado en el visor
 */
function renderSpecificBivariateIndex(index) {
  if (index < 0 || index >= currentBivariatePairs.length) return;
  currentPairIndex = index;

  const pairData = currentBivariatePairs[index];
  const dropdown = document.getElementById("pairSelectDropdown");
  const btnPrev = document.getElementById("btnPrevPair");
  const btnNext = document.getElementById("btnNextPair");

  // Sincronizar el valor de la lista y el estado de los botones
  if (dropdown) dropdown.value = index;
  if (btnPrev) btnPrev.disabled = index === 0;
  if (btnNext) btnNext.disabled = index === currentBivariatePairs.length - 1;

  // Actualizar tarjetas de métricas del par
  const valCov = document.getElementById("activePairCov");
  const valR = document.getElementById("activePairR");
  const valEq = document.getElementById("activePairEq");
  const imgPlt = document.getElementById("pltScatterImg");

  if (valCov) valCov.textContent = pairData.cov.toFixed(4);
  if (valR) valR.textContent = pairData.r.toFixed(4);
  if (valEq) valEq.textContent = pairData.equation;
  if (imgPlt) imgPlt.src = pairData.image_base64;

  // Renderizar la gráfica en el canvas interactivo
  const canvas = document.getElementById("interactiveScatterChart");
  if (!canvas) return;

  if (activeScatterChart) {
    activeScatterChart.destroy();
  }

  const isDark = (document.documentElement.getAttribute("data-theme") || "dark") === "dark";
  const textColor = isDark ? "#ffffff" : "#1e1f24";
  const gridColor = isDark ? "rgba(39, 72, 125, 0.45)" : "rgba(205, 206, 215, 0.6)";

  activeScatterChart = new Chart(canvas, {
    type: "scatter",
    data: {
      datasets: [
        {
          label: `Muestras (${pairData.col_x}, ${pairData.col_y})`,
          data: pairData.points,
          backgroundColor: pairData.colors.point,
          borderColor: isDark ? "#ffffff" : "#112340",
          borderWidth: 1.5,
          pointRadius: 6.5,
          pointHoverRadius: 9.5
        },
        {
          label: `Tendencia (${pairData.equation})`,
          data: pairData.trend_line,
          type: "line",
          borderColor: pairData.colors.line,
          borderWidth: 2.4,
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
            label: (ctx) => `(${pairData.col_x}: ${ctx.parsed.x.toFixed(2)}, ${pairData.col_y}: ${ctx.parsed.y.toFixed(2)})`
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
            text: pairData.col_x,
            color: textColor,
            font: { size: 12, weight: "bold" }
          },
          ticks: { color: textColor, font: { size: 11, weight: "600" } },
          grid: { color: gridColor }
        },
        y: {
          title: {
            display: true,
            text: pairData.col_y,
            color: textColor,
            font: { size: 12, weight: "bold" }
          },
          ticks: { color: textColor, font: { size: 11, weight: "600" } },
          grid: { color: gridColor }
        }
      }
    }
  });
}

export function updateScatterTheme(isDark) {
  if (!activeScatterChart) return;

  const textColor = isDark ? "#ffffff" : "#1e1f24";
  const gridColor = isDark ? "rgba(39, 72, 125, 0.45)" : "rgba(205, 206, 215, 0.6)";

  activeScatterChart.options.plugins.legend.labels.color = textColor;
  activeScatterChart.options.scales.x.title.color = textColor;
  activeScatterChart.options.scales.x.ticks.color = textColor;
  activeScatterChart.options.scales.x.grid.color = gridColor;

  activeScatterChart.options.scales.y.title.color = textColor;
  activeScatterChart.options.scales.y.ticks.color = textColor;
  activeScatterChart.options.scales.y.grid.color = gridColor;

  if (activeScatterChart.data.datasets[0]) {
    activeScatterChart.data.datasets[0].borderColor = isDark ? "#ffffff" : "#112340";
  }

  activeScatterChart.update();
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