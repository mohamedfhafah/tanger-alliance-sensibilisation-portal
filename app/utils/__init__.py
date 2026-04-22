import os
import secrets
from flask import abort, current_app
from app import db

def save_profile_picture(form_picture):
    """Sauvegarde la photo de profil uploadée sans redimensionnement
    
    Args:
        form_picture: Objet FileStorage de la photo de profil uploadée
        
    Returns:
        str: Nom du fichier de la photo de profil sauvegardée
    """
    # Générer un nom de fichier aléatoire pour éviter les collisions
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_filename = random_hex + f_ext
    
    # Définir le chemin où sauvegarder la photo
    pictures_dir = os.path.join(current_app.root_path, 'static/profile_pics')
    
    # Créer le dossier s'il n'existe pas
    if not os.path.exists(pictures_dir):
        os.makedirs(pictures_dir)
    
    picture_path = os.path.join(pictures_dir, picture_filename)
    
    # Sauvegarder la photo sans redimensionnement
    form_picture.save(picture_path)
    
    # Note: Sans Pillow, nous ne pouvons pas redimensionner l'image
    # Le redimensionnement sera géré par CSS côté client
    
    return picture_filename


def get_or_404(model, object_id):
    """Fetch a model instance with Session.get and raise a 404 if missing."""
    instance = db.session.get(model, object_id)
    if instance is None:
        abort(404)
    return instance
