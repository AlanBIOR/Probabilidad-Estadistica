/**
 * Módulo: metrics.js
 * Gestión de selección de métricas y ventana modal emergente.
 */

export function initMetrics() {
  const modal = document.getElementById("metricsModal");
  const openBtn = document.getElementById("btnOpenMetricsModal");
  const closeBtn = document.getElementById("btnCloseMetricsModal");
  const toggleBtn = document.getElementById("btnToggleAllMetrics");
  const label = document.getElementById("metricsBtnLabel");
  const checkboxes = document.querySelectorAll('input[name="metric"]');

  // Asegurar que el modal inicie cerrado
  if (modal && modal.hasAttribute("open")) {
    modal.close();
  }

  function updateCount() {
    const activeCount = document.querySelectorAll('input[name="metric"]:checked').length;
    if (label) label.textContent = `Configurar Métricas (${activeCount} activas)`;
  }

  // Abrir modal solo al hacer clic en el botón
  if (openBtn && modal) {
    openBtn.addEventListener("click", () => {
      modal.showModal();
    });
  }

  // Cerrar modal al presionar el botón de confirmación
  if (closeBtn && modal) {
    closeBtn.addEventListener("click", () => {
      updateCount();
      modal.close();
    });
  }

  // Cerrar al hacer clic fuera del modal (en el backdrop)
  if (modal) {
    modal.addEventListener("click", (event) => {
      const rect = modal.getBoundingClientRect();
      const clickInside = (
        rect.top <= event.clientY &&
        event.clientY <= rect.top + rect.height &&
        rect.left <= event.clientX &&
        event.clientX <= rect.left + rect.width
      );
      if (!clickInside) {
        updateCount();
        modal.close();
      }
    });
  }

  // Botón para alternar marcar / desmarcar todos
  if (toggleBtn) {
    toggleBtn.addEventListener("click", () => {
      const areSomeChecked = Array.from(checkboxes).some((cb) => cb.checked);
      checkboxes.forEach((cb) => (cb.checked = !areSomeChecked));
      toggleBtn.textContent = areSomeChecked ? "Marcar todos" : "Desmarcar todos";
      updateCount();
    });
  }

  checkboxes.forEach((cb) => cb.addEventListener("change", updateCount));
  updateCount();
}

export function getSelectedMetrics() {
  const checkboxes = document.querySelectorAll('input[name="metric"]:checked');
  return Array.from(checkboxes).map((cb) => cb.value);
}