"""
Script de migration pour ajouter les champs firstname et lastname à la table User.
À exécuter avec Python après avoir arrêté l'application.
"""

import os
import sys
from datetime import datetime

# Ajouter le répertoire parent au chemin pour pouvoir importer l'application
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app, db
from app.models.user import User
from sqlalchemy import Column, String, text

def run_migration():
    """Exécute la migration pour ajouter les champs firstname et lastname."""
    print("Démarrage de la migration pour ajouter les champs prénom et nom...")
    
    app = create_app()
    with app.app_context():
        # Vérifier si les colonnes existent déjà
        inspector = db.inspect(db.engine)
        columns = [col['name'] for col in inspector.get_columns('user')]
        
        if 'firstname' not in columns:
            print("Ajout de la colonne 'firstname'...")
            with db.engine.connect() as conn:
                conn.execute(text('ALTER TABLE user ADD COLUMN firstname VARCHAR(50)'))
                conn.commit()
            print("Colonne 'firstname' ajoutée avec succès!")
        else:
            print("La colonne 'firstname' existe déjà.")
        
        if 'lastname' not in columns:
            print("Ajout de la colonne 'lastname'...")
            with db.engine.connect() as conn:
                conn.execute(text('ALTER TABLE user ADD COLUMN lastname VARCHAR(50)'))
                conn.commit()
            print("Colonne 'lastname' ajoutée avec succès!")
        else:
            print("La colonne 'lastname' existe déjà.")
            
        print("Migration terminée à", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

if __name__ == "__main__":
    run_migration()
