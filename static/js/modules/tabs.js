export function switchView(targetView) {
  const navItems = document.querySelectorAll(".sidebar__nav-item");
  const dashboardSection = document.getElementById("dashboardSection");
  const descriptiveSection = document.getElementById("descriptiveSection");
  const covarianceSection = document.getElementById("covarianceSection");

  navItems.forEach((btn) => {
    if (btn.dataset.view === targetView) {
      btn.classList.add("sidebar__nav-item--active");
    } else {
      btn.classList.remove("sidebar__nav-item--active");
    }
  });

  if (dashboardSection) dashboardSection.classList.add("panel--hidden");
  if (descriptiveSection) descriptiveSection.classList.add("panel--hidden");
  if (covarianceSection) covarianceSection.classList.add("panel--hidden");

  if (targetView === "dashboard") {
    dashboardSection?.classList.remove("panel--hidden");
  } else if (targetView === "descriptive") {
    descriptiveSection?.classList.remove("panel--hidden");
  } else if (targetView === "covariance") {
    covarianceSection?.classList.remove("panel--hidden");
  }
}

export function initTabs(onTabChange) {
  const tabManualBtn = document.getElementById("tabManualBtn");
  const tabFileBtn = document.getElementById("tabFileBtn");
  const panelManual = document.getElementById("panelManual");
  const panelFile = document.getElementById("panelFile");

  if (tabFileBtn && tabManualBtn) {
    tabFileBtn.addEventListener("click", () => {
      tabFileBtn.classList.add("tabs__btn--active");
      tabManualBtn.classList.remove("tabs__btn--active");
      panelFile?.classList.remove("panel--hidden");
      panelManual?.classList.add("panel--hidden");
      if (onTabChange) onTabChange("file");
    });

    tabManualBtn.addEventListener("click", () => {
      tabManualBtn.classList.add("tabs__btn--active");
      tabFileBtn.classList.remove("tabs__btn--active");
      panelManual?.classList.remove("panel--hidden");
      panelFile?.classList.add("panel--hidden");
      if (onTabChange) onTabChange("manual");
    });
  }

  // Navegación manual por sidebar
  const navItems = document.querySelectorAll(".sidebar__nav-item");
  navItems.forEach((btn) => {
    btn.addEventListener("click", () => {
      const view = btn.dataset.view;
      if (view) switchView(view);
    });
  });
}