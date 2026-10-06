const alertModal = document.getElementById("alertModal");
const alertModalTitle = document.getElementById("alertModalTitle");
const alertModalMessage = document.getElementById("alertModalMessage");
const btnCloseAlert = document.getElementById("btnCloseAlert");

const csvColumnModal = document.getElementById("csvColumnModal");
const csvColumnSelect = document.getElementById("csvColumnSelect");
const btnConfirmColumn = document.getElementById("btnConfirmColumn");

// Listener de cierre de alerta
btnCloseAlert.addEventListener("click", () => alertModal.close());

/**
 * Muestra el pop-up de alerta/error.
 */
export function showAlert(message, title = "Aviso") {
  alertModalTitle.textContent = title;
  alertModalMessage.textContent = message;
  alertModal.showModal();
}

/**
 * Despliega el pop-up para seleccionar columna numérica del CSV.
 * @param {Array<string>} columns - Lista de nombres de columnas.
 * @param {Function} onConfirm - Callback al confirmar selección.
 */
export function showColumnModal(columns, onConfirm) {
  csvColumnSelect.innerHTML = "";
  columns.forEach((col) => {
    const opt = document.createElement("option");
    opt.value = col;
    opt.textContent = col;
    csvColumnSelect.appendChild(opt);
  });

  csvColumnModal.showModal();

  btnConfirmColumn.onclick = () => {
    const selected = csvColumnSelect.value;
    csvColumnModal.close();
    onConfirm(selected);
  };
}