// Main JavaScript file for the Security Awareness Portal

// Wait for DOM to be fully loaded
document.addEventListener('DOMContentLoaded', function() {
    // Initialize Bootstrap tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Initialize Bootstrap popovers
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    var popoverList = popoverTriggerList.map(function(popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });

    // Password strength meter
    const passwordInput = document.getElementById('password');
    const passwordStrength = document.getElementById('password-strength');
    
    if (passwordInput && passwordStrength) {
        passwordInput.addEventListener('input', function() {
            const password = passwordInput.value;
            let strength = 0;
            let feedback = '';
            
            // Check password length
            if (password.length >= 12) {
                strength += 25;
            }
            
            // Check for uppercase letters
            if (/[A-Z]/.test(password)) {
                strength += 25;
            }
            
            // Check for numbers
            if (/[0-9]/.test(password)) {
                strength += 25;
            }
            
            // Check for special characters
            if (/[^A-Za-z0-9]/.test(password)) {
                strength += 25;
            }
            
            // Update strength meter
            passwordStrength.style.width = strength + '%';
            
            // Update color based on strength
            if (strength < 50) {
                passwordStrength.classList.remove('bg-warning', 'bg-success');
                passwordStrength.classList.add('bg-danger');
                feedback = 'Faible';
            } else if (strength < 100) {
                passwordStrength.classList.remove('bg-danger', 'bg-success');
                passwordStrength.classList.add('bg-warning');
                feedback = 'Moyen';
            } else {
                passwordStrength.classList.remove('bg-danger', 'bg-warning');
                passwordStrength.classList.add('bg-success');
                feedback = 'Fort';
            }
            
            // Update feedback text if element exists
            const feedbackElement = document.getElementById('password-feedback');
            if (feedbackElement) {
                feedbackElement.textContent = feedback;
            }
        });
    }

    // Autoclose flash messages after 5 seconds
    const flashMessages = document.querySelectorAll('.alert');
    flashMessages.forEach(function(message) {
        setTimeout(function() {
            const alert = new bootstrap.Alert(message);
            alert.close();
        }, 5000);
    });

    // Module completion confirmation
    const completeButtons = document.querySelectorAll('.btn-complete-module');
    completeButtons.forEach(function(button) {
        button.addEventListener('click', function(event) {
            if (!confirm('Êtes-vous sûr de vouloir marquer ce module comme terminé?')) {
                event.preventDefault();
            }
        });
    });

    // Quiz timer functionality
    const quizTimer = document.getElementById('quiz-timer');
    if (quizTimer) {
        let timeLeft = parseInt(quizTimer.dataset.timeLimit) || 600; // Default 10 minutes
        
        const updateTimer = function() {
            const minutes = Math.floor(timeLeft / 60);
            const seconds = timeLeft % 60;
            
            quizTimer.textContent = `${minutes}:${seconds < 10 ? '0' : ''}${seconds}`;
            
            if (timeLeft <= 0) {
                clearInterval(timerInterval);
                document.getElementById('quiz-form').submit();
            } else {
                timeLeft--;
            }
        };
        
        updateTimer(); // Initial display
        const timerInterval = setInterval(updateTimer, 1000);
    }
});

// Phishing simulation report functionality
function reportPhishing(emailId) {
    fetch('/report-phishing', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': document.querySelector('meta[name="csrf-token"]').getAttribute('content')
        },
        body: JSON.stringify({ email_id: emailId })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert('Merci d\'avoir signalé cet email suspect!');
        } else {
            alert('Une erreur est survenue lors du signalement.');
        }
    })
    .catch(error => {
        console.error('Error:', error);
    });
}

// Chart.js integration for dashboard statistics
function initializeCharts() {
    const progressCtx = document.getElementById('progressChart');
    if (progressCtx) {
        new Chart(progressCtx, {
            type: 'doughnut',
            data: {
                labels: ['Complété', 'En cours', 'Non commencé'],
                datasets: [{
                    data: [25, 25, 50],
                    backgroundColor: ['#198754', '#ffc107', '#6c757d']
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false
            }
        });
    }
    
    const performanceCtx = document.getElementById('performanceChart');
    if (performanceCtx) {
        new Chart(performanceCtx, {
            type: 'bar',
            data: {
                labels: ['Mots de passe', 'Phishing', 'Vulnérabilités', 'Protection des données'],
                datasets: [{
                    label: 'Score (%)',
                    data: [85, 70, 0, 0],
                    backgroundColor: ['#0d6efd', '#0d6efd', '#0d6efd', '#0d6efd']
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 100
                    }
                }
            }
        });
    }
}
