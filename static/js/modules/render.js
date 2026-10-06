const formatVal = (v) => (v === null || v === undefined ? "--" : Number(v).toFixed(4));

export function renderSummaryTable(allData) {
  const tableSection = document.getElementById("summarySection");
  const tbody = document.querySelector("#summaryTable tbody");
  tbody.innerHTML = "";

  const cols = Object.keys(allData);
  if (cols.length <= 1 && cols[0] === "Entrada Manual") {
    tableSection.classList.add("panel--hidden");
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
      <td>${formatVal(res.harmonic)}</td>
      <td>${formatVal(res.geometric)}</td>
      <td>${formatVal(res.quartiles?.iqr)}</td>
    `;
    tbody.appendChild(tr);
  });

  tableSection.classList.remove("panel--hidden");
}

export function renderColumnPills(columns, activeCol, onSelectCol) {
  const container = document.getElementById("columnPills");
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
  container.innerHTML = "";
  const { results, warnings, chart } = columnPayload;

  // Tarjeta de Sesgo / Distribución
  const skewCard = document.createElement("div");
  skewCard.className = "metric-card";
  skewCard.style.borderLeft = "4px solid var(--primary-hover)";
  skewCard.innerHTML = `
    <span class="metric-card__title">Distribución y Asimetría</span>
    <span class="metric-card__val" style="font-size: 1.1rem;">${chart.skewness}</span>
    <span class="metric-card__warn" style="color: var(--primary-hover);">Muestras analizadas: N = ${chart.n}</span>
  `;
  container.appendChild(skewCard);

  if ("mean" in results) {
    container.appendChild(createCard("Media Aritmética (X̄)", formatVal(results.mean)));
  }
  if ("harmonic" in results) {
    container.appendChild(createCard("Media Armónica (H)", formatVal(results.harmonic), warnings.harmonic));
  }
  if ("geometric" in results) {
    container.appendChild(createCard("Media Geométrica (G)", formatVal(results.geometric), warnings.geometric));
  }
  if ("mode" in results) {
    const modas = results.mode;
    const val = modas.length ? modas.map((m) => Number(m).toFixed(2)).join(", ") : "Amodal";
    container.appendChild(createCard("Moda", val, warnings.mode));
  }
  if ("quartiles" in results) {
    const q = results.quartiles;
    container.appendChild(createCard("Mediana / Q2", formatVal(q.q2)));
    container.appendChild(createCard("Rango Intercuartílico (IQR)", formatVal(q.iqr), `Q1: ${q.q1.toFixed(2)} | Q3: ${q.q3.toFixed(2)}`));
  }
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