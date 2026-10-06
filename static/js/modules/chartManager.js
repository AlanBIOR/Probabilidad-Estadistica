let chartInstance = null;

export function renderDistributionChart(canvasElement, chartData, isDark) {
  const ctx = canvasElement.getContext("2d");
  if (chartInstance) chartInstance.destroy();

  const primaryBar = isDark ? "#1d3b6c" : "#a6bff9";
  const meanBarColor = isDark ? "#8cb7fc" : "#3d63dd"; // Color de acento para la barra de la Media
  const curveColor = isDark ? "#d3e2fc" : "#1d2e5c";
  const textColor = isDark ? "#b4b3b7" : "#62636c";
  const gridColor = isDark ? "#27487d22" : "#cdced744";

  // Pintar de color destacado el contenedor donde cae la media
  const barColors = chartData.counts.map((_, idx) =>
    idx === chartData.mean_bin_index ? meanBarColor : primaryBar
  );

  const datasets = [
    {
      type: "bar",
      label: "Frecuencia de datos",
      data: chartData.counts,
      backgroundColor: barColors,
      borderRadius: 4,
      order: 2,
    },
  ];

  if (chartData.curve && chartData.curve.length) {
    datasets.push({
      type: "line",
      label: "Curva estimada de distribución",
      data: chartData.curve,
      borderColor: curveColor,
      borderWidth: 2.5,
      pointRadius: 0,
      tension: 0.35,
      order: 1,
    });
  }

  chartInstance = new Chart(ctx, {
    data: {
      labels: chartData.labels,
      datasets: datasets,
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          labels: { color: textColor },
        },
        tooltip: {
          callbacks: {
            title: (items) => `Intervalo: ${items[0].label}`,
            afterBody: () => [
              `-----------------------`,
              `Media: ${chartData.mean_value}`,
              `Mediana: ${chartData.median_value}`,
              `Asimetría: ${chartData.skewness}`,
            ],
          },
        },
      },
      scales: {
        x: {
          ticks: { color: textColor, maxRotation: 45, minRotation: 0 },
          grid: { display: false },
        },
        y: {
          ticks: { color: textColor },
          grid: { color: gridColor },
        },
      },
    },
  });
}

export function updateChartTheme(isDark) {
  if (chartInstance) {
    chartInstance.update();
  }
}