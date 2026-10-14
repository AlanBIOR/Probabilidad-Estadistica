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
  renderAllBivariatePlots,
  updateScatterTheme
} from "./modules/render.js";
import { renderDistributionChart, updateChartTheme } from "./modules/chartManager.js";
import { showAlert } from "./modules/modal.js";
import {
  guardarAnalisisLocal,
  obtenerAnalisisLocal,
  limpiarAnalisisLocal,
  guardarVistaActiva,
  obtenerVistaActiva
} from "./modules/storage.js";

document.addEventListener("DOMContentLoaded", () => {
  const resultsContainer = document.getElementById("resultsContainer");
  const chartSection = document.getElementById("chartSection");
  const chartCanvas = document.getElementById("statsChart");
  const btnCalculate = document.getElementById("btnCalculate");

  let currentTab = "file";
  let datasetResults = null;
  let activeColumn = null;

  initTheme((isDark) => {
    updateChartTheme(isDark);
    updateScatterTheme(isDark);
  });

  initTabs((tab) => { currentTab = tab; });
  initDataInputs();
  initMetrics();

  // Restaurar estado al recargar o cambiar de tema
  restaurarEstadoPrevio();

  function restaurarEstadoPrevio() {
    const cache = obtenerAnalisisLocal();
    if (!cache) return;

    if (cache.analysis_type === "covariance") {
      renderCovarianceMatrix(cache.covariance);
      if (cache.bivariate_pairs) {
        renderAllBivariatePlots(cache.bivariate_pairs);
      }
      switchView(obtenerVistaActiva() === "covariance" ? "covariance" : "dashboard");
    } else if (cache.analysis_type === "descriptive" && cache.data) {
      datasetResults = cache.data;
      activeColumn = cache.columns[0];

      renderSummaryTable(datasetResults);
      renderColumnView(cache.columns, activeColumn);
      if (chartSection) {
        chartSection.classList.remove("panel--hidden");
        chartSection.dataset.hasData = "true";
      }
      switchView(obtenerVistaActiva() === "descriptive" ? "descriptive" : "dashboard");
    }
  }

  btnCalculate.addEventListener("click", async () => {
    const metrics = getSelectedMetrics();
    if (!metrics.length) {
      showAlert("Selecciona al menos una métrica para calcular.", "Aviso");
      return;
    }

    const payloadObj = getPayload(currentTab, metrics);
    if (!payloadObj) return;

    // Adjuntar el tema actual a la petición
    const currentTheme = document.documentElement.getAttribute("data-theme") || "dark";
    if (payloadObj.isFile) {
      payloadObj.body.append("theme", currentTheme);
    } else {
      payloadObj.body.theme = currentTheme;
    }

    try {
      btnCalculate.disabled = true;
      btnCalculate.textContent = "Procesando...";

      const res = await executeProcess(payloadObj.body, payloadObj.isFile);
      guardarAnalisisLocal(res);

      if (res.analysis_type === "covariance") {
        renderCovarianceMatrix(res.covariance);
        if (res.bivariate_pairs) {
          renderAllBivariatePlots(res.bivariate_pairs);
        }
        guardarVistaActiva("covariance");
        switchView("covariance");
      } else {
        datasetResults = res.data;
        activeColumn = res.columns[0];

        renderSummaryTable(datasetResults);
        renderColumnView(res.columns, activeColumn);
        if (chartSection) {
          chartSection.classList.remove("panel--hidden");
          chartSection.dataset.hasData = "true";
        }
        guardarVistaActiva("descriptive");
        switchView("descriptive");
      }
    } catch (err) {
      showAlert(err.message, "Error en el Análisis");
    } finally {
      btnCalculate.disabled = false;
      btnCalculate.textContent = "EJECUTAR ANÁLISIS Y VER RESULTADOS";
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

  const btnReset = document.getElementById("btnResetData");
  if (btnReset) {
    btnReset.addEventListener("click", () => {
      limpiarAnalisisLocal();
      location.reload();
    });
  }
});