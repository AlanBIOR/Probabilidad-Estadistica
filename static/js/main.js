import { initTheme } from "./modules/theme.js";
import { initTabs } from "./modules/tabs.js";
import { initDataInputs, getPayload } from "./modules/dataInput.js";
import { initMetrics, getSelectedMetrics } from "./modules/metrics.js";
import { executeProcess } from "./modules/api.js";
import { renderSummaryTable, renderColumnPills, renderColumnCards } from "./modules/render.js";
import { renderDistributionChart, updateChartTheme } from "./modules/chartManager.js";
import { showAlert } from "./modules/modal.js";

document.addEventListener("DOMContentLoaded", () => {
  const resultsContainer = document.getElementById("resultsContainer");
  const chartSection = document.getElementById("chartSection");
  const chartCanvas = document.getElementById("statsChart");
  const btnCalculate = document.getElementById("btnCalculate");

  let currentTab = "manual";
  let datasetResults = null;
  let activeColumn = null;

  initTheme((isDark) => updateChartTheme(isDark));
  initTabs((tab) => { currentTab = tab; });
  initDataInputs();
  initMetrics();

  btnCalculate.addEventListener("click", async () => {
    const metrics = getSelectedMetrics();
    if (!metrics.length) {
      showAlert("Selecciona al menos una métrica para calcular.");
      return;
    }

    const payloadObj = getPayload(currentTab, metrics);
    if (!payloadObj) return;

    try {
      btnCalculate.disabled = true;
      btnCalculate.textContent = "Procesando...";

      const res = await executeProcess(payloadObj.body, payloadObj.isFile);
      datasetResults = res.data;
      activeColumn = res.columns[0];

      // 1. Mostrar tabla resumen general
      renderSummaryTable(datasetResults);

      // 2. Mostrar selector de columnas y vista detallada
      renderColumnView(res.columns, activeColumn);

      chartSection.classList.remove("panel--hidden");
    } catch (err) {
      showAlert(err.message, "Error en el Análisis");
    } finally {
      btnCalculate.disabled = false;
      btnCalculate.textContent = "Ejecutar Análisis Completo";
    }
  });

  function renderColumnView(columns, columnToSelect) {
    activeColumn = columnToSelect;
    const colData = datasetResults[activeColumn];

    renderColumnPills(columns, activeColumn, (newCol) => {
      renderColumnView(columns, newCol);
    });

    renderColumnCards(colData, resultsContainer);

    const isDark = document.documentElement.getAttribute("data-theme") === "dark";
    renderDistributionChart(chartCanvas, colData.chart, isDark);
  }
});