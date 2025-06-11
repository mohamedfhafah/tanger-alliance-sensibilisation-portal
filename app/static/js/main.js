// Main JavaScript file for the Security Awareness Portal
// Enhanced for modern dashboard integration with Tanger Alliance styling

document.addEventListener('DOMContentLoaded', function() {
    console.log('🚀 Initialisation du Portail de Sécurité - Tanger Alliance');
    
    // Initialize core components
    initializeBootstrapComponents();
    initializePasswordStrength();
    initializeAlertDismissal();
    initializeDashboardEnhancements();
    
    console.log('✅ Composants principaux initialisés');
});

/**
 * Initialize Bootstrap components with enhanced styling
 */
function initializeBootstrapComponents() {
    // Initialize Bootstrap tooltips with custom styling
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl, {
            template: '<div class="tooltip" role="tooltip"><div class="tooltip-arrow"></div><div class="tooltip-inner" style="background-color: #004a99; color: white; border-radius: 8px; font-family: Poppins, sans-serif;"></div></div>'
        });
    });

    // Initialize Bootstrap popovers with custom styling
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    var popoverList = popoverTriggerList.map(function(popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl, {
            template: '<div class="popover" role="tooltip"><div class="popover-arrow"></div><h3 class="popover-header" style="background-color: #004a99; color: white; font-family: Poppins, sans-serif;"></h3><div class="popover-body" style="font-family: Poppins, sans-serif;"></div></div>'
        });
    });
    
    console.log('Bootstrap components initialized with custom styling');
}

/**
 * Enhanced password strength meter
 */
function initializePasswordStrength() {
    const passwordInput = document.getElementById('password');
    const passwordStrength = document.getElementById('password-strength');
    
    if (passwordInput && passwordStrength) {
        passwordInput.addEventListener('input', function() {
            const password = passwordInput.value;
            let strength = 0;
            let feedback = '';
            
            // Enhanced password validation with visual feedback
            if (password.length >= 12) strength += 25;
            if (/[A-Z]/.test(password)) strength += 25;
            if (/[0-9]/.test(password)) strength += 25;
            if (/[^A-Za-z0-9]/.test(password)) strength += 25;
            
            // Smooth animation for strength meter
            passwordStrength.style.transition = 'width 0.3s ease, background-color 0.3s ease';
            passwordStrength.style.width = strength + '%';
            
            // Enhanced color scheme matching Tanger Alliance colors
            passwordStrength.classList.remove('bg-danger', 'bg-warning', 'bg-success');
            if (strength < 50) {
                passwordStrength.classList.add('bg-danger');
                feedback = 'Faible - Ajoutez plus de caractères';
            } else if (strength < 75) {
                passwordStrength.classList.add('bg-warning');
                feedback = 'Moyen - Presque parfait';
            } else {
                passwordStrength.classList.add('bg-success');
                feedback = 'Fort - Excellent mot de passe';
            }
            
            // Update feedback text if element exists
            const feedbackElement = document.getElementById('password-feedback');
            if (feedbackElement) {
                feedbackElement.textContent = feedback;
                feedbackElement.style.fontFamily = 'Poppins, sans-serif';
            }
        });
    }
    
    console.log('Password strength meter initialized with enhanced styling');
}

/**
 * Enhanced alert dismissal with smooth animations
 */
function initializeAlertDismissal() {
    // Enhanced auto-dismissal for alerts with smooth fade-out
    setTimeout(function() {
        document.querySelectorAll('.alert:not(.alert-feedback):not(.alert-danger)').forEach(function(alert) {
            alert.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
            alert.style.opacity = '0';
            alert.style.transform = 'translateY(-10px)';
            
            setTimeout(function() {
                if (alert.parentNode) {
                    alert.parentNode.removeChild(alert);
                }
            }, 500);
        });
    }, 4000);
    
    console.log('Enhanced alert dismissal initialized');
}

/**
 * Initialize dashboard-specific enhancements
 */
function initializeDashboardEnhancements() {
    // Add smooth scroll behavior for navigation
    document.documentElement.style.scrollBehavior = 'smooth';
    
    // Enhance form controls with focus animations
    document.querySelectorAll('.form-control, .form-select').forEach(function(input) {
        input.addEventListener('focus', function() {
            this.style.transform = 'scale(1.02)';
            this.style.transition = 'transform 0.2s ease, box-shadow 0.2s ease';
        });
        
        input.addEventListener('blur', function() {
            this.style.transform = 'scale(1)';
        });
    });
    
    // Add hover effects to cards
    document.querySelectorAll('.card').forEach(function(card) {
        card.addEventListener('mouseenter', function() {
            this.style.transition = 'transform 0.3s ease, box-shadow 0.3s ease';
        });
    });
    
    // Enhanced button interactions
    document.querySelectorAll('.btn').forEach(function(button) {
        button.addEventListener('mousedown', function() {
            this.style.transform = 'scale(0.98)';
        });
        
        button.addEventListener('mouseup', function() {
            this.style.transform = 'scale(1)';
        });
        
        button.addEventListener('mouseleave', function() {
            this.style.transform = 'scale(1)';
        });
    });
    
    console.log('Dashboard enhancements initialized');
}

// ... (reste du fichier inchangé, y compris Chart.js, fetch, etc.)
