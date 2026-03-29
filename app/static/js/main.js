function withBootstrapInstances(selector, bootstrap5Factory, jqueryFactory) {
    document.querySelectorAll(selector).forEach((element) => {
        if (window.bootstrap && typeof bootstrap5Factory === 'function') {
            bootstrap5Factory(element);
            return;
        }

        if (window.jQuery && typeof jqueryFactory === 'function') {
            jqueryFactory(window.jQuery(element));
        }
    });
}

function initializeBootstrapComponents() {
    withBootstrapInstances(
        '[data-toggle="tooltip"], [data-bs-toggle="tooltip"]',
        (element) => {
            if (!window.bootstrap?.Tooltip) {
                return;
            }

            if (typeof window.bootstrap.Tooltip.getOrCreateInstance === 'function') {
                window.bootstrap.Tooltip.getOrCreateInstance(element);
                return;
            }

            if (typeof window.bootstrap.Tooltip.getInstance === 'function') {
                window.bootstrap.Tooltip.getInstance(element) || new window.bootstrap.Tooltip(element);
            }
        },
        ($element) => $element.tooltip()
    );

    withBootstrapInstances(
        '[data-toggle="popover"], [data-bs-toggle="popover"]',
        (element) => {
            if (!window.bootstrap?.Popover) {
                return;
            }

            if (typeof window.bootstrap.Popover.getOrCreateInstance === 'function') {
                window.bootstrap.Popover.getOrCreateInstance(element);
                return;
            }

            if (typeof window.bootstrap.Popover.getInstance === 'function') {
                window.bootstrap.Popover.getInstance(element) || new window.bootstrap.Popover(element);
            }
        },
        ($element) => $element.popover()
    );
}

function initializePasswordValidation() {
    const passwordInput = document.getElementById('password');
    const confirmInput = document.getElementById('confirm_password');
    const strengthMeter = document.getElementById('password-strength');

    if (passwordInput && strengthMeter) {
        passwordInput.addEventListener('input', function () {
            const password = this.value;
            let strength = 0;

            if (password.length >= 8) strength += 20;
            if (/[a-z]+/.test(password)) strength += 20;
            if (/[A-Z]+/.test(password)) strength += 20;
            if (/[0-9]+/.test(password)) strength += 20;
            if (/[\W_]+/.test(password)) strength += 20;

            strengthMeter.style.width = `${strength}%`;
            strengthMeter.className = 'progress-bar';

            if (strength <= 40) {
                strengthMeter.classList.add('bg-danger');
            } else if (strength <= 80) {
                strengthMeter.classList.add('bg-warning');
            } else {
                strengthMeter.classList.add('bg-success');
            }
        });
    }

    if (passwordInput && confirmInput) {
        confirmInput.addEventListener('input', function () {
            const mismatch = passwordInput.value !== this.value;
            this.setCustomValidity(mismatch ? 'Les mots de passe ne correspondent pas' : '');
        });
    }
}

function initializeAlertDismissal() {
    window.setTimeout(() => {
        document.querySelectorAll('.alert:not(.alert-permanent)').forEach((alert) => {
            if (window.bootstrap?.Alert) {
                if (typeof window.bootstrap.Alert.getOrCreateInstance === 'function') {
                    window.bootstrap.Alert.getOrCreateInstance(alert).close();
                    return;
                }

                if (typeof window.bootstrap.Alert.getInstance === 'function') {
                    const instance = window.bootstrap.Alert.getInstance(alert) || new window.bootstrap.Alert(alert);
                    instance.close();
                    return;
                }
            }

            if (window.jQuery) {
                window.jQuery(alert).alert('close');
                return;
            }

            alert.style.transition = 'opacity 0.35s ease';
            alert.style.opacity = '0';
            window.setTimeout(() => alert.remove(), 350);
        });
    }, 5000);
}

function initializeSearchShortcut() {
    const searchInput = document.getElementById('search-input');
    const shortcutHint = document.getElementById('searchShortcutHint');

    if (!searchInput) {
        return;
    }

    if (shortcutHint) {
        const isMac = /Mac|iPhone|iPad|iPod/.test(window.navigator.platform);
        shortcutHint.textContent = isMac ? '⌘ K' : 'Ctrl K';
    }

    document.addEventListener('keydown', (event) => {
        const activeTag = document.activeElement?.tagName;
        const isTypingContext = ['INPUT', 'TEXTAREA', 'SELECT'].includes(activeTag) || document.activeElement?.isContentEditable;
        const key = event.key.toLowerCase();

        if ((event.metaKey || event.ctrlKey) && key === 'k') {
            event.preventDefault();
            searchInput.focus();
            searchInput.select();
            return;
        }

        if (!isTypingContext && key === '/') {
            event.preventDefault();
            searchInput.focus();
        }
    });
}

document.addEventListener('DOMContentLoaded', () => {
    initializeBootstrapComponents();
    initializePasswordValidation();
    initializeAlertDismissal();
    initializeSearchShortcut();
});
