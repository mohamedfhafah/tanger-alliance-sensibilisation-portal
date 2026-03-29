function readDashboardCssVariable(name, fallback) {
    const value = getComputedStyle(document.documentElement).getPropertyValue(name).trim();
    return value || fallback;
}

function getDashboardTheme() {
    return {
        primary: readDashboardCssVariable('--color-primary', '#38bdf8'),
        secondary: readDashboardCssVariable('--color-secondary', '#2dd4bf'),
        accent: readDashboardCssVariable('--color-accent', '#f59e0b'),
        success: readDashboardCssVariable('--color-success', '#22c55e'),
        warning: readDashboardCssVariable('--color-warning', '#f59e0b'),
        danger: readDashboardCssVariable('--color-danger', '#fb7185'),
        text: readDashboardCssVariable('--color-text', '#f5fbff'),
        muted: readDashboardCssVariable('--color-text-muted', '#96a8c4'),
        faint: readDashboardCssVariable('--color-text-faint', '#70819d'),
        border: readDashboardCssVariable('--color-border', 'rgba(148, 163, 184, 0.18)'),
        surface: readDashboardCssVariable('--color-surface-strong', '#122443'),
        elevated: readDashboardCssVariable('--color-surface-elevated', '#183056')
    };
}

function createLinearGradient(context, startColor, endColor, horizontal) {
    const width = context.canvas?.width || 400;
    const height = context.canvas?.height || 300;
    const gradient = horizontal
        ? context.createLinearGradient(0, 0, width, 0)
        : context.createLinearGradient(0, 0, 0, height);

    gradient.addColorStop(0, startColor);
    gradient.addColorStop(1, endColor);
    return gradient;
}

function applyDashboardChartDefaults(theme) {
    Chart.defaults.font.family = "'Inter', 'Segoe UI', sans-serif";
    Chart.defaults.font.size = 13;
    Chart.defaults.color = theme.muted;
    Chart.defaults.borderColor = theme.border;
    Chart.defaults.animation.duration = 900;
    Chart.defaults.animation.easing = 'easeOutCubic';
}

function destroyDashboardCharts() {
    if (!window.tangerDashboardCharts) {
        return;
    }

    Object.values(window.tangerDashboardCharts).forEach((chart) => {
        if (chart && typeof chart.destroy === 'function') {
            chart.destroy();
        }
    });

    window.tangerDashboardCharts = {};
}

function buildModuleCompletionChart(theme) {
    const canvas = document.getElementById('moduleCompletionChart');
    const labels = window.moduleChartLabels;
    const scores = window.moduleChartData;
    const completion = window.moduleChartCompletionStatus;

    if (!canvas || !Array.isArray(labels) || !Array.isArray(scores) || !Array.isArray(completion)) {
        return null;
    }

    const context = canvas.getContext('2d');
    const scoreGradient = createLinearGradient(
        context,
        `${theme.primary}dd`,
        `${theme.secondary}aa`,
        false
    );

    return new Chart(context, {
        type: 'bar',
        data: {
            labels,
            datasets: [
                {
                    label: 'Score (%)',
                    data: scores,
                    backgroundColor: scoreGradient,
                    borderRadius: 12,
                    borderSkipped: false,
                    maxBarThickness: 44
                },
                {
                    label: 'Complété',
                    data: completion,
                    type: 'line',
                    yAxisID: 'y1',
                    borderColor: theme.accent,
                    backgroundColor: theme.accent,
                    pointBackgroundColor: completion.map((value) => value === 1 ? theme.success : theme.faint),
                    pointBorderColor: theme.surface,
                    pointBorderWidth: 2,
                    pointRadius: 5,
                    pointHoverRadius: 7,
                    borderWidth: 2,
                    tension: 0.28
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            interaction: {
                intersect: false,
                mode: 'index'
            },
            plugins: {
                legend: {
                    position: 'top',
                    labels: {
                        color: theme.muted,
                        usePointStyle: true,
                        boxWidth: 10,
                        padding: 18
                    }
                },
                tooltip: {
                    backgroundColor: theme.elevated,
                    titleColor: theme.text,
                    bodyColor: theme.text,
                    borderColor: theme.border,
                    borderWidth: 1,
                    cornerRadius: 14,
                    padding: 12,
                    callbacks: {
                        label(context) {
                            if (context.dataset.label === 'Complété') {
                                return `Complété: ${context.raw === 1 ? 'Oui' : 'Non'}`;
                            }
                            return `Score: ${Math.round((context.raw || 0) * 10) / 10}%`;
                        }
                    }
                }
            },
            scales: {
                x: {
                    grid: {
                        display: false
                    },
                    ticks: {
                        color: theme.faint,
                        maxRotation: 24,
                        minRotation: 0,
                        font: {
                            size: 11
                        }
                    }
                },
                y: {
                    beginAtZero: true,
                    suggestedMax: 100,
                    ticks: {
                        color: theme.faint,
                        stepSize: 20
                    },
                    title: {
                        display: true,
                        text: 'Score (%)',
                        color: theme.muted
                    }
                },
                y1: {
                    position: 'right',
                    beginAtZero: true,
                    min: 0,
                    max: 1,
                    grid: {
                        drawOnChartArea: false
                    },
                    ticks: {
                        color: theme.faint,
                        stepSize: 1,
                        callback(value) {
                            return value === 1 ? 'Oui' : 'Non';
                        }
                    },
                    title: {
                        display: true,
                        text: 'Complété',
                        color: theme.muted
                    }
                }
            }
        }
    });
}

function buildOverallProgressChart(theme) {
    const canvas = document.getElementById('overallProgressChart');
    const totalModules = Number(window.totalModulesCount || 0);
    const completedModules = Number(window.completedModulesCount || 0);
    const percentage = Number(window.percentageCompleteValue || 0);

    if (!canvas || totalModules < 0) {
        return null;
    }

    const context = canvas.getContext('2d');
    const ringGradient = createLinearGradient(
        context,
        `${theme.primary}ff`,
        `${theme.secondary}ff`,
        true
    );

    return new Chart(context, {
        type: 'doughnut',
        data: {
            labels: ['Complété', 'Restant'],
            datasets: [{
                data: [percentage, Math.max(100 - percentage, 0)],
                backgroundColor: [ringGradient, 'rgba(203, 213, 225, 0.28)'],
                borderColor: [theme.surface, theme.surface],
                borderWidth: 3,
                hoverOffset: 4,
                cutout: '72%'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        color: theme.muted,
                        usePointStyle: true,
                        boxWidth: 10,
                        padding: 16
                    }
                },
                tooltip: {
                    backgroundColor: theme.elevated,
                    titleColor: theme.text,
                    bodyColor: theme.text,
                    borderColor: theme.border,
                    borderWidth: 1,
                    cornerRadius: 14,
                    padding: 12,
                    callbacks: {
                        label(context) {
                            return `${context.label}: ${Math.round((context.raw || 0) * 10) / 10}%`;
                        }
                    }
                }
            }
        },
        plugins: [{
            id: 'centerLabel',
            beforeDraw(chart) {
                const { width, height, ctx } = chart;
                ctx.save();
                ctx.fillStyle = theme.primary;
                ctx.font = `700 ${Math.max(height / 8.5, 18)}px Space Grotesk, sans-serif`;
                ctx.textAlign = 'center';
                ctx.textBaseline = 'middle';
                ctx.fillText(`${Math.round(percentage)}%`, width / 2, height / 2);
                ctx.font = `500 ${Math.max(height / 20, 10)}px IBM Plex Mono, monospace`;
                ctx.fillStyle = theme.faint;
                ctx.fillText(`${completedModules}/${totalModules} modules`, width / 2, height / 2 + Math.max(height / 8, 22));
                ctx.restore();
            }
        }]
    });
}

function initializeDashboardCharts() {
    if (!window.Chart || !document.querySelector('.dashboard-hero')) {
        return;
    }

    const theme = getDashboardTheme();
    applyDashboardChartDefaults(theme);
    destroyDashboardCharts();

    window.tangerDashboardCharts = {
        moduleCompletion: buildModuleCompletionChart(theme),
        overallProgress: buildOverallProgressChart(theme)
    };
}

document.addEventListener('DOMContentLoaded', initializeDashboardCharts);
document.addEventListener('theme:changed', initializeDashboardCharts);
