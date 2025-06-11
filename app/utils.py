import os
import secrets
from PIL import Image, UnidentifiedImageError
from flask import current_app, flash, redirect, url_for
from werkzeug.utils import secure_filename
from functools import wraps
from flask_login import current_user
import os

def save_profile_picture(picture_data):
    """Sauvegarde la photo de profil avec un nom aléatoire et la redimensionne"""
    # Générer un nom de fichier aléatoire pour éviter les collisions
    random_hex = secrets.token_hex(8)
    # Sanitize filename to prevent path traversal
    filename = secure_filename(picture_data.filename)
    _, file_ext = os.path.splitext(filename)
    file_ext = file_ext.lower()
    # Autoriser uniquement les extensions d'images
    if file_ext not in ['.jpg', '.jpeg', '.png']:
        raise ValueError('Format de fichier non supporté.')
    picture_filename = random_hex + file_ext
    
    # Chemin de sauvegarde
    pictures_dir = os.path.join(current_app.root_path, 'static/profile_pics')
    # Créer le dossier s'il n'existe pas
    if not os.path.exists(pictures_dir):
        os.makedirs(pictures_dir)
    
    picture_path = os.path.join(pictures_dir, picture_filename)
    
    # Vérifier que c'est une image valide
    stream = picture_data.stream
    try:
        img = Image.open(stream)
        img.verify()
    except UnidentifiedImageError:
        raise ValueError('Image corrompue ou format non valide.')
    # Revenir au début du flux pour redimensionner
    stream.seek(0)
    # Redimensionner pour optimiser le chargement
    output_size = (150, 150)
    img = Image.open(stream)
    img.thumbnail(output_size)
    img.save(picture_path)
    
    return picture_filename

def admin_required(f):
    """Décorateur pour s'assurer que l'utilisateur est admin"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'admin':
            flash('Accès refusé. Privilèges administrateur requis.', 'danger')
            return redirect(url_for('main.dashboard'))
        return f(*args, **kwargs)
    return decorated_function
