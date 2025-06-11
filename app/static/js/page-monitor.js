/**
 * Page Monitor - Détecte les changements sur la page après chargement
 */
(function() {
  // Enregistrer l'état initial du DOM juste après le chargement
  let initialState = null;
  let monitorActive = false;
  
  // Fonction pour capturer l'état de la page
  function captureState() {
    return document.documentElement.outerHTML;
  }
  
  // Fonction pour comparer les états
  function compareStates(oldState, newState) {
    if (oldState === newState) {
      console.log('[PageMonitor] Aucun changement détecté dans le DOM');
      return [];
    }
    
    // Convertir les états HTML en éléments DOM pour comparaison
    const parser = new DOMParser();
    const oldDoc = parser.parseFromString(oldState, 'text/html');
    const newDoc = parser.parseFromString(newState, 'text/html');
    
    // Récupérer tous les éléments
    const oldElements = oldDoc.querySelectorAll('*');
    const newElements = newDoc.querySelectorAll('*');
    
    // Liste des différences
    const changes = [];
    
    // Vérifier si le nombre d'éléments a changé
    if (oldElements.length !== newElements.length) {
      changes.push(`Nombre d'éléments changé: ${oldElements.length} -> ${newElements.length}`);
    }
    
    // Comparer les classes des éléments (jusqu'à 1000 pour limiter la charge)
    const maxCheck = Math.min(1000, oldElements.length, newElements.length);
    
    for (let i = 0; i < maxCheck; i++) {
      // Vérifier les changements de classe
      if (oldElements[i].className !== newElements[i].className) {
        changes.push(`Élément ${oldElements[i].tagName} (index ${i}): classes modifiées`);
      }
      
      // Vérifier les changements d'attributs
      if (oldElements[i].attributes && newElements[i].attributes) {
        const oldAttrs = oldElements[i].attributes;
        const newAttrs = newElements[i].attributes;
        
        for (let j = 0; j < oldAttrs.length; j++) {
          const attrName = oldAttrs[j].name;
          const oldValue = oldElements[i].getAttribute(attrName);
          const newValue = newElements[i].getAttribute(attrName);
          
          if (oldValue !== newValue) {
            changes.push(`Attribut '${attrName}' modifié sur élément ${oldElements[i].tagName} (index ${i})`);
          }
        }
      }
    }
    
    // Limiter le nombre de changements à signaler
    return changes.slice(0, 20);
  }
  
  // Démarrer le monitoring
  function startMonitoring() {
    console.log('[PageMonitor] Démarrage du monitoring...');
    monitorActive = true;
    
    // Capturer l'état initial
    initialState = captureState();
    console.log('[PageMonitor] État initial capturé');
    
    // Vérifier les changements toutes les secondes pendant 5 secondes
    let checkCount = 0;
    const maxChecks = 5;
    
    const interval = setInterval(() => {
      checkCount++;
      const currentState = captureState();
      const changes = compareStates(initialState, currentState);
      
      if (changes.length > 0) {
        console.warn(`[PageMonitor] Changements détectés à ${checkCount}s:`);
        changes.forEach(change => console.warn(`- ${change}`));
        
        // Essayer d'identifier la source du changement
        console.warn('[PageMonitor] Scripts possiblement responsables:');
        const scripts = document.querySelectorAll('script');
        scripts.forEach(script => {
          if (script.src) {
            console.warn(`- Script externe: ${script.src}`);
          } else if (script.textContent && script.textContent.includes('setTimeout')) {
            console.warn('- Script inline avec setTimeout détecté');
          }
        });
      }
      
      if (checkCount >= maxChecks) {
        clearInterval(interval);
        console.log('[PageMonitor] Monitoring terminé');
        monitorActive = false;
      }
    }, 1000);
  }
  
  // Démarrer le monitoring après le chargement complet de la page
  window.addEventListener('load', () => {
    // Attendre un court instant pour laisser la page se stabiliser
    setTimeout(startMonitoring, 100);
  });
})();
