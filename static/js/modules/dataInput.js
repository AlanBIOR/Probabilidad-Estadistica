/**
 * Módulo: dataInput.js
 * Genera tablas editables en pantalla para ingreso manual univariado y multivariado,
 * gestiona archivos .csv/.txt y genera el payload correspondiente.
 */
import { showAlert } from "./modal.js";

export function initDataInputs() {
  const dropzone = document.getElementById("dropzone");
  const fileInput = document.getElementById("fileInput");
  const fileStatus = document.getElementById("fileStatus");
  const btnGenTable = document.getElementById("btnGenTable");
  const btnLoadExample = document.getElementById("btnLoadExample");
  const inputCols = document.getElementById("inputCols");
  const inputRows = document.getElementById("inputRows");

  const radioDescriptive = document.querySelector('input[name="analysisType"][value="descriptive"]');
  const radioCovariance = document.querySelector('input[name="analysisType"][value="covariance"]');
  const cardDescriptive = document.getElementById("cardOptDescriptive");
  const cardCovariance = document.getElementById("cardOptCovariance");
  const btnMetrics = document.getElementById("btnOpenMetricsModal");

  // Arrastre y subida de archivos
  if (dropzone && fileInput) {
    dropzone.addEventListener("click", () => fileInput.click());

    dropzone.addEventListener("dragover", (e) => {
      e.preventDefault();
      dropzone.classList.add("dropzone--dragover");
    });

    dropzone.addEventListener("dragleave", () => {
      dropzone.classList.remove("dropzone--dragover");
    });

    dropzone.addEventListener("drop", (e) => {
      e.preventDefault();
      dropzone.classList.remove("dropzone--dragover");
      if (e.dataTransfer.files.length) {
        fileInput.files = e.dataTransfer.files;
        actualizarEstadoArchivo(fileInput.files[0]);
      }
    });

    fileInput.addEventListener("change", () => {
      if (fileInput.files.length) {
        actualizarEstadoArchivo(fileInput.files[0]);
      }
    });
  }

  function actualizarEstadoArchivo(file) {
    if (fileStatus) {
      fileStatus.textContent = `Archivo seleccionado: ${file.name} (${(file.size / 1024).toFixed(1)} KB)`;
    }
  }

  // Generación de la tabla editable en pantalla
  function construirTablaEditable(cols, rows, datosIniciales = null) {
    const table = document.getElementById("manualInputTable");
    const thead = table.querySelector("thead");
    const tbody = table.querySelector("tbody");
    if (!table || !thead || !tbody) return;

    thead.innerHTML = "";
    tbody.innerHTML = "";

    // Nombres de columnas por defecto (X, Y, Z, o Var_1, Var_2...)
    const letras = ["X", "Y", "Z", "W", "V", "U"];
    let headHtml = "<tr><th>#</th>";
    for (let c = 0; c < cols; c++) {
      const nombreCol = cols <= letras.length ? letras[c] : `Var_${c + 1}`;
      headHtml += `<th><input type="text" class="manual-table-header" value="${nombreCol}" style="width: 100%; border: none; background: transparent; font-weight: 800; text-align: center; color: var(--text-title);"></th>`;
    }
    headHtml += "</tr>";
    thead.innerHTML = headHtml;

    // Generar celdas de entrada
    for (let r = 0; r < rows; r++) {
      const tr = document.createElement("tr");
      let rowHtml = `<td style="font-weight: 700; color: var(--text-body); text-align: center;">${r + 1}</td>`;
      for (let c = 0; c < cols; c++) {
        const val = (datosIniciales && datosIniciales[r] && datosIniciales[r][c] !== undefined)
          ? datosIniciales[r][c]
          : "";
        rowHtml += `<td><input type="number" step="any" class="manual-cell-input" data-row="${r}" data-col="${c}" value="${val}" placeholder="0.0" style="width: 100%; padding: 0.45rem; border: 1px solid var(--border); border-radius: 6px; background: var(--surface); color: var(--text-title); text-align: center;"></td>`;
      }
      tr.innerHTML = rowHtml;
      tbody.appendChild(tr);
    }
  }

  // Listener para construir tabla con los inputs
  if (btnGenTable && inputCols && inputRows) {
    btnGenTable.addEventListener("click", () => {
      const cols = parseInt(inputCols.value, 10) || 1;
      const rows = parseInt(inputRows.value, 10) || 5;
      construirTablaEditable(cols, rows);
    });
  }

  // Carga de ejemplo de las diapositivas (X, Y, Z con 5 filas)
  if (btnLoadExample) {
    btnLoadExample.addEventListener("click", () => {
      const esCov = radioCovariance?.checked;
      if (esCov) {
        inputCols.value = 3;
        inputRows.value = 5;
        // Datos de la diapositiva de la clase (datos_x_y_z.txt)
        const ejemploCov = [
          [75, 10.5, 45],
          [65, 12.8, 65],
          [22, 7.3, 74],
          [15, 2.1, 76],
          [18, 9.2, 56]
        ];
        construirTablaEditable(3, 5, ejemploCov);
      } else {
        inputCols.value = 1;
        inputRows.value = 10;
        const ejemploDesc = [[12], [15], [14], [10], [18], [22], [15], [19], [17], [16]];
        construirTablaEditable(1, 10, ejemploDesc);
      }
    });
  }

  // Ajustar configuración según el tipo de análisis
  function sincronizarTipoAnalisis() {
    const esCov = radioCovariance?.checked;
    if (esCov) {
      cardCovariance?.classList.add("analysis-card--active");
      cardDescriptive?.classList.remove("analysis-card--active");
      if (btnMetrics) btnMetrics.style.display = "none";
      if (parseInt(inputCols.value, 10) < 2) {
        inputCols.value = 2; // Covarianza requiere al menos 2 variables
      }
      construirTablaEditable(parseInt(inputCols.value, 10), parseInt(inputRows.value, 10));
    } else {
      cardDescriptive?.classList.add("analysis-card--active");
      cardCovariance?.classList.remove("analysis-card--active");
      if (btnMetrics) btnMetrics.style.display = "inline-flex";
      inputCols.value = 1;
      construirTablaEditable(1, parseInt(inputRows.value, 10));
    }
  }

  radioDescriptive?.addEventListener("change", sincronizarTipoAnalisis);
  radioCovariance?.addEventListener("change", sincronizarTipoAnalisis);

  // Inicializar tabla por defecto
  sincronizarTipoAnalisis();
}

export function getPayload(currentTab, metrics) {
  const fileInput = document.getElementById("fileInput");
  const radioCovariance = document.querySelector('input[name="analysisType"][value="covariance"]');
  const analysisType = radioCovariance?.checked ? "covariance" : "descriptive";

  if (currentTab === "file") {
    if (!fileInput.files.length) {
      showAlert("Por favor selecciona o arrastra un archivo (.csv o .txt).", "Aviso");
      return null;
    }
    const formData = new FormData();
    formData.append("file", fileInput.files[0]);
    formData.append("analysis_type", analysisType);
    metrics.forEach((m) => formData.append("metrics", m));
    return { isFile: true, body: formData };
  } else {
    // Si escribió en el textarea en bloque
    const rawTextarea = document.getElementById("manualRawTextarea")?.value.trim();
    if (rawTextarea) {
      return {
        isFile: false,
        body: { raw_text: rawTextarea, analysis_type: analysisType, metrics }
      };
    }

    // Si llenó la tabla editable en pantalla
    const table = document.getElementById("manualInputTable");
    const headerInputs = table.querySelectorAll(".manual-table-header");
    const headers = Array.from(headerInputs).map((inp, idx) => inp.value.trim() || `Var_${idx + 1}`);

    const rowElements = table.querySelectorAll("tbody tr");
    const matrix = [];

    rowElements.forEach((tr) => {
      const cellInputs = tr.querySelectorAll(".manual-cell-input");
      const rowVals = [];
      let rowHasData = false;

      cellInputs.forEach((inp) => {
        const val = inp.value.trim();
        if (val !== "") {
          rowHasData = true;
          rowVals.push(parseFloat(val));
        }
      });

      if (rowHasData && rowVals.length === headers.length) {
        matrix.push(rowVals);
      }
    });

    if (!matrix.length) {
      showAlert("Ingresa valores numéricos en la tabla editable o pega tus datos en el bloque inferior.", "Aviso");
      return null;
    }

    return {
      isFile: false,
      body: {
        table_matrix: matrix,
        headers: headers,
        analysis_type: analysisType,
        metrics: metrics
      }
    };
  }
}