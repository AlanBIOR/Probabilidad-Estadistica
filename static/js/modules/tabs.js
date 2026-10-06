export function initTabs(onTabChange) {
  const tabManualBtn = document.getElementById("tabManualBtn");
  const tabFileBtn = document.getElementById("tabFileBtn");
  const panelManual = document.getElementById("panelManual");
  const panelFile = document.getElementById("panelFile");

  tabManualBtn.addEventListener("click", () => {
    tabManualBtn.classList.add("tabs__btn--active");
    tabFileBtn.classList.remove("tabs__btn--active");
    panelManual.classList.remove("panel--hidden");
    panelFile.classList.add("panel--hidden");
    if (typeof onTabChange === "function") onTabChange("manual");
  });

  tabFileBtn.addEventListener("click", () => {
    tabFileBtn.classList.add("tabs__btn--active");
    tabManualBtn.classList.remove("tabs__btn--active");
    panelFile.classList.remove("panel--hidden");
    panelManual.classList.add("panel--hidden");
    if (typeof onTabChange === "function") onTabChange("file");
  });
}