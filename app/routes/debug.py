# Route de débogage pour résoudre les problèmes de rendu
from flask import Blueprint, render_template, request, current_app, send_from_directory
import os

debug = Blueprint('debug', __name__)

@debug.route('/no-js-view')
def no_js_view():
    """Affiche une page sans JavaScript en prenant l'URL comme paramètre"""
    target_url = request.args.get('url', '')
    if not target_url:
        return "Veuillez spécifier une URL à visualiser", 400
    
    # Récupérer le contenu HTML
    import requests
    try:
        response = requests.get(target_url)
        html = response.text
        
        # Supprimer tous les scripts
        html = html.replace('<script', '<!-- SCRIPT REMOVED')
        html = html.replace('</script>', 'SCRIPT REMOVED -->')
        
        return html
    except Exception as e:
        return f"Erreur lors de la récupération de la page: {str(e)}", 500

