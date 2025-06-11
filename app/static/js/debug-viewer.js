/**
 * Debug Viewer - Outil pour diagnostiquer les changements de DOM en temps réel
 */
(function() {
  // Attendre que le DOM soit complètement chargé
  document.addEventListener('DOMContentLoaded', function() {
    console.log('[Debug Viewer] Chargement terminé, surveillance active...');
    
    // Créer une div de débogage en position fixe
    const debugDiv = document.createElement('div');
    debugDiv.id = 'debug-viewer';
    debugDiv.style.cssText = `
      position: fixed;
      bottom: 10px;
      right: 10px;
      background: rgba(0, 0, 0, 0.8);
      color: #fff;
      padding: 10px;
      border-radius: 5px;
      font-family: monospace;
      font-size: 12px;
      max-width: 300px;
      max-height: 200px;
      overflow: auto;
      z-index: 9999;
      display: none;
    `;
    
    // Bouton pour afficher/masquer
    const toggleButton = document.createElement('button');
    toggleButton.textContent = 'Debug';
    toggleButton.style.cssText = `
      position: fixed;
      bottom: 10px;
      right: 10px;
      background: #007bff;
      color: white;
      border: none;
      border-radius: 5px;
      padding: 5px 10px;
      cursor: pointer;
      z-index: 10000;
    `;
    
    // Log de débogage
    const logDiv = document.createElement('div');
    logDiv.id = 'debug-log';
    debugDiv.appendChild(logDiv);
    
    // Fonction pour ajouter un message au log
    function addLog(message) {
      const log = document.getElementById('debug-log');
      const entry = document.createElement('div');
      entry.innerHTML = `<span>[${new Date().toLocaleTimeString()}]</span> ${message}`;
      log.appendChild(entry);
      
      // Limiter le nombre d'entrées
      if (log.children.length > 20) {
        log.removeChild(log.firstChild);
      }
      
      // Scroll vers le bas
      log.scrollTop = log.scrollHeight;
    }
    
    // Ajouter les éléments au DOM
    document.body.appendChild(debugDiv);
    document.body.appendChild(toggleButton);
    
    // Gérer l'affichage/masquage du debug
    toggleButton.addEventListener('click', function() {
      if (debugDiv.style.display === 'none') {
        debugDiv.style.display = 'block';
        toggleButton.style.display = 'none';
      } else {
        debugDiv.style.display = 'none';
      }
    });
    
    // Fermer le debug
    const closeButton = document.createElement('button');
    closeButton.textContent = 'X';
    closeButton.style.cssText = `
      position: absolute;
      top: 5px;
      right: 5px;
      background: none;
      border: none;
      color: white;
      cursor: pointer;
    `;
    closeButton.addEventListener('click', function() {
      debugDiv.style.display = 'none';
      toggleButton.style.display = 'block';
    });
    debugDiv.appendChild(closeButton);
    
    // Observer les changements dans le DOM
    const observer = new MutationObserver(function(mutations) {
      mutations.forEach(function(mutation) {
        if (mutation.type === 'childList') {
          if (mutation.addedNodes.length > 0) {
            addLog(`<span style="color: #4CAF50;">Élément ajouté dans ${mutation.target.tagName.toLowerCase()}</span>`);
          }
          if (mutation.removedNodes.length > 0) {
            addLog(`<span style="color: #F44336;">Élément supprimé de ${mutation.target.tagName.toLowerCase()}</span>`);
          }
        } else if (mutation.type === 'attributes') {
          addLog(`<span style="color: #2196F3;">Attribut '${mutation.attributeName}' modifié sur ${mutation.target.tagName.toLowerCase()}</span>`);
        }
      });
    });
    
    // Options de l'observer
    const config = { 
      attributes: true, 
      childList: true, 
      subtree: true,
      attributeFilter: ['class', 'style', 'id', 'hidden']
    };
    
    // Démarrer l'observation après un délai pour éviter de capturer les changements initiaux
    setTimeout(() => {
      observer.observe(document.body, config);
      addLog('Surveillance des modifications DOM démarrée');
    }, 2000);
    
    // Enregistrer l'état initial du contenu
    const initialContent = document.body.innerHTML;
    
    // Vérifier les changements après 3 secondes
    setTimeout(() => {
      const currentContent = document.body.innerHTML;
      if (initialContent !== currentContent) {
        addLog('<span style="color: #FFC107; font-weight: bold;">⚠️ Changements détectés dans le DOM après 3s</span>');
      } else {
        addLog('<span style="color: #4CAF50; font-weight: bold;">✓ Aucun changement de DOM après 3s</span>');
      }
    }, 3000);
  });
})();
