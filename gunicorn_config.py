#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Configuration Gunicorn pour le déploiement en production
du Portail de Sécurité Tanger Alliance
"""

import multiprocessing
import os

# Environnement
os.environ.setdefault("FLASK_CONFIG", "production")

# Liaison du serveur
bind = "0.0.0.0:5000"

# Nombre de processus worker
workers = multiprocessing.cpu_count() * 2 + 1

# Type de worker
worker_class = "gevent"

# Timeout (secondes)
timeout = 60

# Réessayer après un timeout?
retry_policy = {
    'max_retries': 3,
    'retry_delay': 5
}

# Logs
accesslog = "logs/gunicorn_access.log"
errorlog = "logs/gunicorn_error.log"
loglevel = "info"

# Redémarrage automatique des workers
max_requests = 1000
max_requests_jitter = 100

# Identité et groupes du processus (à définir en production)
# user = 'www-data'
# group = 'www-data'

# Démarrage en daemon (en arrière-plan)
daemon = False

# Répertoire de travail
chdir = os.path.dirname(os.path.abspath(__file__))

# Hooks
def on_starting(server):
    """Log du démarrage du serveur."""
    server.log.info("Démarrage du serveur Gunicorn pour le Portail de Sécurité")

def post_fork(server, worker):
    """Actions après fork d'un worker."""
    server.log.info("Worker spawned (pid: %s)", worker.pid)

def worker_exit(server, worker):
    """Actions à la sortie d'un worker."""
    server.log.info("Worker exited (pid: %s)", worker.pid)
