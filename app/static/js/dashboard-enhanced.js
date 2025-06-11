/**
 * Enhanced Dashboard JavaScript - Portail de Sécurité Tanger Alliance
 * 
 * Styles JavaScript pour les nouveaux composants dashboard incluant :
 * - Animations des cartes de statistiques
 * - Interactions avec les barres de progression
 * - Timeline d'activités dynamique
 * - Graphiques Chart.js améliorés
 * - Badges avec effets visuels
 * - Intégration avec enhanced-sidebar.css et dashboard.css
 */

class DashboardEnhanced {
    constructor() {
        this.charts = {};
        this.animations = {};
        this.init();
    }

    /**
     * Initialisation du dashboard amélioré
     */
    init() {
        this.initializeComponents();
        this.setupAnimations();
        this.setupInteractions();
        this.initializeCharts();
        this.setupResponsiveHandlers();
    }

    /**
     * Initialisation des composants dashboard
     */
    initializeComponents() {
        // Initialiser les cartes de statistiques animées
        this.initStatCards();
        
        // Initialiser les barres de progression avec animations
        this.initProgressBars();
        
        // Initialiser la timeline interactive
        this.initTimeline();
        
        // Initialiser les badges avec effets
        this.initEnhancedBadges();
        
        // Initialiser les info-boxes hover
        this.initInfoBoxes();
    }

    /**
     * Configuration des animations générales
     */
    setupAnimations() {
        // Animation d'entrée pour les éléments du dashboard
        this.observeElements('.stat-card, .info-box, .timeline-item, .chart-container', {
            threshold: 0.1,
            callback: (entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        entry.target.classList.add('fade-in');
                    }
                });
            }
        });

        // Animations de parallaxe légère pour les cartes
        this.setupParallaxCards();
    }

    /**
     * Configuration des interactions utilisateur
     */
    setupInteractions() {
        // Effets hover pour les cartes de statistiques
        document.querySelectorAll('.stat-card').forEach(card => {
            card.addEventListener('mouseenter', this.handleStatCardHover.bind(this));
            card.addEventListener('mouseleave', this.handleStatCardLeave.bind(this));
        });

        // Interactions avec les éléments de timeline
        document.querySelectorAll('.timeline-item').forEach(item => {
            item.addEventListener('click', this.handleTimelineItemClick.bind(this));
        });

        // Gestion des clics sur les badges pulse
        document.querySelectorAll('.badge-pulse').forEach(badge => {
            badge.addEventListener('click', this.handleBadgePulseClick.bind(this));
        });
    }

    /**
     * Initialisation des cartes de statistiques
     */
    initStatCards() {
        const statCards = document.querySelectorAll('.stat-card');
        
        statCards.forEach((card, index) => {
            // Animation d'entrée décalée
            setTimeout(() => {
                card.style.opacity = '0';
                card.style.transform = 'translateY(30px)';
                
                requestAnimationFrame(() => {
                    card.style.transition = 'all 0.6s cubic-bezier(0.4, 0, 0.2, 1)';
                    card.style.opacity = '1';
                    card.style.transform = 'translateY(0)';
                });
            }, index * 150);

            // Animation des valeurs numériques
            const valueElement = card.querySelector('.stat-value');
            if (valueElement) {
                this.animateNumber(valueElement);
            }
        });
    }

    /**
     * Initialisation des barres de progression animées
     */
    initProgressBars() {
        const progressBars = document.querySelectorAll('.progress-bar');
        
        progressBars.forEach(bar => {
            const targetWidth = bar.style.width || bar.getAttribute('aria-valuenow') + '%';
            
            // Animation de remplissage
            bar.style.width = '0%';
            setTimeout(() => {
                bar.style.transition = 'width 1.5s cubic-bezier(0.4, 0, 0.2, 1)';
                bar.style.width = targetWidth;
            }, 500);

            // Animation des rayures pour les barres actives
            if (bar.classList.contains('progress-bar-striped')) {
                this.enhanceStripedAnimation(bar);
            }
        });
    }

    /**
     * Initialisation de la timeline interactive
     */
    initTimeline() {
        const timelineItems = document.querySelectorAll('.timeline-item');
        
        timelineItems.forEach((item, index) => {
            // Animation d'apparition séquentielle
            item.style.opacity = '0';
            item.style.transform = 'translateX(-20px)';
            
            setTimeout(() => {
                item.style.transition = 'all 0.5s ease';
                item.style.opacity = '1';
                item.style.transform = 'translateX(0)';
            }, index * 200 + 800);

            // Effets hover pour les contenus de timeline
            const content = item.querySelector('.timeline-content');
            if (content) {
                content.addEventListener('mouseenter', () => {
                    content.style.transform = 'scale(1.02)';
                    content.style.boxShadow = '0 8px 25px rgba(0, 0, 0, 0.15)';
                });
                
                content.addEventListener('mouseleave', () => {
                    content.style.transform = 'scale(1)';
                    content.style.boxShadow = '';
                });
            }
        });
    }

    /**
     * Initialisation des badges améliorés
     */
    initEnhancedBadges() {
        const badgesPulse = document.querySelectorAll('.badge-pulse');
        
        badgesPulse.forEach(badge => {
            // Démarrer l'animation pulse après un délai aléatoire
            const delay = Math.random() * 2000;
            setTimeout(() => {
                badge.classList.add('pulse-active');
            }, delay);
        });
    }

    /**
     * Initialisation des info-boxes
     */
    initInfoBoxes() {
        const infoBoxes = document.querySelectorAll('.info-box');
        
        infoBoxes.forEach(box => {
            box.addEventListener('mouseenter', () => {
                this.createRippleEffect(box);
            });
        });
    }

    /**
     * Initialisation des graphiques Chart.js améliorés
     */
    initializeCharts() {
        // Configuration par défaut pour tous les graphiques
        Chart.defaults.font.family = "'Poppins', 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif";
        Chart.defaults.color = '#4b5563';
        Chart.defaults.borderColor = 'rgba(0, 0, 0, 0.1)';

        // Styles personnalisés pour les graphiques du dashboard
        this.setupChartStyles();
        
        // Réinitialiser les graphiques existants avec les nouveaux styles
        this.enhanceExistingCharts();
    }

    /**
     * Animation des nombres dans les cartes de statistiques
     */
    animateNumber(element) {
        const targetValue = parseInt(element.textContent) || 0;
        const duration = 2000;
        const step = targetValue / (duration / 16);
        let current = 0;

        const updateNumber = () => {
            current += step;
            if (current < targetValue) {
                element.textContent = Math.floor(current);
                requestAnimationFrame(updateNumber);
            } else {
                element.textContent = targetValue;
            }
        };

        // Démarrer l'animation après un délai
        setTimeout(updateNumber, 600);
    }

    /**
     * Gestion des effets hover sur les cartes de statistiques
     */
    handleStatCardHover(event) {
        const card = event.currentTarget;
        const icon = card.querySelector('.stat-icon');
        
        if (icon) {
            icon.style.transform = 'scale(1.1) rotate(5deg)';
            icon.style.opacity = '0.3';
        }
        
        card.style.borderLeft = '4px solid var(--tanger-alliance-accent)';
    }

    handleStatCardLeave(event) {
        const card = event.currentTarget;
        const icon = card.querySelector('.stat-icon');
        
        if (icon) {
            icon.style.transform = 'scale(1) rotate(0deg)';
            icon.style.opacity = '0.15';
        }
        
        card.style.borderLeft = '';
    }

    /**
     * Gestion des clics sur les éléments de timeline
     */
    handleTimelineItemClick(event) {
        const item = event.currentTarget;
        const content = item.querySelector('.timeline-content');
        
        // Animation de "pop"
        content.style.transform = 'scale(0.95)';
        setTimeout(() => {
            content.style.transform = 'scale(1)';
        }, 150);
        
        // Optionnel : Afficher plus de détails
        this.expandTimelineItem(item);
    }

    /**
     * Gestion des clics sur les badges pulse
     */
    handleBadgePulseClick(event) {
        const badge = event.currentTarget;
        
        // Créer un effet de burst
        this.createBurstEffect(badge);
        
        // Arrêter temporairement l'animation pulse
        badge.style.animationPlayState = 'paused';
        setTimeout(() => {
            badge.style.animationPlayState = 'running';
        }, 1000);
    }

    /**
     * Création d'un effet de ondulation (ripple)
     */
    createRippleEffect(element) {
        const ripple = document.createElement('div');
        ripple.className = 'ripple-effect';
        
        const rect = element.getBoundingClientRect();
        const size = Math.max(rect.width, rect.height);
        
        ripple.style.width = ripple.style.height = size + 'px';
        ripple.style.left = (rect.width / 2 - size / 2) + 'px';
        ripple.style.top = (rect.height / 2 - size / 2) + 'px';
        
        element.style.position = 'relative';
        element.appendChild(ripple);
        
        setTimeout(() => {
            ripple.remove();
        }, 600);
    }

    /**
     * Création d'un effet de burst pour les badges
     */
    createBurstEffect(element) {
        const burst = document.createElement('div');
        burst.className = 'burst-effect';
        element.appendChild(burst);
        
        setTimeout(() => {
            burst.remove();
        }, 1000);
    }

    /**
     * Configuration des styles personnalisés pour Chart.js
     */
    setupChartStyles() {
        // Couleurs Tanger Alliance pour les graphiques
        this.chartColors = {
            primary: '#004a99',
            secondary: '#00a8cc',
            accent: '#ff6b35',
            success: '#28a745',
            warning: '#ffc107',
            danger: '#dc3545',
            info: '#17a2b8',
            light: '#f8f9fa',
            dark: '#343a40'
        };

        // Gradients pour les graphiques
        this.setupChartGradients();
    }

    /**
     * Configuration des gradients pour Chart.js
     */
    setupChartGradients() {
        // Cette méthode sera appelée pour chaque graphique individuellement
        this.createGradient = (ctx, colorStart, colorEnd) => {
            const gradient = ctx.createLinearGradient(0, 0, 0, 400);
            gradient.addColorStop(0, colorStart);
            gradient.addColorStop(1, colorEnd);
            return gradient;
        };
    }

    /**
     * Amélioration des graphiques existants
     */
    enhanceExistingCharts() {
        // Attendre que les graphiques existants soient initialisés
        setTimeout(() => {
            Object.values(Chart.instances).forEach(chart => {
                this.enhanceChart(chart);
            });
        }, 1000);
    }

    /**
     * Amélioration d'un graphique spécifique
     */
    enhanceChart(chart) {
        // Ajouter des animations personnalisées
        chart.options.animation = {
            duration: 2000,
            easing: 'easeInOutCubic'
        };

        // Améliorer les tooltips
        chart.options.plugins.tooltip = {
            ...chart.options.plugins.tooltip,
            backgroundColor: 'rgba(0, 74, 153, 0.9)',
            titleColor: '#ffffff',
            bodyColor: '#ffffff',
            borderColor: '#00a8cc',
            borderWidth: 2,
            cornerRadius: 8,
            displayColors: true
        };

        chart.update();
    }

    /**
     * Configuration de la parallaxe légère pour les cartes
     */
    setupParallaxCards() {
        window.addEventListener('scroll', () => {
            const scrollY = window.pageYOffset;
            
            document.querySelectorAll('.stat-card, .chart-container').forEach((card, index) => {
                const speed = 0.5 + (index * 0.1);
                const yPos = -(scrollY * speed / 100);
                card.style.transform = `translateY(${yPos}px)`;
            });
        });
    }

    /**
     * Observateur d'éléments pour les animations
     */
    observeElements(selector, options) {
        const observer = new IntersectionObserver(options.callback, {
            threshold: options.threshold || 0.1
        });

        document.querySelectorAll(selector).forEach(el => {
            observer.observe(el);
        });
    }

    /**
     * Configuration des gestionnaires responsive
     */
    setupResponsiveHandlers() {
        window.addEventListener('resize', this.handleResize.bind(this));
        this.handleResize(); // Appel initial
    }

    /**
     * Gestion des changements de taille d'écran
     */
    handleResize() {
        const isMobile = window.innerWidth <= 768;
        
        if (isMobile) {
            // Ajustements pour mobile
            document.querySelectorAll('.stat-card').forEach(card => {
                card.style.marginBottom = '1rem';
            });
            
            // Redimensionner les graphiques
            Object.values(Chart.instances).forEach(chart => {
                chart.resize();
            });
        }
    }

    /**
     * Expansion d'un élément de timeline (optionnel)
     */
    expandTimelineItem(item) {
        const content = item.querySelector('.timeline-content');
        const isExpanded = content.classList.contains('expanded');
        
        if (!isExpanded) {
            content.classList.add('expanded');
            // Ajouter du contenu détaillé si nécessaire
        } else {
            content.classList.remove('expanded');
        }
    }

    /**
     * Amélioration de l'animation des rayures
     */
    enhanceStripedAnimation(progressBar) {
        // Ajouter une animation plus fluide aux rayures
        progressBar.style.backgroundSize = '1rem 1rem';
        progressBar.style.animation = 'progress-bar-stripes 1s linear infinite';
    }
}

// Styles CSS additionnels injectés dynamiquement
const additionalStyles = `
    .ripple-effect {
        position: absolute;
        border-radius: 50%;
        background: rgba(0, 168, 204, 0.3);
        transform: scale(0);
        animation: ripple 0.6s linear;
        pointer-events: none;
    }
    
    @keyframes ripple {
        to {
            transform: scale(4);
            opacity: 0;
        }
    }
    
    .burst-effect {
        position: absolute;
        top: 50%;
        left: 50%;
        width: 20px;
        height: 20px;
        background: radial-gradient(circle, rgba(255, 107, 53, 0.8) 0%, transparent 70%);
        border-radius: 50%;
        transform: translate(-50%, -50%) scale(0);
        animation: burst 1s ease-out;
        pointer-events: none;
    }
    
    @keyframes burst {
        0% {
            transform: translate(-50%, -50%) scale(0);
            opacity: 1;
        }
        50% {
            transform: translate(-50%, -50%) scale(2);
            opacity: 0.8;
        }
        100% {
            transform: translate(-50%, -50%) scale(4);
            opacity: 0;
        }
    }
    
    .timeline-content.expanded {
        max-height: none;
        overflow: visible;
    }
    
    .pulse-active {
        animation: pulse 1.5s ease-out infinite;
    }
`;

// Injection des styles additionnels
const styleSheet = document.createElement('style');
styleSheet.textContent = additionalStyles;
document.head.appendChild(styleSheet);

// Initialisation automatique quand le DOM est prêt
document.addEventListener('DOMContentLoaded', () => {
    console.log('🚀 Initialisation du Dashboard Amélioré - Tanger Alliance');
    window.dashboardEnhanced = new DashboardEnhanced();
});

// Export pour utilisation modulaire
if (typeof module !== 'undefined' && module.exports) {
    module.exports = DashboardEnhanced;
}
