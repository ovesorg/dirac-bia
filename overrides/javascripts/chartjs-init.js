/**
 * Chart.js Integration for MkDocs
 * Automatically renders canvas elements with data-chart attributes
 */

(function() {
    'use strict';

    // Wait for DOM and Chart.js to be ready
    function initCharts() {
        if (typeof Chart === 'undefined') {
            console.warn('Chart.js not loaded - skipping chart initialization');
            return;
        }

        // Find all canvas elements with data-chart attribute
        const chartElements = document.querySelectorAll('canvas[data-chart]');
        
        chartElements.forEach(canvas => {
            try {
                const chartConfig = JSON.parse(canvas.getAttribute('data-chart'));
                
                // Apply default options
                const options = {
                    responsive: true,
                    maintainAspectRatio: true,
                    ...chartConfig.options
                };

                // Create chart
                new Chart(canvas.getContext('2d'), {
                    type: chartConfig.type || 'line',
                    data: chartConfig.data,
                    options: options
                });

                console.log('Initialized chart:', canvas.id || 'unnamed');
            } catch (e) {
                console.error('Failed to initialize chart:', e, canvas);
            }
        });
    }

    // Initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initCharts);
    } else {
        initCharts();
    }

    // Re-initialize on navigation (for SPA-like behavior in Material theme)
    document.addEventListener('DOMContentSwitch', initCharts);
})();
