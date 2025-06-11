/**
 * Script de graphiques pour le tableau de bord - Version Améliorée
 * Utilise Chart.js pour afficher les graphiques de progression
 * Intégration avec dashboard.css et enhanced-sidebar.css
 */

// Configuration des couleurs Tanger Alliance pour les graphiques
const TANGER_ALLIANCE_COLORS = {
    primary: '#004a99',
    secondary: '#00a8cc', 
    accent: '#ff6b35',
    success: '#28a745',
    warning: '#ffc107',
    danger: '#dc3545',
    neutral: '#6c757d',
    light: '#f8f9fa'
};

// Configuration des gradients pour les graphiques
function createChartGradient(ctx, color1, color2, direction = 'vertical') {
    const gradient = direction === 'vertical' 
        ? ctx.createLinearGradient(0, 0, 0, 400)
        : ctx.createLinearGradient(0, 0, 400, 0);
    
    gradient.addColorStop(0, color1);
    gradient.addColorStop(1, color2);
    return gradient;
}

// Configuration par défaut améliorée pour Chart.js
Chart.defaults.font.family = "'Poppins', 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif";
Chart.defaults.font.size = 14;
Chart.defaults.color = '#4b5563';
Chart.defaults.borderColor = 'rgba(0, 0, 0, 0.1)';

// Animation par défaut améliorée
Chart.defaults.animation.duration = 1500;
Chart.defaults.animation.easing = 'easeInOutCubic';

// Vérifier si les variables nécessaires sont définies
function checkDataAvailability() {
    console.group('Vérification des données disponibles pour les graphiques');
    
    // Vérifier les données du graphique de progression par module
    let moduleChartDataOk = window.moduleChartLabels && window.moduleChartData && window.moduleChartCompletionStatus;
    console.log('Données pour graphique modules disponibles:', moduleChartDataOk ? 'OUI' : 'NON');
    
    if (moduleChartDataOk) {
        console.log('Labels des modules:', window.moduleChartLabels);
        console.log('Scores des modules:', window.moduleChartData);
        console.log('États de complétion:', window.moduleChartCompletionStatus);
        // Compter les modules complétés à partir des données JavaScript
        const jsCompletedModules = window.moduleChartCompletionStatus.filter(status => status === 1).length;
        console.log('Modules complétés (calculé à partir des états):', jsCompletedModules);
    } else {
        console.warn('Certaines données pour le graphique des modules sont manquantes!');
    }
    
    // Vérifier les données du graphique de progression globale
    let overallChartDataOk = typeof window.totalModulesCount !== 'undefined' && 
                           typeof window.completedModulesCount !== 'undefined' && 
                           typeof window.percentageCompleteValue !== 'undefined';
    console.log('Données pour graphique global disponibles:', overallChartDataOk ? 'OUI' : 'NON');
    
    if (overallChartDataOk) {
        console.log('Total modules:', window.totalModulesCount);
        console.log('Modules complétés:', window.completedModulesCount);
        console.log('Pourcentage:', window.percentageCompleteValue);
        console.log('Pourcentage calculé en JS:', Math.round((window.completedModulesCount / window.totalModulesCount) * 100) || 0);
        
        // Vérifier la cohérence entre les valeurs
        const progressBar = document.querySelector('.progress-bar');
        if (progressBar) {
            const progressBarValue = progressBar.style.width;
            console.log('Valeur de la barre de progression HTML:', progressBarValue);
            console.log('Différence avec le pourcentage JS:', progressBarValue !== window.percentageCompleteValue + '%' ? 'OUI' : 'NON');
        }
    } else {
        console.warn('Certaines données pour le graphique global sont manquantes!');
    }
    
    console.groupEnd();
    return { moduleChartDataOk, overallChartDataOk };
}

// Fonction pour initialiser le graphique de progression par module
function initModuleCompletionChart() {
    console.group('Initialisation du graphique de progression par module');
    
    // Vérifier si les données nécessaires sont disponibles
    if (!window.moduleChartLabels || !window.moduleChartData || !window.moduleChartCompletionStatus) {
        console.error("Données manquantes pour le graphique de progression par module");
        console.groupEnd();
        return;
    }
    
    // Vérifier si l'élément canvas existe
    const ctx = document.getElementById('moduleCompletionChart');
    if (!ctx) {
        console.error("Élément canvas 'moduleCompletionChart' non trouvé dans le DOM");
        console.groupEnd();
        return;
    }
    
    console.log("Création du graphique de progression par module...");
    try {
        new Chart(ctx, {
            type: 'bar',
            data: {
                labels: window.moduleChartLabels,
                datasets: [
                    {
                        label: 'Score (%)',
                        data: window.moduleChartData,
                        backgroundColor: function(context) {
                            const index = context.dataIndex;
                            const score = window.moduleChartData[index];
                            const ctx = context.chart.ctx;
                            
                            if (score >= 80) {
                                return createChartGradient(ctx, 
                                    'rgba(40, 167, 69, 0.8)', 
                                    'rgba(40, 167, 69, 0.4)'
                                );
                            }
                            if (score >= 60) {
                                return createChartGradient(ctx, 
                                    'rgba(255, 193, 7, 0.8)', 
                                    'rgba(255, 193, 7, 0.4)'
                                );
                            }
                            if (score > 0) {
                                return createChartGradient(ctx, 
                                    'rgba(220, 53, 69, 0.8)', 
                                    'rgba(220, 53, 69, 0.4)'
                                );
                            }
                            return 'rgba(108, 117, 125, 0.5)';
                        },
                        borderColor: TANGER_ALLIANCE_COLORS.primary,
                        borderWidth: 3,
                        yAxisID: 'y',
                        borderRadius: 4,
                        hoverBackgroundColor: function(context) {
                            const index = context.dataIndex;
                            const score = window.moduleChartData[index];
                            
                            if (score >= 80) return 'rgba(40, 167, 69, 0.9)';   // Vert pour score élevé
                            if (score >= 60) return 'rgba(255, 193, 7, 0.9)';    // Jaune pour score moyen
                            if (score > 0)  return 'rgba(220, 53, 69, 0.9)';     // Rouge pour score faible
                            return 'rgba(108, 117, 125, 0.7)';                    // Gris pour score nul
                        },
                    },
                    {
                        label: 'Complété',
                        data: window.moduleChartCompletionStatus,
                        type: 'line',
                        fill: false,
                        borderColor: TANGER_ALLIANCE_COLORS.secondary,
                        borderWidth: 3,
                        pointBackgroundColor: function(context) {
                            var index = context.dataIndex;
                            var value = context.dataset.data[index];
                            return value === 1 ? TANGER_ALLIANCE_COLORS.success : TANGER_ALLIANCE_COLORS.neutral;
                        },
                        pointBorderColor: '#ffffff',
                        pointBorderWidth: 2,
                        pointRadius: 8,
                        pointHoverRadius: 10,
                        pointStyle: 'rectRounded',
                        yAxisID: 'y1'
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
                            font: {
                                family: "'Poppins', sans-serif",
                                size: 14,
                                weight: '500'
                            },
                            color: '#374151',
                            usePointStyle: true,
                            padding: 20
                        }
                    },
                    tooltip: {
                        backgroundColor: 'rgba(0, 74, 153, 0.95)',
                        titleColor: '#ffffff',
                        titleFont: {
                            family: "'Poppins', sans-serif",
                            size: 16,
                            weight: '600'
                        },
                        bodyColor: '#ffffff',
                        bodyFont: {
                            family: "'Poppins', sans-serif",
                            size: 14
                        },
                        borderColor: TANGER_ALLIANCE_COLORS.secondary,
                        borderWidth: 2,
                        cornerRadius: 12,
                        padding: 12,
                        displayColors: true,
                        callbacks: {
                            label: function(context) {
                                const datasetLabel = context.dataset.label || '';
                                const value = context.raw;
                                
                                if (datasetLabel === 'Complété') {
                                    return ` ${datasetLabel}: ${value === 1 ? 'Oui ✓' : 'Non ✗'}`;
                                }
                                return ` ${datasetLabel}: ${Math.round(value * 10) / 10}%`;
                            }
                        }
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: 'Score (%)'
                        },
                        suggestedMax: 100
                    },
                    y1: {
                        position: 'right',
                        beginAtZero: true,
                        min: -0.2, // Légèrement en dessous de 0 pour plus de visibilité
                        max: 1.2,  // Légèrement au-dessus de 1 pour plus de visibilité
                        ticks: {
                            stepSize: 1,
                            callback: function(value) {
                                if (value === 0) return 'Non';
                                if (value === 1) return 'Oui';
                                return '';
                            }
                        },
                        title: {
                            display: true,
                            text: 'Complété'
                        },
                        grid: {
                            drawOnChartArea: false
                        }
                    }
                },
                plugins: {
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                const datasetLabel = context.dataset.label || '';
                                const value = context.raw;
                                
                                if (datasetLabel === 'Complété') {
                                    return datasetLabel + ': ' + (value === 1 ? 'Oui' : 'Non');
                                }
                                return datasetLabel + ': ' + (Math.round(value * 10) / 10) + '%';
                            }
                        }
                    }
                }
            }
        });
        console.log("Graphique de progression par module créé avec succès");
    } catch (error) {
        console.error("Erreur lors de la création du graphique:", error);
    }
    console.groupEnd();
}

// Fonction pour initialiser le graphique de progression globale
function initOverallProgressChart() {
    console.group('Initialisation du graphique de progression globale');
    
    try {
        const ctx = document.getElementById('overallProgressChart');
        if (!ctx) {
            console.error("Canvas 'overallProgressChart' introuvable!");
            return;
        }
        
        console.log("Initialisation du graphique de progression globale...");
        
        // Utiliser les données globales ou des valeurs par défaut
        const totalModules = window.totalModulesCount || 0;
        const completedModules = window.completedModulesCount || 0;
        const percentageComplete = window.percentageCompleteValue || 0;
        
        // Créer le gradient pour le graphique en donut
        const gradient = createChartGradient(ctx.getContext('2d'), 
            TANGER_ALLIANCE_COLORS.primary, 
            TANGER_ALLIANCE_COLORS.secondary
        );
        
        new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: ['Complété', 'Restant'],
                datasets: [{
                    data: [percentageComplete, 100 - percentageComplete],
                    backgroundColor: [
                        gradient,
                        'rgba(229, 231, 235, 0.8)'
                    ],
                    borderColor: [
                        TANGER_ALLIANCE_COLORS.primary,
                        '#e5e7eb'
                    ],
                    borderWidth: 3,
                    hoverBorderWidth: 5,
                    cutout: '70%'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            font: {
                                family: "'Poppins', sans-serif",
                                size: 14,
                                weight: '500'
                            },
                            color: '#374151',
                            usePointStyle: true,
                            padding: 20
                        }
                    },
                    tooltip: {
                        backgroundColor: 'rgba(0, 74, 153, 0.95)',
                        titleColor: '#ffffff',
                        titleFont: {
                            family: "'Poppins', sans-serif",
                            size: 16,
                            weight: '600'
                        },
                        bodyColor: '#ffffff',
                        bodyFont: {
                            family: "'Poppins', sans-serif",
                            size: 14
                        },
                        borderColor: TANGER_ALLIANCE_COLORS.secondary,
                        borderWidth: 2,
                        cornerRadius: 12,
                        padding: 12,
                        callbacks: {
                            label: function(context) {
                                const label = context.label || '';
                                const value = context.raw;
                                return ` ${label}: ${Math.round(value * 10) / 10}%`;
                            }
                        }
                    }
                },
                animation: {
                    animateRotate: true,
                    animateScale: true,
                    duration: 2000,
                    easing: 'easeInOutCubic'
                }
            },
            plugins: [{
                beforeDraw: function(chart) {
                    const width = chart.width;
                    const height = chart.height;
                    const ctx = chart.ctx;
                    
                    ctx.restore();
                    const fontSize = (height / 120).toFixed(2);
                    ctx.font = `bold ${fontSize}em Poppins, sans-serif`;
                    ctx.textBaseline = "middle";
                    ctx.fillStyle = TANGER_ALLIANCE_COLORS.primary;
                    
                    const text = Math.round(percentageComplete * 10) / 10 + "%";
                    const textX = Math.round((width - ctx.measureText(text).width) / 2);
                    const textY = height / 2;
                    
                    ctx.fillText(text, textX, textY);
                    ctx.save();
                }
            }]
        });
        console.log("Graphique de progression globale créé avec succès");
    } catch (error) {
        console.error("Erreur lors de la création du graphique:", error);
    }
    console.groupEnd();
}

// Initialiser les graphiques au chargement de la page
document.addEventListener('DOMContentLoaded', function() {
    console.log("=== Page chargée, initialisation des graphiques... ===");
    
    // Vérifier si Chart.js est disponible
    if (typeof Chart === 'undefined') {
        console.error("Chart.js n'est pas chargé! Vérifiez l'inclusion de la bibliothèque.");
        return;
    }
    
    // Vérifier si les données sont disponibles
    const { moduleChartDataOk, overallChartDataOk } = checkDataAvailability();
    
    // Initialiser les graphiques si les données sont disponibles
    if (moduleChartDataOk) {
        initModuleCompletionChart();
    }
    
    if (overallChartDataOk) {
        initOverallProgressChart();
    }
    
    // Si aucune donnée n'est disponible, essayer à nouveau après un court délai
    // (utile si les données sont chargées dynamiquement)
    if (!moduleChartDataOk || !overallChartDataOk) {
        console.log("Certaines données ne sont pas encore disponibles, nouvelle tentative dans 500ms...");
        setTimeout(function() {
            const { moduleChartDataOk, overallChartDataOk } = checkDataAvailability();
            if (moduleChartDataOk && !document.getElementById('moduleCompletionChart').__chartjs) {
                initModuleCompletionChart();
            }
            if (overallChartDataOk && !document.getElementById('overallProgressChart').__chartjs) {
                initOverallProgressChart();
            }
        }, 500);
    }
});
