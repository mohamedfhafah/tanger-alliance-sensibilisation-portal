document.addEventListener('DOMContentLoaded', function() {
    const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    const animateElements = document.querySelectorAll(
        '.hero-badge, .hero-title, .hero-subtitle, .hero-actions, .user-pill, .premium-card, .stat-block, .hero-console, .console-metric, .command-mission, .command-live-panel, .track-card, .analysis-content, .analysis-chart-panel'
    );

    if (prefersReducedMotion) {
        animateElements.forEach((el) => el.classList.add('visible'));
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
        threshold: 0.12,
        rootMargin: '0px 0px -48px 0px'
    });

    animateElements.forEach((el, index) => {
        el.classList.add('fade-in-up');
        el.style.transitionDelay = `${Math.min(index * 70, 420)}ms`;
        observer.observe(el);
    });
});
