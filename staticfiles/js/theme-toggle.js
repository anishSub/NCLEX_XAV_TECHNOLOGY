/* =========================================
   Theme Toggle JavaScript
   ========================================= */

(function () {
  'use strict';

  console.log('🎨 Theme system loaded');

  // Initialize theme from localStorage or default to light
  function initTheme() {
    const savedTheme = localStorage.getItem('theme') || 'light';
    document.documentElement.setAttribute('data-theme', savedTheme);
    updateToggleButton(savedTheme);
    console.log(`✅ Theme initialized: ${savedTheme}`);
  }

  // Toggle between light and dark themes
  function toggleTheme() {
    const currentTheme = document.documentElement.getAttribute('data-theme');
    const newTheme = currentTheme === 'dark' ? 'light' : 'dark';

    document.documentElement.setAttribute('data-theme', newTheme);
    localStorage.setItem('theme', newTheme);
    updateToggleButton(newTheme);

    console.log(`🎨 Theme switched to: ${newTheme}`);

    // Update Chart.js charts if they exist
    updateCharts(newTheme);
  }

  // Update toggle button state
  function updateToggleButton(theme) {
    const toggleBtn = document.getElementById('theme-toggle-btn');
    if (toggleBtn) {
      toggleBtn.setAttribute('aria-label', `Switch to ${theme === 'dark' ? 'light' : 'dark'} mode`);
      toggleBtn.setAttribute('title', `Switch to ${theme === 'dark' ? 'light' : 'dark'} mode`);
    }
  }

  // Update Chart.js charts with theme-appropriate colors
  function updateCharts(theme) {
    if (typeof Chart !== 'undefined' && Chart.instances) {
      const isDark = theme === 'dark';
      const gridColor = isDark ? '#404040' : '#e0e0e0';
      const textColor = isDark ? '#b0b0b0' : '#666666';

      Object.values(Chart.instances).forEach(chart => {
        // Update grid colors
        if (chart.options.scales) {
          Object.values(chart.options.scales).forEach(scale => {
            if (scale.grid) {
              scale.grid.color = gridColor;
            }
            if (scale.ticks) {
              scale.ticks.color = textColor;
            }
            if (scale.title) {
              scale.title.color = textColor;
            }
          });
        }

        // Update legend
        if (chart.options.plugins && chart.options.plugins.legend) {
          chart.options.plugins.legend.labels = chart.options.plugins.legend.labels || {};
          chart.options.plugins.legend.labels.color = textColor;
        }

        // Re-render chart
        chart.update();
      });

      console.log('📊 Charts updated for theme');
    }
  }

  // Set up event listeners
  function setupEventListeners() {
    // Toggle button click
    const toggleBtn = document.getElementById('theme-toggle-btn');
    if (toggleBtn) {
      toggleBtn.addEventListener('click', toggleTheme);
    }

    // Keyboard shortcut: Alt + T
    document.addEventListener('keydown', function (e) {
      if (e.altKey && e.key === 't') {
        e.preventDefault();
        toggleTheme();
      }
    });
  }

  // Initialize on DOM ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', function () {
      initTheme();
      setupEventListeners();
    });
  } else {
    initTheme();
    setupEventListeners();
  }

  // Expose toggle function globally
  window.toggleTheme = toggleTheme;

})();
