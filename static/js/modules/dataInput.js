import { showAlert } from "./modal.js";

let selectedFile = null;

export function initDataInputs() {
  const inputN = document.getElementById("inputN");
  const btnGenInputs = document.getElementById("btnGenInputs");
  const dynamicInputs = document.getElementById("dynamicInputs");

  btnGenInputs.addEventListener("click", () => {
    const n = parseInt(inputN.value, 10);
    if (!n || n < 1 || n > 500) {
      showAlert("Ingresa una cantidad de muestras válida (entre 1 y 500).");
      return;
    }

    dynamicInputs.innerHTML = "";
    dynamicInputs.classList.remove("panel--hidden");

    for (let i = 0; i < n; i++) {
      const input = document.createElement("input");
      input.type = "number";
      input.step = "any";
      input.placeholder = `x${i + 1}`;
      input.required = true;
      dynamicInputs.appendChild(input);
    }
  });

  const dropzone = document.getElementById("dropzone");
  const fileInput = document.getElementById("fileInput");
  const fileStatus = document.getElementById("fileStatus");

  dropzone.addEventListener("click", () => fileInput.click());
  dropzone.addEventListener("dragover", (e) => {
    e.preventDefault();
    dropzone.classList.add("dropzone--dragover");
  });
  dropzone.addEventListener("dragleave", () => dropzone.classList.remove("dropzone--dragover"));
  dropzone.addEventListener("drop", (e) => {
    e.preventDefault();
    dropzone.classList.remove("dropzone--dragover");
    if (e.dataTransfer.files.length) handleFile(e.dataTransfer.files[0], fileStatus);
  });
  fileInput.addEventListener("change", (e) => {
    if (e.target.files.length) handleFile(e.target.files[0], fileStatus);
  });
}

function handleFile(file, statusElement) {
  selectedFile = file;
  statusElement.textContent = `Archivo seleccionado: ${file.name} (${(file.size / 1024).toFixed(1)} KB)`;
}

export function getPayload(activeTab, metrics) {
  if (activeTab === "manual") {
    const inputs = document.querySelectorAll("#dynamicInputs input");
    if (!inputs.length) {
      showAlert("Genera y completa las celdas numéricas primero.");
      return null;
    }
    const values = [];
    for (const inp of inputs) {
      if (inp.value.trim() === "") {
        showAlert("Todas las celdas deben tener un valor numérico.");
        return null;
      }
      values.push(parseFloat(inp.value));
    }
    return { isFile: false, body: { data: values, metrics } };
  }

  if (!selectedFile) {
    showAlert("Selecciona o arrastra un archivo .csv o .txt primero.");
    return null;
  }

  const formData = new FormData();
  formData.append("file", selectedFile);
  metrics.forEach((m) => formData.append("metrics", m));
  return { isFile: true, body: formData };
}