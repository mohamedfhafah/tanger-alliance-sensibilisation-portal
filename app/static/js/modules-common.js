/**
 * JavaScript commun pour tous les modules de formation
 * Gère la navigation, la progression, les notifications et la sauvegarde
 */

class ModuleManager {
    constructor(moduleId, totalSections, moduleType = 'default') {
        this.moduleId = moduleId;
        this.totalSections = totalSections;
        this.moduleType = moduleType;
        this.completedSections = new Set();
        this.csrfToken = null;
        
        this.init();
    }
    
    /**
     * Initialisation du gestionnaire de module
     */
    init() {
        this.initializeBootstrap();
        this.setupImageErrorHandling();
        this.setupTabManagement();
        this.getCsrfToken();
        this.restoreProgress();
        this.updateProgress();
    }
    
    /**
     * Initialisation des composants Bootstrap
     */
    initializeBootstrap() {
        $(document).ready(() => {
            $('[data-toggle="tooltip"]').tooltip();
            $('.nav-tabs a').on('click', (e) => {
                e.preventDefault();
                $(e.target).tab('show');
                this.updateProgress();
            });
        });
    }
    
    /**
     * Gestion des erreurs d'images
     */
    setupImageErrorHandling() {
        $('img').on('error', function() {
            $(this).attr('src', '/static/images/placeholder.png');
            $(this).attr('alt', 'Image non disponible');
        });
    }
    
    /**
     * Gestion des onglets avec sauvegarde de l'état
     */
    setupTabManagement() {
        // Sauvegarder l'onglet actif
        $('.nav-link').on('click', function() {
            localStorage.setItem(`activeTab_module_${this.moduleId}`, $(this).attr('href'));
        }.bind(this));
        
        // Restaurer l'onglet actif
        const activeTab = localStorage.getItem(`activeTab_module_${this.moduleId}`);
        if (activeTab) {
            const tabElement = $(`a[href="${activeTab}"]`);
            if (tabElement.length) {
                tabElement.tab('show');
            }
        }
    }
    
    /**
     * Récupération du token CSRF
     */
    getCsrfToken() {
        const csrfMeta = $('meta[name=csrf-token]');
        if (csrfMeta.length) {
            this.csrfToken = csrfMeta.attr('content');
        } else {
            console.error('Token CSRF non trouvé');
        }
    }
    
    /**
     * Mise à jour de la barre de progression
     */
    updateProgress() {
        const completedCount = this.completedSections.size;
        const progressPercentage = Math.round((completedCount / this.totalSections) * 100);
        
        // Mise à jour de la barre de progression
        const progressBar = $('#progress-bar');
        const progressText = $('#progress-text');
        
        if (progressBar.length) {
            progressBar.css('width', progressPercentage + '%')
                      .attr('aria-valuenow', progressPercentage);
        }
        
        if (progressText.length) {
            progressText.text(`${completedCount} section(s) terminée(s) sur ${this.totalSections}`);
        }
        
        // Afficher le quiz si toutes les sections sont terminées
        if (completedCount === this.totalSections) {
            this.showQuizSection();
        }
        
        // Sauvegarder la progression
        this.saveProgressToStorage();
    }
    
    /**
     * Marquer une section comme terminée
     */
    markSectionComplete(sectionId, nextSectionId = null) {
        // Vérifier le token CSRF
        if (!this.csrfToken) {
            Swal.fire({
                title: 'Erreur',
                text: 'Session invalide ou expirée. Veuillez rafraîchir la page.',
                icon: 'error'
            });
            return;
        }
        
        // Ajouter la section aux sections terminées
        this.completedSections.add(sectionId);
        
        // Ajouter un badge visuel à l'onglet
        this.addCompletedBadge(sectionId);
        
        // Mettre à jour la progression
        this.updateProgress();
        
        // Afficher une notification de succès
        this.showSuccessNotification();
        
        // Naviguer vers la section suivante
        if (nextSectionId) {
            setTimeout(() => {
                this.navigateToSection(nextSectionId);
            }, 1500);
        }
        
        // Sauvegarder sur le serveur
        this.saveProgressToServer(sectionId);
        
        // Update progress bar immediately
        this.updateProgress();
    }

    /**
     * Ajouter un badge de section terminée
     */
    addCompletedBadge(sectionId) {
        const tab = $(`#${sectionId}-tab`);
        if (tab.length && !tab.find('.completed-badge').length) {
            const badge = $('<span class="completed-badge"><i class="fas fa-check-circle"></i> Terminé</span>');
            tab.append(badge);
        }
    }
    
    /**
     * Afficher une notification de succès
     */
    showSuccessNotification() {
        Swal.fire({
            title: 'Section terminée !',
            text: 'Félicitations ! Vous avez terminé cette section.',
            icon: 'success',
            timer: 2000,
            showConfirmButton: false,
            toast: true,
            position: 'top-end'
        });
    }
    
    /**
     * Naviguer vers une section spécifique
     * @param {string} sectionId - L'ID de la section cible
     */
    navigateToSection(sectionId) {
        console.log('Tentative de navigation vers:', sectionId);
        const nextTab = $(`#${sectionId}-tab`);
        console.log('Onglet trouvé:', nextTab.length > 0, nextTab);
        
        if (nextTab.length) {
            // Désactiver l'onglet actuel
            $('.nav-link.active').removeClass('active');
            $('.tab-pane.active').removeClass('active show');
            
            // Activer le nouvel onglet
            nextTab.addClass('active');
            $(`#${sectionId}`).addClass('active show');
            
            // Utiliser la méthode Bootstrap pour s'assurer que tout fonctionne
            nextTab.tab('show');
            
            console.log('Navigation terminée vers:', sectionId);
        } else {
            console.error('Onglet non trouvé pour sectionId:', sectionId);
        }
    }
    
    /**
     * Afficher la section quiz
     */
    showQuizSection() {
        // show the quiz button container
        $('#quiz-button-container').removeClass('d-none');
        // show a dedicated quiz tab if exists
        const quizTab = $('#quiz-tab');
        if (quizTab.length) quizTab.parent().removeClass('d-none');
    }
    
    /**
     * Sauvegarder la progression sur le serveur
     */
    saveProgressToServer(sectionId) {
        if (!this.csrfToken) {
            console.error('Token CSRF manquant');
            return;
        }
        
        const data = {
            module_id: this.moduleId,
            section: sectionId,
            status: 'completed'
        };
        
        fetch('/modules/update-progress', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': this.csrfToken
            },
            body: JSON.stringify(data)
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Erreur réseau: ' + response.statusText);
            }
            return response.json();
        })
        .then(data => {
            if (!data.success) {
                console.error('Erreur lors de la sauvegarde:', data.message);
            }
        })
        .catch(error => {
            console.error('Erreur lors de la sauvegarde:', error);
        });
    }
    
    /**
     * Sauvegarder la progression dans le localStorage
     */
    saveProgressToStorage() {
        const progressData = {
            completedSections: Array.from(this.completedSections),
            timestamp: Date.now()
        };
        localStorage.setItem(`module_progress_${this.moduleId}`, JSON.stringify(progressData));
    }
    
    /**
     * Restaurer la progression depuis le localStorage
     */
    restoreProgress() {
        const savedProgress = localStorage.getItem(`module_progress_${this.moduleId}`);
        if (savedProgress) {
            try {
                const progressData = JSON.parse(savedProgress);
                this.completedSections = new Set(progressData.completedSections || []);
                
                // Restaurer les badges visuels
                this.completedSections.forEach(sectionId => {
                    this.addCompletedBadge(sectionId);
                });
            } catch (error) {
                console.error('Erreur lors de la restauration de la progression:', error);
            }
        }
    }
    
    /**
     * Gestion de la progression des checklists
     */
    setupChecklistProgress() {
        const checkboxes = $('input[type="checkbox"]');
        
        const updateChecklistProgress = () => {
            const checked = $('input[type="checkbox"]:checked').length;
            const total = checkboxes.length;
            const percentage = total > 0 ? (checked / total) * 100 : 0;
            
            // Mise à jour visuelle de la progression
            const checklistProgress = $('#checklist-progress');
            if (checklistProgress.length) {
                checklistProgress.css('width', percentage + '%')
                               .attr('aria-valuenow', percentage);
            }
            
            // Message de félicitations à 80%
            if (percentage >= 80 && checked > 0) {
                console.log('Félicitations! Vous maîtrisez les concepts de ce module.');
            }
        };
        
        checkboxes.on('change', updateChecklistProgress);
        updateChecklistProgress(); // Initialiser
    }
    
    /**
     * Réinitialiser la progression du module
     */
    resetProgress() {
        this.completedSections.clear();
        localStorage.removeItem(`module_progress_${this.moduleId}`);
        localStorage.removeItem(`activeTab_module_${this.moduleId}`);
        
        // Supprimer les badges visuels
        $('.completed-badge').remove();
        
        // Réactiver les boutons
        $('.btn-info, .btn-primary').prop('disabled', false);
        
        // Masquer le quiz
        $('#quiz-section, #quiz-button-container').hide();
        
        // Mettre à jour la progression
        this.updateProgress();
    }
    
    /**
     * Obtenir le statut de progression
     */
    getProgressStatus() {
        return {
            completedSections: Array.from(this.completedSections),
            totalSections: this.totalSections,
            progressPercentage: Math.round((this.completedSections.size / this.totalSections) * 100),
            isComplete: this.completedSections.size === this.totalSections
        };
    }
}

// Fonctions utilitaires globales
window.ModuleUtils = {
    /**
     * Formater une date
     */
    formatDate: function(date) {
        return new Intl.DateTimeFormat('fr-FR', {
            year: 'numeric',
            month: 'long',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        }).format(date);
    },
    
    /**
     * Valider un email
     */
    validateEmail: function(email) {
        const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return re.test(email);
    },
    
    /**
     * Débounce une fonction
     */
    debounce: function(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    },
    
    /**
     * Copier du texte dans le presse-papiers
     */
    copyToClipboard: function(text) {
        if (navigator.clipboard) {
            return navigator.clipboard.writeText(text);
        } else {
            // Fallback pour les navigateurs plus anciens
            const textArea = document.createElement('textarea');
            textArea.value = text;
            document.body.appendChild(textArea);
            textArea.select();
            document.execCommand('copy');
            document.body.removeChild(textArea);
            return Promise.resolve();
        }
    }
};

// Fonction globale pour la compatibilité avec les anciens modules
window.markSectionComplete = function(sectionId, nextSectionId, moduleId) {
    if (window.moduleManager) {
        window.moduleManager.markSectionComplete(sectionId, nextSectionId);
    } else {
        console.error('ModuleManager non initialisé');
    }
};

// Export pour les modules ES6
if (typeof module !== 'undefined' && module.exports) {
    module.exports = ModuleManager;
}