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

      // Icon Logic: 
      // Dark Mode -> Show SUN (to switch to light)
      // Light Mode -> Show MOON (to switch to dark)
      if (theme === 'dark') {
        // SUN ICON
        toggleBtn.innerHTML = `
            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <circle cx="12" cy="12" r="5"></circle>
                <line x1="12" y1="1" x2="12" y2="3"></line>
                <line x1="12" y1="21" x2="12" y2="23"></line>
                <line x1="4.22" y1="4.22" x2="5.64" y2="5.64"></line>
                <line x1="18.36" y1="18.36" x2="19.78" y2="19.78"></line>
                <line x1="1" y1="12" x2="3" y2="12"></line>
                <line x1="21" y1="12" x2="23" y2="12"></line>
                <line x1="4.22" y1="19.78" x2="5.64" y2="18.36"></line>
                <line x1="18.36" y1="5.64" x2="19.78" y2="4.22"></line>
            </svg>
          `;
      } else {
        // MOON ICON
        toggleBtn.innerHTML = `
            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
                <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/>
            </svg>
          `;
      }
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
