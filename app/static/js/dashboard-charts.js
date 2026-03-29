function readDashboardCssVariable(name, fallback) {
    const value = getComputedStyle(document.documentElement).getPropertyValue(name).trim();
    return value || fallback;
}

function getDashboardTheme() {
    return {
        primary: readDashboardCssVariable('--color-primary', '#5b9cf5'),
        secondary: readDashboardCssVariable('--color-secondary', '#4ec9b0'),
        accent: readDashboardCssVariable('--color-accent', '#e8a840'),
        success: readDashboardCssVariable('--color-success', '#3dba6f'),
        warning: readDashboardCssVariable('--color-warning', '#dfb050'),
        danger: readDashboardCssVariable('--color-danger', '#e85c5c'),
        text: readDashboardCssVariable('--color-text', '#eaf0f8'),
        muted: readDashboardCssVariable('--color-text-muted', '#8c9db5'),
        faint: readDashboardCssVariable('--color-text-faint', '#6b7d96'),
        border: readDashboardCssVariable('--color-border', 'rgba(148, 163, 184, 0.12)'),
        surface: readDashboardCssVariable('--color-surface-strong', '#142236'),
        elevated: readDashboardCssVariable('--color-surface-elevated', '#1a2a48')
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
                    borderColor: theme.secondary,
                    backgroundColor: theme.secondary,
                    pointBackgroundColor: completion.map((value) => value === 1 ? theme.success : theme.primary),
                    pointBorderColor: '#ffffff',
                    pointBorderWidth: 2,
                    pointRadius: 4,
                    pointHoverRadius: 6,
                    borderWidth: 2,
                    tension: 0.35
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
                        maxRotation: 0,
                        minRotation: 0,
                        autoSkip: true,
                        maxTicksLimit: 6,
                        font: {
                            size: 12
                        },
                        callback: function(value) {
                            let label = this.getLabelForValue(value) || '';
                            if (label.length > 15) {
                                return label.substr(0, 15) + '...';
                            }
                            return label;
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
