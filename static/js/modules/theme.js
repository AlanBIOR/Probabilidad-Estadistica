export function initTheme(onThemeChange) {
  const themeToggle = document.getElementById("themeToggle");

  themeToggle.addEventListener("click", () => {
    const isDark = document.documentElement.getAttribute("data-theme") === "dark";
    const nextTheme = isDark ? "light" : "dark";
    document.documentElement.setAttribute("data-theme", nextTheme);

    if (typeof onThemeChange === "function") {
      onThemeChange(!isDark);
    }
  });
}