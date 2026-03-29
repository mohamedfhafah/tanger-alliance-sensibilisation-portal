function getDashboardCssVariable(name, fallback) {
    const value = getComputedStyle(document.documentElement).getPropertyValue(name).trim();
    return value || fallback;
}

function revealDashboardBlocks() {
    const items = document.querySelectorAll('.dashboard-panel, .dashboard-hero, .ta-kpi-card, .small-box, .info-box');
    const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

    if (reducedMotion) {
        items.forEach((item) => item.classList.add('visible'));
        return;
    }

    const observer = new IntersectionObserver((entries) => {
        entries.forEach((entry) => {
            if (entry.isIntersecting) {
                entry.target.classList.add('visible');
                observer.unobserve(entry.target);
            }
        });
    }, {
        threshold: 0.08,
        rootMargin: '0px 0px -48px 0px'
    });

    items.forEach((item, index) => {
        item.classList.add('fade-in-up');
        item.style.transitionDelay = `${Math.min(index * 70, 320)}ms`;
        observer.observe(item);
    });
}

function enhanceDashboardInteractions() {
    const accent = getDashboardCssVariable('--color-primary', '#38bdf8');

    document.querySelectorAll('.dashboard-module-entry, .dashboard-activity-item, .badge-item').forEach((item) => {
        item.addEventListener('mouseenter', () => {
            item.style.borderColor = `${accent}55`;
        });

        item.addEventListener('mouseleave', () => {
            item.style.borderColor = '';
        });
    });
}

function refreshChartsForTheme() {
    if (!window.Chart || !Chart.instances) {
        return;
    }

    Object.values(Chart.instances).forEach((chart) => chart?.update?.());
}

document.addEventListener('DOMContentLoaded', () => {
    if (!document.querySelector('.dashboard-hero')) {
        return;
    }

    revealDashboardBlocks();
    enhanceDashboardInteractions();

    document.addEventListener('theme:changed', refreshChartsForTheme);
});
