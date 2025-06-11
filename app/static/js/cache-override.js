// Script pour forcer la désactivation du cache du navigateur
(function() {
    // Si l'URL contient un paramètre de cache buster ou est une URL POST (formulaire), ne pas continuer
    if (window.location.href.indexOf('_nocache=') !== -1) {
        return;
    }
    
    // Ne pas appliquer aux URLs d'évaluation qui doivent être traitées en POST
    if (window.location.href.indexOf('/phishing-simulation/evaluate') !== -1 ||
        window.location.href.indexOf('/quiz/submit') !== -1 ||
        window.location.href.indexOf('/evaluate') !== -1) {
        return;
    }
    
    // Ajouter un timestamp comme paramètre d'URL pour forcer le rechargement
    var nocacheParam = '_nocache=' + Date.now();
    var newUrl;
    
    if (window.location.href.indexOf('?') !== -1) {
        newUrl = window.location.href + '&' + nocacheParam;
    } else {
        newUrl = window.location.href + '?' + nocacheParam;
    }
    
    // Remplacer l'URL actuelle
    window.location.replace(newUrl);
})();