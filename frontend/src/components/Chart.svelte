<script lang="ts">
  import { onMount, onDestroy } from 'svelte';
  import {
    Chart,
    CategoryScale,
    LinearScale,
    PointElement,
    LineElement,
    LineController,
    Title,
    Tooltip,
    Legend,
    type ChartConfiguration
  } from 'chart.js';

  export let data: any;

  let chartCanvas: HTMLCanvasElement;
  let chartInstance: Chart | null = null;

  // Register Chart.js components
  Chart.register(
    CategoryScale,
    LinearScale,
    PointElement,
    LineElement,
    LineController,
    Title,
    Tooltip,
    Legend
  );

  onMount(() => {
    if (!chartCanvas || !data) return;

    const isDark = document.documentElement.classList.contains('dark');
    const textColor = isDark ? '#e5e7eb' : '#374151';
    const gridColor = isDark ? '#374151' : '#e5e7eb';

    const config: ChartConfiguration<'line'> = {
      type: 'line',
      data: {
        labels: data.data.labels || [],
        datasets: data.data.datasets.map((dataset, index) => ({
          label: dataset.label || `Dataset ${index + 1}`,
          data: dataset.data,
          borderColor: dataset.borderColor || 'rgb(59, 130, 246)',
          backgroundColor: dataset.backgroundColor || 'rgba(59, 130, 246, 0.1)',
          tension: 0.4,
          fill: true,
          pointRadius: 4,
          pointHoverRadius: 6,
        })),
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          title: {
            display: !!data.title,
            text: data.title || '',
            color: textColor,
            font: {
              size: 18,
              weight: 'bold',
            },
            padding: {
              top: 10,
              bottom: 20,
            },
          },
          legend: {
            display: true,
            position: 'top',
            labels: {
              color: textColor,
              usePointStyle: true,
              padding: 15,
            },
          },
          tooltip: {
            backgroundColor: isDark ? 'rgba(31, 41, 55, 0.95)' : 'rgba(255, 255, 255, 0.95)',
            titleColor: textColor,
            bodyColor: textColor,
            borderColor: gridColor,
            borderWidth: 1,
            padding: 12,
            displayColors: true,
          },
        },
        scales: {
          x: {
            display: true,
            title: {
              display: !!data.xLabel,
              text: data.xLabel || '',
              color: textColor,
              font: {
                size: 14,
                weight: '500',
              },
            },
            ticks: {
              color: textColor,
            },
            grid: {
              color: gridColor,
            },
          },
          y: {
            display: true,
            title: {
              display: !!data.yLabel,
              text: data.yLabel || '',
              color: textColor,
              font: {
                size: 14,
                weight: '500',
              },
            },
            ticks: {
              color: textColor,
            },
            grid: {
              color: gridColor,
            },
          },
        },
      },
    };

    chartInstance = new Chart(chartCanvas, config);

    // Watch for dark mode changes
    const observer = new MutationObserver(() => {
      if (chartInstance) {
        const isDarkNow = document.documentElement.classList.contains('dark');
        const newTextColor = isDarkNow ? '#e5e7eb' : '#374151';
        const newGridColor = isDarkNow ? '#374151' : '#e5e7eb';

        if (chartInstance.options.plugins) {
          if (chartInstance.options.plugins.title) {
            chartInstance.options.plugins.title.color = newTextColor;
          }
          if (chartInstance.options.plugins.legend) {
            chartInstance.options.plugins.legend.labels!.color = newTextColor;
          }
          if (chartInstance.options.plugins.tooltip) {
            chartInstance.options.plugins.tooltip.backgroundColor = isDarkNow
              ? 'rgba(31, 41, 55, 0.95)'
              : 'rgba(255, 255, 255, 0.95)';
            chartInstance.options.plugins.tooltip.titleColor = newTextColor;
            chartInstance.options.plugins.tooltip.bodyColor = newTextColor;
            chartInstance.options.plugins.tooltip.borderColor = newGridColor;
          }
        }

        if (chartInstance.options.scales) {
          if (chartInstance.options.scales.x) {
            chartInstance.options.scales.x.ticks!.color = newTextColor;
            chartInstance.options.scales.x.grid!.color = newGridColor;
            if (chartInstance.options.scales.x.title) {
              chartInstance.options.scales.x.title.color = newTextColor;
            }
          }
          if (chartInstance.options.scales.y) {
            chartInstance.options.scales.y.ticks!.color = newTextColor;
            chartInstance.options.scales.y.grid!.color = newGridColor;
            if (chartInstance.options.scales.y.title) {
              chartInstance.options.scales.y.title.color = newTextColor;
            }
          }
        }

        chartInstance.update();
      }
    });

    observer.observe(document.documentElement, {
      attributes: true,
      attributeFilter: ['class'],
    });

    return () => {
      observer.disconnect();
    };
  });

  onDestroy(() => {
    if (chartInstance) {
      chartInstance.destroy();
      chartInstance = null;
    }
  });
</script>

<div class="w-full h-full flex flex-col">
  {#if data && data.data && data.data.labels && data.data.labels.length > 0}
    <div class="flex-1 min-h-[400px]">
      <canvas bind:this={chartCanvas}></canvas>
    </div>
  {:else}
    <div class="flex items-center justify-center h-full text-gray-500 dark:text-gray-400">
      <p>No chart data available</p>
    </div>
  {/if}
</div>

