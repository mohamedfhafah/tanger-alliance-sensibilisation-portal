# Rapport de configuration CSRF

Date : 2025-06-04

## 1. Configuration actuelle

- **WTF_CSRF_ENABLED** : True (activé par défaut)
- **SECRET_KEY** : utilisé pour signer le token CSRF (`app.config['SECRET_KEY']`)
- **Session cookie** :
  - `SESSION_COOKIE_HTTPONLY` : True par défaut (protége contre l'accès JS)
  - `SESSION_COOKIE_SECURE` : False en développement (à passer à True en production)
  - `SESSION_COOKIE_SAMESITE` : Lax par défaut (empêche envoi croisé dans la plupart des requêtes)
- **CSRF token** :
  - Généré à chaque requête et stocké dans la session
  - Injecté via `{{ csrf_token() }}` dans un `<meta>` ou dans les formulaires
  - Validé côté serveur via `flask_wtf.CSRFProtect`

## 2. Bonnes pratiques et recommandations

1. **Forcer les cookies sécurisés en production** :
   - `app.config['SESSION_COOKIE_SECURE'] = True` (HTTPS uniquement)
   - `app.config['REMEMBER_COOKIE_SECURE'] = True`
2. **Renforcer SameSite** :
   - Passer à `SESSION_COOKIE_SAMESITE = 'Strict'` pour bloquer totalement le cross-site
3. **Limiter la portée du cookie CSRF** :
   - Utiliser un cookie dédié `_csrf_token` avec attributs `HttpOnly; Secure; SameSite=Strict` si besoin
4. **Configurer CSRF_TRUSTED_ORIGINS** (Flask-WTF ≥1.1.0) :
   - Définir `app.config['WTF_CSRF_TRUSTED_ORIGINS'] = ['https://votre-domaine.com']`
5. **Double submit cookie (optionnel)** :
   - Émettre un cookie CSRF et vérifier qu'il correspond à l'en-tête X-CSRFToken
6. **Limiter le temps de vie du token** (rafraîchissement régulier) pour réduire la fenêtre d’attaque
7. **Monitorer et logger** :
   - Conserver les logs détaillés des échecs CSRF (handlers dans `app/__init__.py`)
   - Alerting sur un nombre élevé d’échecs

## 3. Tests et validations

- Vérifier que tous les formulaires POST incluent un champ CSRF valide
- Tester les requêtes AJAX en supprimant ou modifiant le header `X-CSRFToken` -> 400
- Vérifier que les cookies portent bien `HttpOnly; Secure; SameSite` en environnement production
- Scanner avec un outil de sécurité (OWASP ZAP) pour vérifier absence de vulnérabilités CSRF

---

*Fin du rapport.*
