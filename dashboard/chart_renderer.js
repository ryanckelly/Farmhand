/**
 * Chart Renderer for Farmhand Dashboard
 * Initializes all Chart.js charts with diary data
 */

// Global chart instances
const chartInstances = {
    money: null,
    xpBySkill: null,
    totalXP: null,
    relationship: null,
    bundles: null,
    cumulativeMoney: null
};

// Global data storage
let fullChartData = null;
let maxSessions = 0;

// Wait for DOM and diary data to be loaded
document.addEventListener('DOMContentLoaded', function() {
    if (typeof diaryData === 'undefined') {
        console.error('Diary data not loaded!');
        return;
    }

    initializeCharts(diaryData);
    setupSessionFilter();
});

/**
 * Initialize all charts from diary data
 */
function initializeCharts(diary) {
    const entries = diary.entries || [];

    if (entries.length === 0) {
        console.warn('No diary entries found');
        return;
    }

    // Extract data from diary entries
    fullChartData = extractChartData(entries);
    maxSessions = entries.length;

    // Update filter max value
    const filterInput = document.getElementById('sessionFilter');
    if (filterInput) {
        filterInput.max = maxSessions;
        filterInput.value = maxSessions;
    }

    // Initialize each chart with full data
    initMoneyChart(fullChartData);
    initXPBySkillChart(fullChartData);
    initTotalXPChart(fullChartData);
    initRelationshipChart(fullChartData);
    initBundlesChart(fullChartData);
    initCumulativeMoneyChart(fullChartData);
}

/**
 * Extract and transform data for charts
 */
function extractChartData(entries) {
    const data = {
        sessionLabels: [],
        moneyChanges: [],
        farmingXP: [],
        fishingXP: [],
        foragingXP: [],
        miningXP: [],
        combatXP: [],
        totalXP: [],
        bundlesCompleted: [],
        cumulativeBundles: [],
        abigailHearts: [],
        cumulativeMoney: []
    };

    let cumulativeBundles = 0;
    let cumulativeMoney = entries[0].financial.starting_money || 0;

    entries.forEach((entry, index) => {
        data.sessionLabels.push(index.toString());

        // Money
        const moneyChange = entry.financial.change || 0;
        data.moneyChanges.push(moneyChange);
        cumulativeMoney += moneyChange;
        data.cumulativeMoney.push(cumulativeMoney);

        // Skills
        const skills = entry.changes_detail?.skill_changes || {};
        data.farmingXP.push(skills.farming?.xp_gained || 0);
        data.fishingXP.push(skills.fishing?.xp_gained || 0);
        data.foragingXP.push(skills.foraging?.xp_gained || 0);
        data.miningXP.push(skills.mining?.xp_gained || 0);
        data.combatXP.push(skills.combat?.xp_gained || 0);

        // Total XP
        const totalXP = (skills.farming?.xp_gained || 0) +
                       (skills.fishing?.xp_gained || 0) +
                       (skills.foraging?.xp_gained || 0) +
                       (skills.mining?.xp_gained || 0) +
                       (skills.combat?.xp_gained || 0);
        data.totalXP.push(totalXP);

        // Bundles
        const bundles = entry.changes_detail?.bundles_completed || 0;
        data.bundlesCompleted.push(bundles);
        cumulativeBundles += bundles;
        data.cumulativeBundles.push(cumulativeBundles);

        // Abigail hearts
        const friendships = entry.changes_detail?.friendship_changes || {};
        const abigailHearts = friendships.Abigail?.new_hearts ||
                            (data.abigailHearts.length > 0 ? data.abigailHearts[data.abigailHearts.length - 1] : 0);
        data.abigailHearts.push(abigailHearts);
    });

    return data;
}

/**
 * Initialize Money Change Chart
 */
function initMoneyChart(chartData) {
    const ctx = document.getElementById('moneyChart');
    if (!ctx) return;

    const colors = chartData.moneyChanges.map(v =>
        v >= 0 ? TERMINAL_COLORS.green : TERMINAL_COLORS.red
    );

    const config = createBarChartConfig({
        labels: chartData.sessionLabels,
        datasets: [{
            label: 'Net Money Change (g)',
            data: chartData.moneyChanges,
            backgroundColor: colors,
            borderColor: colors.map(c => c === TERMINAL_COLORS.green ? TERMINAL_COLORS.gold : TERMINAL_COLORS.red),
            borderWidth: 1
        }]
    }, {
        plugins: {
            legend: { display: false }
        }
    });

    chartInstances.money = new Chart(ctx, config);
}

/**
 * Initialize XP by Skill Chart (Stacked)
 */
function initXPBySkillChart(chartData) {
    const ctx = document.getElementById('xpBySkillChart');
    if (!ctx) return;

    const config = {
        type: 'bar',
        data: {
            labels: chartData.sessionLabels,
            datasets: [
                {
                    label: 'Farming',
                    data: chartData.farmingXP,
                    backgroundColor: TERMINAL_COLORS.skills.farming,
                    borderColor: TERMINAL_COLORS.green,
                    borderWidth: 0
                },
                {
                    label: 'Fishing',
                    data: chartData.fishingXP,
                    backgroundColor: TERMINAL_COLORS.skills.fishing,
                    borderColor: TERMINAL_COLORS.green,
                    borderWidth: 0
                },
                {
                    label: 'Foraging',
                    data: chartData.foragingXP,
                    backgroundColor: TERMINAL_COLORS.skills.foraging,
                    borderColor: TERMINAL_COLORS.green,
                    borderWidth: 0
                },
                {
                    label: 'Mining',
                    data: chartData.miningXP,
                    backgroundColor: TERMINAL_COLORS.skills.mining,
                    borderColor: TERMINAL_COLORS.green,
                    borderWidth: 0
                },
                {
                    label: 'Combat',
                    data: chartData.combatXP,
                    backgroundColor: TERMINAL_COLORS.skills.combat,
                    borderColor: TERMINAL_COLORS.green,
                    borderWidth: 0
                }
            ]
        },
        options: {
            ...terminalChartDefaults,
            scales: {
                x: {
                    stacked: true,
                    ticks: {
                        color: TERMINAL_COLORS.green,
                        font: { family: "'Courier New', monospace", size: 11 }
                    },
                    grid: {
                        color: 'rgba(0, 255, 0, 0.1)',
                        borderColor: TERMINAL_COLORS.green
                    }
                },
                y: {
                    stacked: true,
                    ticks: {
                        color: TERMINAL_COLORS.green,
                        font: { family: "'Courier New', monospace", size: 11 }
                    },
                    grid: {
                        color: 'rgba(0, 255, 0, 0.1)',
                        borderColor: TERMINAL_COLORS.green
                    }
                }
            }
        }
    };

    chartInstances.xpBySkill = new Chart(ctx, config);
}

/**
 * Initialize Total XP Chart
 */
function initTotalXPChart(chartData) {
    const ctx = document.getElementById('totalXPChart');
    if (!ctx) return;

    const average = chartData.totalXP.reduce((a, b) => a + b, 0) / chartData.totalXP.length;

    const config = createLineChartConfig({
        labels: chartData.sessionLabels,
        datasets: [{
            label: 'Total XP',
            data: chartData.totalXP,
            backgroundColor: 'rgba(0, 255, 0, 0.2)',
            borderColor: TERMINAL_COLORS.green,
            borderWidth: 2,
            fill: true,
            pointBackgroundColor: TERMINAL_COLORS.green,
            pointBorderColor: TERMINAL_COLORS.gold,
            pointBorderWidth: 2
        }]
    }, {
        plugins: {
            annotation: {
                annotations: {
                    line1: {
                        type: 'line',
                        yMin: average,
                        yMax: average,
                        borderColor: TERMINAL_COLORS.gold,
                        borderWidth: 2,
                        borderDash: [5, 5],
                        label: {
                            content: `Average: ${Math.round(average)} XP`,
                            display: true,
                            color: TERMINAL_COLORS.gold,
                            font: { family: "'Courier New', monospace", size: 10 }
                        }
                    }
                }
            }
        }
    });

    chartInstances.totalXP = new Chart(ctx, config);
}

/**
 * Initialize Relationship Chart (Abigail)
 */
function initRelationshipChart(chartData) {
    const ctx = document.getElementById('relationshipChart');
    if (!ctx) return;

    const config = createLineChartConfig({
        labels: chartData.sessionLabels,
        datasets: [{
            label: 'Abigail Hearts',
            data: chartData.abigailHearts,
            backgroundColor: 'transparent',
            borderColor: TERMINAL_COLORS.relationship,
            borderWidth: 3,
            fill: false,
            pointBackgroundColor: TERMINAL_COLORS.relationship,
            pointBorderColor: TERMINAL_COLORS.gold,
            pointBorderWidth: 2,
            pointRadius: 5
        }]
    }, {
        scales: {
            y: {
                ...terminalChartDefaults.scales.y,
                min: 0,
                max: 14,
                ticks: {
                    ...terminalChartDefaults.scales.y.ticks,
                    stepSize: 2
                }
            }
        }
    });

    chartInstances.relationship = new Chart(ctx, config);
}

/**
 * Initialize Bundles Chart
 */
function initBundlesChart(chartData) {
    const ctx = document.getElementById('bundlesChart');
    if (!ctx) return;

    const config = {
        type: 'bar',
        data: {
            labels: chartData.sessionLabels,
            datasets: [
                {
                    label: 'Per Session',
                    data: chartData.bundlesCompleted,
                    backgroundColor: TERMINAL_COLORS.green,
                    borderColor: TERMINAL_COLORS.gold,
                    borderWidth: 1,
                    order: 2
                },
                {
                    label: 'Cumulative',
                    data: chartData.cumulativeBundles,
                    type: 'line',
                    borderColor: TERMINAL_COLORS.gold,
                    backgroundColor: 'transparent',
                    borderWidth: 2,
                    pointBackgroundColor: TERMINAL_COLORS.gold,
                    pointBorderColor: TERMINAL_COLORS.green,
                    pointBorderWidth: 2,
                    order: 1
                }
            ]
        },
        options: terminalChartDefaults
    };

    chartInstances.bundles = new Chart(ctx, config);
}

/**
 * Initialize Cumulative Money Chart
 */
function initCumulativeMoneyChart(chartData) {
    const ctx = document.getElementById('cumulativeMoneyChart');
    if (!ctx) return;

    const config = createLineChartConfig({
        labels: chartData.sessionLabels,
        datasets: [{
            label: 'Total Money',
            data: chartData.cumulativeMoney,
            backgroundColor: 'rgba(255, 215, 0, 0.2)',
            borderColor: TERMINAL_COLORS.gold,
            borderWidth: 2,
            fill: true,
            pointBackgroundColor: TERMINAL_COLORS.gold,
            pointBorderColor: TERMINAL_COLORS.green,
            pointBorderWidth: 2
        }]
    }, {
        plugins: {
            tooltip: {
                ...terminalChartDefaults.plugins.tooltip,
                callbacks: {
                    label: function(context) {
                        return 'Total: ' + formatNumber(context.parsed.y) + 'g';
                    }
                }
            }
        }
    });

    chartInstances.cumulativeMoney = new Chart(ctx, config);
}

/**
 * Setup session filter controls
 */
function setupSessionFilter() {
    const filterInput = document.getElementById('sessionFilter');
    const sessionCount = document.getElementById('sessionCount');
    const resetButton = document.getElementById('resetFilter');

    if (!filterInput || !sessionCount) return;

    // Update display when slider moves
    filterInput.addEventListener('input', function() {
        const value = parseInt(this.value);
        if (value >= maxSessions) {
            sessionCount.textContent = 'All';
        } else {
            sessionCount.textContent = value;
        }
    });

    // Apply filter when slider is released
    filterInput.addEventListener('change', function() {
        const value = parseInt(this.value);
        filterCharts(value >= maxSessions ? maxSessions : value);
    });

    // Reset button
    if (resetButton) {
        resetButton.addEventListener('click', function() {
            filterInput.value = maxSessions;
            sessionCount.textContent = 'All';
            filterCharts(maxSessions);
        });
    }
}

/**
 * Filter all charts to show only N most recent sessions
 */
function filterCharts(sessionCount) {
    if (!fullChartData) return;

    // Calculate starting index (show most recent N sessions)
    const totalSessions = fullChartData.sessionLabels.length;
    const startIndex = Math.max(0, totalSessions - sessionCount);

    // Create filtered data
    const filteredData = {
        sessionLabels: fullChartData.sessionLabels.slice(startIndex),
        moneyChanges: fullChartData.moneyChanges.slice(startIndex),
        farmingXP: fullChartData.farmingXP.slice(startIndex),
        fishingXP: fullChartData.fishingXP.slice(startIndex),
        foragingXP: fullChartData.foragingXP.slice(startIndex),
        miningXP: fullChartData.miningXP.slice(startIndex),
        combatXP: fullChartData.combatXP.slice(startIndex),
        totalXP: fullChartData.totalXP.slice(startIndex),
        bundlesCompleted: fullChartData.bundlesCompleted.slice(startIndex),
        cumulativeBundles: fullChartData.cumulativeBundles.slice(startIndex),
        abigailHearts: fullChartData.abigailHearts.slice(startIndex),
        cumulativeMoney: fullChartData.cumulativeMoney.slice(startIndex)
    };

    // Update each chart
    updateMoneyChart(filteredData);
    updateXPBySkillChart(filteredData);
    updateTotalXPChart(filteredData);
    updateRelationshipChart(filteredData);
    updateBundlesChart(filteredData);
    updateCumulativeMoneyChart(filteredData);
}

/**
 * Update individual charts with filtered data
 */
function updateMoneyChart(chartData) {
    if (!chartInstances.money) return;

    const colors = chartData.moneyChanges.map(v =>
        v >= 0 ? TERMINAL_COLORS.green : TERMINAL_COLORS.red
    );

    chartInstances.money.data.labels = chartData.sessionLabels;
    chartInstances.money.data.datasets[0].data = chartData.moneyChanges;
    chartInstances.money.data.datasets[0].backgroundColor = colors;
    chartInstances.money.data.datasets[0].borderColor = colors.map(c =>
        c === TERMINAL_COLORS.green ? TERMINAL_COLORS.gold : TERMINAL_COLORS.red
    );
    chartInstances.money.update();
}

function updateXPBySkillChart(chartData) {
    if (!chartInstances.xpBySkill) return;

    chartInstances.xpBySkill.data.labels = chartData.sessionLabels;
    chartInstances.xpBySkill.data.datasets[0].data = chartData.farmingXP;
    chartInstances.xpBySkill.data.datasets[1].data = chartData.fishingXP;
    chartInstances.xpBySkill.data.datasets[2].data = chartData.foragingXP;
    chartInstances.xpBySkill.data.datasets[3].data = chartData.miningXP;
    chartInstances.xpBySkill.data.datasets[4].data = chartData.combatXP;
    chartInstances.xpBySkill.update();
}

function updateTotalXPChart(chartData) {
    if (!chartInstances.totalXP) return;

    chartInstances.totalXP.data.labels = chartData.sessionLabels;
    chartInstances.totalXP.data.datasets[0].data = chartData.totalXP;
    chartInstances.totalXP.update();
}

function updateRelationshipChart(chartData) {
    if (!chartInstances.relationship) return;

    chartInstances.relationship.data.labels = chartData.sessionLabels;
    chartInstances.relationship.data.datasets[0].data = chartData.abigailHearts;
    chartInstances.relationship.update();
}

function updateBundlesChart(chartData) {
    if (!chartInstances.bundles) return;

    chartInstances.bundles.data.labels = chartData.sessionLabels;
    chartInstances.bundles.data.datasets[0].data = chartData.bundlesCompleted;
    chartInstances.bundles.data.datasets[1].data = chartData.cumulativeBundles;
    chartInstances.bundles.update();
}

function updateCumulativeMoneyChart(chartData) {
    if (!chartInstances.cumulativeMoney) return;

    chartInstances.cumulativeMoney.data.labels = chartData.sessionLabels;
    chartInstances.cumulativeMoney.data.datasets[0].data = chartData.cumulativeMoney;
    chartInstances.cumulativeMoney.update();
}
