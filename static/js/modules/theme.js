export function initTheme(onThemeChange) {
  const toggleBtn = document.getElementById("themeToggle");
  const storedTheme = localStorage.getItem("data-theme") || "dark";

  document.documentElement.setAttribute("data-theme", storedTheme);
  if (onThemeChange) onThemeChange(storedTheme === "dark");

  if (!toggleBtn) return;

  toggleBtn.addEventListener("click", () => {
    const currentTheme = document.documentElement.getAttribute("data-theme");
    const newTheme = currentTheme === "dark" ? "light" : "dark";

    document.documentElement.setAttribute("data-theme", newTheme);
    localStorage.setItem("data-theme", newTheme);

    if (onThemeChange) onThemeChange(newTheme === "dark");
  });
}