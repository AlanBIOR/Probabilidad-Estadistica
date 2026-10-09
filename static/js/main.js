/**
 * main.js - Orquestador principal de Data Studio
 */
import { initTheme } from "./modules/theme.js";
import { initTabs, switchView } from "./modules/tabs.js";
import { initDataInputs, getPayload } from "./modules/dataInput.js";
import { initMetrics, getSelectedMetrics } from "./modules/metrics.js";
import { executeProcess } from "./modules/api.js";
import {
  renderSummaryTable,
  renderColumnPills,
  renderColumnCards,
  renderCovarianceMatrix,
  renderBivariateScatter,
  updateScatterTheme
} from "./modules/render.js";
import { renderDistributionChart, updateChartTheme } from "./modules/chartManager.js";
import { showAlert } from "./modules/modal.js";

document.addEventListener("DOMContentLoaded", () => {
  const resultsContainer = document.getElementById("resultsContainer");
  const chartSection = document.getElementById("chartSection");
  const chartCanvas = document.getElementById("statsChart");
  const btnCalculate = document.getElementById("btnCalculate");

  let currentTab = "file";
  let datasetResults = null;
  let activeColumn = null;

  // Sincronizar tema en ambos gráficos (Histograma + Dispersión)
  initTheme((isDark) => {
    updateChartTheme(isDark);
    updateScatterTheme(isDark);
  });

  initTabs((tab) => { currentTab = tab; });
  initDataInputs();
  initMetrics();

  btnCalculate.addEventListener("click", async () => {
    const metrics = getSelectedMetrics();
    if (!metrics.length) {
      showAlert("Selecciona al menos una métrica para calcular.", "Aviso");
      return;
    }

    const payloadObj = getPayload(currentTab, metrics);
    if (!payloadObj) return;

    const analysisType = document.querySelector('input[name="analysisType"]:checked')?.value || "descriptive";

    try {
      btnCalculate.disabled = true;
      btnCalculate.textContent = "Procesando...";

      const res = await executeProcess(payloadObj.body, payloadObj.isFile);
      datasetResults = res.data;
      activeColumn = res.columns[0];

      // 1. Llenar módulo descriptivo
      renderSummaryTable(datasetResults);
      renderColumnView(res.columns, activeColumn);
      if (chartSection) {
        chartSection.classList.remove("panel--hidden");
        chartSection.dataset.hasData = "true";
      }

      // 2. Llenar módulo de covarianza y dispersión
      if (res.covariance) {
        renderCovarianceMatrix(res.covariance);
      }
      if (res.bivariate) {
        renderBivariateScatter(res.bivariate);
      }

      // 3. Redirección automática al apartado correspondiente
      if (analysisType === "covariance") {
        if (!res.covariance) {
          showAlert("Se requieren al menos 2 variables numéricas para calcular la covarianza. Mostrando vista descriptiva.", "Aviso");
          switchView("descriptive");
        } else {
          switchView("covariance");
        }
      } else {
        switchView("descriptive");
      }
    } catch (err) {
      showAlert(err.message, "Error en el Análisis");
    } finally {
      btnCalculate.disabled = false;
      btnCalculate.textContent = "Ejecutar Análisis y Ver Resultados";
    }
  });

  function renderColumnView(columns, columnToSelect) {
    activeColumn = columnToSelect;
    const colData = datasetResults[activeColumn];

    renderColumnPills(columns, activeColumn, (newCol) => {
      renderColumnView(columns, newCol);
    });

    renderColumnCards(colData, resultsContainer);

    const isDark = (document.documentElement.getAttribute("data-theme") || "dark") === "dark";
    if (chartCanvas && colData.chart) {
      renderDistributionChart(chartCanvas, colData.chart, isDark);
    }
  }
});