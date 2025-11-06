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
let xAxisMode = 'sessions'; // 'sessions' or 'dates'

// Wait for DOM and diary data to be loaded
document.addEventListener('DOMContentLoaded', function() {
    if (typeof diaryData === 'undefined') {
        console.error('Diary data not loaded!');
        return;
    }

    initializeCharts(diaryData);
    setupSessionFilter();
    setupXAxisToggle();
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
    initRelationshipChart(fullChartData, selectedVillager || 'Abigail');
    initBundlesChart(fullChartData);
    initCumulativeMoneyChart(fullChartData);
}

/**
 * Extract and transform data for charts
 */
function extractChartData(entries) {
    const data = {
        sessionLabels: [],
        dateLabels: [],
        moneyChanges: [],
        farmingXP: [],
        fishingXP: [],
        foragingXP: [],
        miningXP: [],
        combatXP: [],
        totalXP: [],
        bundlesCompleted: [],
        cumulativeBundles: [],
        villagerHearts: {},  // Dynamic: stores hearts for all villagers
        cumulativeMoney: []
    };

    // Initialize villager hearts tracking for all villagers
    if (typeof villagersData !== 'undefined') {
        villagersData.forEach(villager => {
            data.villagerHearts[villager.name] = [];
        });
    }

    let cumulativeBundles = 0;
    let cumulativeMoney = entries[0].financial.starting_money || 0;

    entries.forEach((entry, index) => {
        // Extract in-game date (e.g., "Spring 3, Year 1" -> "Spring 3")
        let gameDate = `Session ${index}`;
        if (entry.game_progress?.end) {
            // Remove the year portion for brevity (e.g., "Winter 7, Year 2" -> "Winter 7")
            gameDate = entry.game_progress.end.replace(/, Year \d+/, '');
        }
        data.sessionLabels.push(gameDate);

        // Extract real-world date from detected_at timestamp
        let dateLabel = `Session ${index}`;
        if (entry.detected_at) {
            const date = new Date(entry.detected_at);
            // Format as "Nov 1" for brevity
            dateLabel = date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
        }
        data.dateLabels.push(dateLabel);

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

        // Track hearts for ALL villagers
        const friendships = entry.changes_detail?.friendship_changes || {};

        // Update each villager's hearts (carry forward previous value if no change)
        for (const villagerName in data.villagerHearts) {
            const previousHearts = data.villagerHearts[villagerName].length > 0
                ? data.villagerHearts[villagerName][data.villagerHearts[villagerName].length - 1]
                : 0;

            const newHearts = friendships[villagerName]?.new_hearts ?? previousHearts;
            data.villagerHearts[villagerName].push(newHearts);
        }
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
 * Initialize Relationship Chart (Dynamic Villager)
 */
function initRelationshipChart(chartData, villagerName = 'Abigail') {
    const ctx = document.getElementById('relationshipChart');
    if (!ctx) return;

    // Get villager data
    const villagerHearts = chartData.villagerHearts[villagerName] || [];
    const villagerData = villagersData?.find(v => v.name === villagerName);
    const villagerColor = villagerData?.color || TERMINAL_COLORS.relationship;

    const config = createLineChartConfig({
        labels: chartData.sessionLabels,
        datasets: [{
            label: `${villagerName} Hearts`,
            data: villagerHearts,
            backgroundColor: `${villagerColor}33`,  // 20% opacity
            borderColor: villagerColor,
            borderWidth: 3,
            fill: true,
            pointBackgroundColor: villagerColor,
            pointBorderColor: TERMINAL_COLORS.gold,
            pointBorderWidth: 2,
            pointRadius: 5,
            tension: 0.4
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
        dateLabels: fullChartData.dateLabels.slice(startIndex),
        moneyChanges: fullChartData.moneyChanges.slice(startIndex),
        farmingXP: fullChartData.farmingXP.slice(startIndex),
        fishingXP: fullChartData.fishingXP.slice(startIndex),
        foragingXP: fullChartData.foragingXP.slice(startIndex),
        miningXP: fullChartData.miningXP.slice(startIndex),
        combatXP: fullChartData.combatXP.slice(startIndex),
        totalXP: fullChartData.totalXP.slice(startIndex),
        bundlesCompleted: fullChartData.bundlesCompleted.slice(startIndex),
        cumulativeBundles: fullChartData.cumulativeBundles.slice(startIndex),
        villagerHearts: {},
        cumulativeMoney: fullChartData.cumulativeMoney.slice(startIndex)
    };

    // Slice villager hearts for all villagers
    for (const villagerName in fullChartData.villagerHearts) {
        filteredData.villagerHearts[villagerName] = fullChartData.villagerHearts[villagerName].slice(startIndex);
    }

    // Update each chart
    updateMoneyChart(filteredData);
    updateXPBySkillChart(filteredData);
    updateTotalXPChart(filteredData);
    updateRelationshipChart(filteredData); // Will use selectedVillager if available
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

    chartInstances.money.data.labels = getCurrentLabels(chartData);
    chartInstances.money.data.datasets[0].data = chartData.moneyChanges;
    chartInstances.money.data.datasets[0].backgroundColor = colors;
    chartInstances.money.data.datasets[0].borderColor = colors.map(c =>
        c === TERMINAL_COLORS.green ? TERMINAL_COLORS.gold : TERMINAL_COLORS.red
    );
    chartInstances.money.update();
}

function updateXPBySkillChart(chartData) {
    if (!chartInstances.xpBySkill) return;

    chartInstances.xpBySkill.data.labels = getCurrentLabels(chartData);
    chartInstances.xpBySkill.data.datasets[0].data = chartData.farmingXP;
    chartInstances.xpBySkill.data.datasets[1].data = chartData.fishingXP;
    chartInstances.xpBySkill.data.datasets[2].data = chartData.foragingXP;
    chartInstances.xpBySkill.data.datasets[3].data = chartData.miningXP;
    chartInstances.xpBySkill.data.datasets[4].data = chartData.combatXP;
    chartInstances.xpBySkill.update();
}

function updateTotalXPChart(chartData) {
    if (!chartInstances.totalXP) return;

    chartInstances.totalXP.data.labels = getCurrentLabels(chartData);
    chartInstances.totalXP.data.datasets[0].data = chartData.totalXP;
    chartInstances.totalXP.update();
}

function updateRelationshipChart(chartData, villagerName) {
    if (!chartInstances.relationship) return;

    // If villagerName not provided, use currently selected villager
    if (!villagerName && typeof selectedVillager !== 'undefined') {
        villagerName = selectedVillager;
    }
    if (!villagerName) villagerName = 'Abigail';

    // Get villager data
    const villagerHearts = chartData.villagerHearts[villagerName] || [];
    const villagerData = villagersData?.find(v => v.name === villagerName);
    const villagerColor = villagerData?.color || TERMINAL_COLORS.relationship;

    chartInstances.relationship.data.labels = getCurrentLabels(chartData);
    chartInstances.relationship.data.datasets[0].label = `${villagerName} Hearts`;
    chartInstances.relationship.data.datasets[0].data = villagerHearts;
    chartInstances.relationship.data.datasets[0].borderColor = villagerColor;
    chartInstances.relationship.data.datasets[0].backgroundColor = `${villagerColor}33`;
    chartInstances.relationship.data.datasets[0].pointBackgroundColor = villagerColor;
    chartInstances.relationship.update();
}

function updateBundlesChart(chartData) {
    if (!chartInstances.bundles) return;

    chartInstances.bundles.data.labels = getCurrentLabels(chartData);
    chartInstances.bundles.data.datasets[0].data = chartData.bundlesCompleted;
    chartInstances.bundles.data.datasets[1].data = chartData.cumulativeBundles;
    chartInstances.bundles.update();
}

function updateCumulativeMoneyChart(chartData) {
    if (!chartInstances.cumulativeMoney) return;

    chartInstances.cumulativeMoney.data.labels = getCurrentLabels(chartData);
    chartInstances.cumulativeMoney.data.datasets[0].data = chartData.cumulativeMoney;
    chartInstances.cumulativeMoney.update();
}

/**
 * Get current labels based on x-axis mode
 */
function getCurrentLabels(chartData) {
    return xAxisMode === 'dates' ? chartData.dateLabels : chartData.sessionLabels;
}

/**
 * Setup x-axis toggle button
 */
function setupXAxisToggle() {
    const toggleButton = document.getElementById('xAxisToggle');
    if (!toggleButton) return;

    toggleButton.addEventListener('click', function() {
        // Toggle mode
        xAxisMode = xAxisMode === 'sessions' ? 'dates' : 'sessions';

        // Update button text
        if (xAxisMode === 'dates') {
            toggleButton.textContent = 'X-Axis: Real Dates';
            toggleButton.classList.add('active');
        } else {
            toggleButton.textContent = 'X-Axis: Game Dates';
            toggleButton.classList.remove('active');
        }

        // Get current filter value
        const filterInput = document.getElementById('sessionFilter');
        const sessionCount = filterInput ? parseInt(filterInput.value) : maxSessions;

        // Re-filter charts with new labels
        filterCharts(sessionCount >= maxSessions ? maxSessions : sessionCount);
    });
}

/**
 * Global function to refresh relationship chart (called from villager chip click)
 */
window.refreshRelationshipChart = function(villagerName) {
    // Get current filter value
    const filterInput = document.getElementById('sessionFilter');
    const sessionCount = filterInput ? parseInt(filterInput.value) : maxSessions;

    // If showing all sessions, use full data
    if (sessionCount >= maxSessions && fullChartData) {
        updateRelationshipChart(fullChartData, villagerName);
    } else {
        // Re-filter with new villager
        const totalSessions = fullChartData.sessionLabels.length;
        const startIndex = Math.max(0, totalSessions - sessionCount);

        const filteredData = {
            sessionLabels: fullChartData.sessionLabels.slice(startIndex),
            dateLabels: fullChartData.dateLabels.slice(startIndex),
            villagerHearts: {}
        };

        // Slice villager hearts
        for (const vName in fullChartData.villagerHearts) {
            filteredData.villagerHearts[vName] = fullChartData.villagerHearts[vName].slice(startIndex);
        }

        updateRelationshipChart(filteredData, villagerName);
    }
};
