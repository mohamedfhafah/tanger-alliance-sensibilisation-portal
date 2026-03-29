// Fonction pour définir le thème sans modifier les éléments DOM
function setThemeOnly(themeName) {
  localStorage.setItem('theme', themeName);
  document.documentElement.setAttribute('data-theme', themeName);
  document.dispatchEvent(new CustomEvent('theme:changed', { detail: { theme: themeName } }));
}

// Fonction pour définir le thème et mettre à jour l'interface utilisateur
function setTheme(themeName) {
  setThemeOnly(themeName);
  
  // Vérifier si l'élément theme-toggle existe avant d'essayer d'y accéder
  const themeToggle = document.getElementById('theme-toggle');
  if (themeToggle) {
    themeToggle.checked = (themeName === 'dark');
  }
}

// Fonction pour mettre à jour l'icône du bouton de mode sombre
function updateDarkModeButtonIcon(isDarkMode) {
  const darkModeToggle = document.getElementById('darkModeToggle');
  if (darkModeToggle) {
    // Sélectionner l'icône dans le bouton
    const icon = darkModeToggle.querySelector('i');
    if (icon) {
      if (isDarkMode) {
        // Mode sombre actif : afficher l'icône du soleil pour revenir au mode clair
        icon.className = 'fas fa-sun';
        darkModeToggle.setAttribute('title', 'Passer en mode clair');
      } else {
        // Mode clair actif : afficher l'icône de la lune pour passer en mode sombre
        icon.className = 'fas fa-moon';
        darkModeToggle.setAttribute('title', 'Passer en mode sombre');
      }
    }
  }
}

// Fonction pour basculer entre les thèmes
function toggleTheme() {
  const isDarkMode = localStorage.getItem('theme') === 'dark';
  if (isDarkMode) {
    setTheme('light');
    updateDarkModeButtonIcon(false);
  } else {
    setTheme('dark');
    updateDarkModeButtonIcon(true);
  }
}

// Fonction pour initialiser le thème en toute sécurité
function initTheme() {
  let themeName = 'light'; // Thème par défaut
  
  // Vérifier si l'utilisateur a une préférence enregistrée
  if (localStorage.getItem('theme')) {
    themeName = localStorage.getItem('theme');
  } 
  // Sinon, vérifier les préférences système
  else if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
    themeName = 'dark';
  }
  
  // Appliquer le thème sans toucher aux éléments DOM qui pourraient ne pas être chargés
  setThemeOnly(themeName);
  
  // Utiliser DOMContentLoaded pour s'assurer que tous les éléments sont chargés
  document.addEventListener('DOMContentLoaded', function() {
    // Mettre à jour l'icône du bouton de mode sombre
    updateDarkModeButtonIcon(themeName === 'dark');
    
    // Ajouter un écouteur d'événement sur le bouton de basculement de thème
    const darkModeToggle = document.getElementById('darkModeToggle');
    if (darkModeToggle) {
      darkModeToggle.addEventListener('click', function(e) {
        e.preventDefault();
        toggleTheme();
      });
    }
  });
}

// Initialiser le thème immédiatement
initTheme();

// Ajouter un écouteur pour les changements de préférence système
window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', e => {
  if (!localStorage.getItem('theme')) {
    setTheme(e.matches ? 'dark' : 'light');
  }
});
