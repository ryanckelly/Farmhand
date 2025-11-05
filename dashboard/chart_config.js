/**
 * Terminal-themed Chart.js Configuration
 * Provides consistent styling for all charts in the Farmhand Dashboard
 */

const TERMINAL_COLORS = {
    background: '#1e1e1e',
    green: '#00ff00',
    gold: '#ffd700',
    red: '#ff3333',
    skills: {
        farming: '#00ff00',
        fishing: '#00ccff',
        foraging: '#33ff33',
        mining: '#ffff00',
        combat: '#ff6600'
    },
    relationship: '#ff1493'
};

/**
 * Base Chart.js configuration with terminal aesthetic
 */
const terminalChartDefaults = {
    responsive: true,
    maintainAspectRatio: true,
    plugins: {
        legend: {
            display: true,
            labels: {
                color: TERMINAL_COLORS.green,
                font: {
                    family: "'Courier New', 'Consolas', 'Monaco', monospace",
                    size: 12
                },
                padding: 15,
                usePointStyle: true
            }
        },
        tooltip: {
            enabled: true,
            backgroundColor: 'rgba(30, 30, 30, 0.9)',
            titleColor: TERMINAL_COLORS.gold,
            titleFont: {
                family: "'Courier New', 'Consolas', 'Monaco', monospace",
                size: 13,
                weight: 'bold'
            },
            bodyColor: TERMINAL_COLORS.green,
            bodyFont: {
                family: "'Courier New', 'Consolas', 'Monaco', monospace",
                size: 12
            },
            borderColor: TERMINAL_COLORS.green,
            borderWidth: 1,
            padding: 10,
            displayColors: true,
            callbacks: {
                title: function(context) {
                    return context[0].label || '';
                },
                label: function(context) {
                    let label = context.dataset.label || '';
                    if (label) {
                        label += ': ';
                    }
                    if (context.parsed.y !== null) {
                        label += new Intl.NumberFormat().format(context.parsed.y);
                    }
                    return label;
                }
            }
        }
    },
    scales: {
        x: {
            ticks: {
                color: TERMINAL_COLORS.green,
                font: {
                    family: "'Courier New', 'Consolas', 'Monaco', monospace",
                    size: 11
                }
            },
            grid: {
                color: 'rgba(0, 255, 0, 0.1)',
                drawBorder: true,
                borderColor: TERMINAL_COLORS.green,
                borderWidth: 1
            }
        },
        y: {
            ticks: {
                color: TERMINAL_COLORS.green,
                font: {
                    family: "'Courier New', 'Consolas', 'Monaco', monospace",
                    size: 11
                },
                callback: function(value) {
                    return new Intl.NumberFormat().format(value);
                }
            },
            grid: {
                color: 'rgba(0, 255, 0, 0.1)',
                drawBorder: true,
                borderColor: TERMINAL_COLORS.green,
                borderWidth: 1
            }
        }
    }
};

/**
 * Create terminal-styled bar chart config
 */
function createBarChartConfig(data, options = {}) {
    return {
        type: 'bar',
        data: data,
        options: {
            ...terminalChartDefaults,
            ...options,
            plugins: {
                ...terminalChartDefaults.plugins,
                ...(options.plugins || {}),
                title: {
                    display: options.title !== undefined,
                    text: options.title,
                    color: TERMINAL_COLORS.gold,
                    font: {
                        family: "'Courier New', 'Consolas', 'Monaco', monospace",
                        size: 16,
                        weight: 'bold'
                    },
                    padding: 20
                }
            }
        }
    };
}

/**
 * Create terminal-styled line chart config
 */
function createLineChartConfig(data, options = {}) {
    return {
        type: 'line',
        data: data,
        options: {
            ...terminalChartDefaults,
            ...options,
            elements: {
                line: {
                    tension: 0.3,
                    borderWidth: 2
                },
                point: {
                    radius: 4,
                    hoverRadius: 6,
                    hitRadius: 10
                }
            },
            plugins: {
                ...terminalChartDefaults.plugins,
                ...(options.plugins || {}),
                title: {
                    display: options.title !== undefined,
                    text: options.title,
                    color: TERMINAL_COLORS.gold,
                    font: {
                        family: "'Courier New', 'Consolas', 'Monaco', monospace",
                        size: 16,
                        weight: 'bold'
                    },
                    padding: 20
                }
            }
        }
    };
}

/**
 * Format large numbers with commas
 */
function formatNumber(num) {
    return new Intl.NumberFormat().format(Math.round(num));
}

/**
 * Generate session labels
 */
function generateSessionLabels(count) {
    return Array.from({ length: count }, (_, i) => `Session ${i}`);
}
