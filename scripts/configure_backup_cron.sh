#!/bin/bash
# Script pour configurer une tâche cron de sauvegarde automatique
# Pour le Portail de Sécurité Tanger Alliance

# Dossier racine du projet
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SCRIPTS_DIR="$PROJECT_ROOT/scripts"
VENV_DIR="$PROJECT_ROOT/venv"
PYTHON_PATH="$VENV_DIR/bin/python"

# Vérification que le script de sauvegarde existe
if [ ! -f "$SCRIPTS_DIR/backup_database.py" ]; then
    echo "Erreur: Le script de sauvegarde n'existe pas dans $SCRIPTS_DIR"
    exit 1
fi

# Vérification que l'environnement virtuel est activé
if [ ! -f "$PYTHON_PATH" ]; then
    echo "Erreur: L'environnement virtuel n'existe pas dans $VENV_DIR"
    exit 1
fi

# Création de la commande cron
BACKUP_COMMAND="cd $PROJECT_ROOT && $PYTHON_PATH $SCRIPTS_DIR/backup_database.py --db-type \$(grep db_type $PROJECT_ROOT/backup_config.ini | cut -d= -f2 | tr -d ' ') --source \$(grep source $PROJECT_ROOT/backup_config.ini | cut -d= -f2 | tr -d ' ') --backup-dir \$(grep backup_dir $PROJECT_ROOT/backup_config.ini | cut -d= -f2 | tr -d ' ') --retention \$(grep retention $PROJECT_ROOT/backup_config.ini | cut -d= -f2 | tr -d ' ')"

# Création du fichier cron temporaire
CRON_FILE=$(mktemp)
crontab -l > $CRON_FILE 2>/dev/null || true

# Vérifie si la commande est déjà présente
if ! grep -q "backup_database.py" $CRON_FILE; then
    # Ajoute la tâche cron pour s'exécuter tous les jours à 3h du matin
    echo "0 3 * * * $BACKUP_COMMAND >> $PROJECT_ROOT/backups/backup.log 2>&1" >> $CRON_FILE
    
    # Installe la nouvelle configuration cron
    crontab $CRON_FILE
    echo "Tâche cron de sauvegarde installée pour s'exécuter quotidiennement à 3h du matin"
else
    echo "Une tâche cron de sauvegarde est déjà configurée"
fi

# Nettoyage du fichier temporaire
rm $CRON_FILE

echo "-----------------------------------"
echo "Configuration de la sauvegarde complétée"
echo "Sauvegarde automatique configurée pour s'exécuter chaque jour à 3h du matin"
echo "Logs des sauvegardes dans: $PROJECT_ROOT/backups/backup.log"
echo "-----------------------------------"

# Création du répertoire de sauvegarde s'il n'existe pas
BACKUP_DIR="$PROJECT_ROOT/$(grep backup_dir $PROJECT_ROOT/backup_config.ini | cut -d= -f2 | tr -d ' ')"
mkdir -p $BACKUP_DIR
echo "Répertoire de sauvegarde créé: $BACKUP_DIR"

# Rendre les scripts exécutables
chmod +x "$SCRIPTS_DIR/backup_database.py"
echo "Script de sauvegarde rendu exécutable"

# Exécution d'une sauvegarde de test
echo "Exécution d'une sauvegarde de test..."
$BACKUP_COMMAND
if [ $? -eq 0 ]; then
    echo "Sauvegarde de test réussie!"
else
    echo "Erreur lors de la sauvegarde de test. Vérifiez les logs pour plus de détails."
fi
