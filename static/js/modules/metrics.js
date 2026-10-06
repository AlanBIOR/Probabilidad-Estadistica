export function initMetrics() {
  const btnToggle = document.getElementById("btnToggleAllMetrics");

  btnToggle.addEventListener("click", () => {
    const checkboxes = document.querySelectorAll('input[name="metric"]');
    const allChecked = Array.from(checkboxes).every((cb) => cb.checked);
    checkboxes.forEach((cb) => (cb.checked = !allChecked));
    btnToggle.textContent = allChecked ? "Marcar todos" : "Desmarcar todos";
  });
}

export function getSelectedMetrics() {
  return Array.from(document.querySelectorAll('input[name="metric"]:checked')).map((cb) => cb.value);
}