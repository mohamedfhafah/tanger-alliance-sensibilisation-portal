# Guide de déploiement en production

Ce document détaille les étapes pour déployer le Portail de Sécurité Tanger Alliance en environnement de production.

## Prérequis

- Serveur Linux (recommandé : Ubuntu Server 20.04 LTS ou plus récent)
- Python 3.8+ avec pip et virtualenv
- PostgreSQL 12+ installé et configuré
- Nginx pour servir de reverse proxy
- Certbot pour les certificats SSL Let's Encrypt
- Accès root ou sudo au serveur

## 1. Préparation du serveur

### Mise à jour du système
```bash
sudo apt update
sudo apt upgrade -y
```

### Installation des dépendances
```bash
sudo apt install -y python3-pip python3-venv postgresql nginx certbot python3-certbot-nginx
```

### Création de la base de données PostgreSQL
```bash
sudo -u postgres psql -c "CREATE DATABASE portail_securite;"
sudo -u postgres psql -c "CREATE USER portail WITH PASSWORD 'votre_mot_de_passe_securise';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE portail_securite TO portail;"
```

## 2. Installation de l'application

### Créer l'utilisateur de service (optionnel mais recommandé)
```bash
sudo useradd -m -s /bin/bash portail_app
```

### Cloner le dépôt et configurer
```bash
# Créer le répertoire d'application
sudo mkdir -p /opt/portail_securite
sudo chown portail_app:portail_app /opt/portail_securite

# Cloner le dépôt (à adapter selon votre système de gestion de code)
sudo -u portail_app git clone https://votre-depot/portail_securite.git /opt/portail_securite

# Créer et activer l'environnement virtuel
cd /opt/portail_securite
sudo -u portail_app python3 -m venv venv
```

### Variables d'environnement de production
Créez un fichier `.env` à la racine du projet :
```bash
sudo -u portail_app nano /opt/portail_securite/.env
```

Contenu du fichier `.env` :
```
FLASK_CONFIG=production
DATABASE_URL=postgresql://portail:votre_mot_de_passe_securise@localhost:5432/portail_securite
SECRET_KEY=votre_clé_secrète_très_longue_et_aléatoire
MAIL_SERVER=smtp.votre-serveur-mail.com
MAIL_PORT=587
MAIL_USE_TLS=true
MAIL_USERNAME=votre_email@example.com
MAIL_PASSWORD=votre_mot_de_passe_email
```

### Permissions de sécurité
```bash
sudo chown -R portail_app:www-data /opt/portail_securite
sudo chmod -R 750 /opt/portail_securite
sudo chmod 770 /opt/portail_securite/logs /opt/portail_securite/backups
sudo chmod 640 /opt/portail_securite/.env
```

## 3. Déploiement de l'application

### Utilisation du script de déploiement
```bash
cd /opt/portail_securite
sudo -u portail_app bash scripts/deploy_to_production.sh
```

### Configuration manuelle (si le script échoue)

#### Installation des dépendances
```bash
cd /opt/portail_securite
source venv/bin/activate
pip install -r requirements.txt
```

#### Migration de la base de données
```bash
export FLASK_CONFIG=production
alembic upgrade head
```

#### Collecte des fichiers statiques
```bash
mkdir -p static_collected
cp -r app/static/* static_collected/
```

## 4. Configuration du serveur web et du service

### Configuration de Nginx
Créez un fichier de configuration Nginx :
```bash
sudo cp /opt/portail_securite/deploy/nginx_config.conf /etc/nginx/sites-available/portail-securite
```

Modifiez le fichier pour l'adapter à votre environnement :
```bash
sudo nano /etc/nginx/sites-available/portail-securite
```

Activez la configuration :
```bash
sudo ln -s /etc/nginx/sites-available/portail-securite /etc/nginx/sites-enabled/
sudo nginx -t  # Vérifiez la configuration
sudo systemctl reload nginx
```

### Obtention d'un certificat SSL
```bash
sudo certbot --nginx -d portail-securite.tangeralliance.com
```

### Configuration du service systemd
Copiez le fichier de service :
```bash
sudo cp /opt/portail_securite/deploy/portail-securite.service /etc/systemd/system/
```

Activez et démarrez le service :
```bash
sudo systemctl daemon-reload
sudo systemctl enable portail-securite
sudo systemctl start portail-securite
sudo systemctl status portail-securite
```

## 5. Vérification du déploiement

### Journaux de l'application
```bash
sudo tail -f /opt/portail_securite/logs/portail_securite.log
```

### Journaux de Nginx
```bash
sudo tail -f /var/log/nginx/portail_securite_access.log
sudo tail -f /var/log/nginx/portail_securite_error.log
```

### Vérification des sauvegardes
```bash
ls -la /opt/portail_securite/backups
```

## 6. Maintenance et sécurité

### Surveillance des sauvegardes
Ajoutez une tâche cron pour la surveillance :
```bash
sudo crontab -e
```

Ajoutez cette ligne pour vérifier les sauvegardes tous les matins à 8h :
```
0 8 * * * cd /opt/portail_securite && venv/bin/python scripts/monitor_backups.py --backup-dir backups --alert-email admin@tangeralliance.com --config monitoring_config.ini >> logs/backup_monitoring.log 2>&1
```

### Rotation des logs
Configurez logrotate pour éviter que les logs ne remplissent le disque :
```bash
sudo nano /etc/logrotate.d/portail-securite
```

Contenu du fichier :
```
/opt/portail_securite/logs/*.log {
    daily
    rotate 14
    compress
    delaycompress
    missingok
    notifempty
    create 0640 portail_app www-data
}
```

### Sauvegardes distantes
Pour plus de sécurité, configurez une sauvegarde distante des fichiers de sauvegarde :
```bash
sudo apt install -y rclone
# Configurez rclone pour votre fournisseur cloud (Google Drive, Dropbox, etc.)
sudo -u portail_app rclone config

# Créez un script de synchronisation
sudo nano /opt/portail_securite/scripts/sync_backups.sh
```

Contenu du script :
```bash
#!/bin/bash
cd /opt/portail_securite
source venv/bin/activate
rclone sync backups remote:portail-securite-backups --log-file=logs/rclone.log
```

Ajoutez-le au crontab :
```
0 5 * * * bash /opt/portail_securite/scripts/sync_backups.sh
```

## 7. Mise à jour de l'application

Pour déployer une mise à jour :
```bash
cd /opt/portail_securite
sudo -u portail_app git pull
sudo -u portail_app bash scripts/deploy_to_production.sh
sudo systemctl restart portail-securite
```

## Résolution des problèmes courants

### L'application ne démarre pas
Vérifiez les logs :
```bash
sudo systemctl status portail-securite
sudo cat /var/log/syslog | grep portail-securite
```

### Erreurs de base de données
Vérifiez la connectivité à PostgreSQL :
```bash
sudo -u portail_app psql -U portail -h localhost -d portail_securite
```

### Problèmes de permissions
Vérifiez et corrigez les permissions :
```bash
sudo find /opt/portail_securite -type d -exec chmod 750 {} \;
sudo find /opt/portail_securite -type f -exec chmod 640 {} \;
sudo chmod 770 /opt/portail_securite/logs /opt/portail_securite/backups
sudo chmod -R portail_app:www-data /opt/portail_securite
```
