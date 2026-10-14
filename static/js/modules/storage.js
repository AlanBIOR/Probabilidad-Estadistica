/**
 * Módulo: storage.js
 * Persistencia segura en localStorage (resiliente a cuotas de 5 MB).
 */

const STORAGE_KEY = "data_studio_analysis_cache";
const VIEW_KEY = "data_studio_active_view";

export function guardarVistaActiva(viewName) {
  try {
    localStorage.setItem(VIEW_KEY, viewName);
  } catch (e) {
    console.warn("Error guardando vista:", e);
  }
}

export function obtenerVistaActiva() {
  return localStorage.getItem(VIEW_KEY) || "dashboard";
}

export function guardarAnalisisLocal(payload) {
  try {
    const copia = JSON.parse(JSON.stringify(payload));

    // Si hay más de 3 pares, no guardamos los Base64 de las imágenes para no superar el límite del navegador
    if (copia.bivariate_pairs && copia.bivariate_pairs.length > 3) {
      copia.bivariate_pairs = copia.bivariate_pairs.map((p) => {
        const { image_base64, ...resto } = p;
        return resto;
      });
    }

    localStorage.setItem(STORAGE_KEY, JSON.stringify(copia));
  } catch (err) {
    console.warn("No se pudo almacenar en localStorage por tamaño:", err);
  }
}

export function obtenerAnalisisLocal() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    return raw ? JSON.parse(raw) : null;
  } catch (e) {
    return null;
  }
}

export function limpiarAnalisisLocal() {
  localStorage.removeItem(STORAGE_KEY);
  localStorage.removeItem(VIEW_KEY);
}