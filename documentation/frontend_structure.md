# Structure et Organisation du Frontend

## Arborescence des templates

```
app/templates/
├── base.html                     # Template de base avec structure HTML commune
├── auth/                         # Templates liés à l'authentification
│   ├── login.html                # Page de connexion
│   ├── register.html             # Page d'inscription
│   ├── reset_password.html       # Demande de réinitialisation de mot de passe
│   └── reset_password_token.html # Formulaire de nouveau mot de passe
├── admin/                        # Templates pour l'administration
│   ├── dashboard.html            # Tableau de bord administrateur
│   ├── users.html                # Gestion des utilisateurs
│   ├── modules.html              # Gestion des modules de formation
│   └── statistics.html           # Statistiques globales
├── main/                         # Templates principaux
│   ├── index.html                # Page d'accueil
│   ├── profile.html              # Profil utilisateur
│   └── dashboard.html            # Tableau de bord utilisateur
├── modules/                      # Templates pour les modules de formation
│   ├── index.html                # Liste des modules
│   ├── view.html                 # Vue d'un module
│   └── quiz.html                 # Quiz d'évaluation
├── errors/                       # Pages d'erreur
│   ├── 404.html                  # Page non trouvée
│   ├── 500.html                  # Erreur serveur
│   └── generic.html              # Erreur générique
└── partials/                     # Composants réutilisables
    ├── nav.html                  # Barre de navigation
    ├── footer.html               # Pied de page
    ├── stat_cards.html           # Cartes statistiques
    ├── user_charts.html          # Graphiques utilisateur
    ├── user_progress.html        # Barres de progression
    ├── alerts.html               # Messages d'alerte
    └── pagination.html           # Pagination
```

## Structure du template de base

Le template `base.html` définit la structure commune à toutes les pages:

```html
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}Tanger Alliance - Portail de Sensibilisation à la Sécurité{% endblock %}</title>
    <!-- CSS commun -->
    <link rel="stylesheet" href="{{ url_for('static', filename='css/adminlte.min.css') }}">
    <link rel="stylesheet" href="{{ url_for('static', filename='plugins/fontawesome-free/css/all.min.css') }}">
    {% block styles %}{% endblock %}
</head>
<body class="hold-transition sidebar-mini">
    <div class="wrapper">
        {% include 'partials/nav.html' %}
        
        <!-- Contenu principal -->
        <div class="content-wrapper">
            {% include 'partials/alerts.html' %}
            {% block content %}{% endblock %}
        </div>
        
        {% include 'partials/footer.html' %}
    </div>
    
    <!-- JavaScript commun -->
    <script src="{{ url_for('static', filename='plugins/jquery/jquery.min.js') }}"></script>
    <script src="{{ url_for('static', filename='plugins/bootstrap/js/bootstrap.bundle.min.js') }}"></script>
    <script src="{{ url_for('static', filename='js/adminlte.min.js') }}"></script>
    {% block scripts %}{% endblock %}
</body>
</html>
```

## Organisation des assets statiques

```
app/static/
├── css/
│   ├── adminlte.min.css          # Framework CSS AdminLTE
│   └── custom.css                # Styles personnalisés
├── js/
│   ├── adminlte.min.js           # JavaScript d'AdminLTE
│   ├── chart.min.js              # Bibliothèque de graphiques
│   └── custom.js                 # Scripts personnalisés
├── plugins/                      # Plugins tiers
│   ├── bootstrap/
│   ├── fontawesome-free/
│   ├── chart.js/
│   └── ...
└── img/
    ├── logo.png                  # Logo Tanger Alliance
    ├── favicon.ico               # Favicon
    └── ...
```

## Composants d'interface utilisateur

Le frontend utilise plusieurs composants d'interface réutilisables:

1. **Stat Cards**: Affichage des statistiques clés sous forme de cartes
2. **Graphiques**: Visualisation des données avec Chart.js
3. **Barres de progression**: Suivi de l'avancement
4. **Tables de données**: Affichage des informations tabulaires
5. **Formulaires**: Saisie et validation des données

Ces composants sont implémentés sous forme de macros Jinja2 pour faciliter leur réutilisation.
