from flask import Blueprint, render_template, flash, redirect, url_for, request, jsonify
from markupsafe import Markup
from flask_login import current_user, login_required
from datetime import datetime, timezone
from sqlalchemy import func
from app import db
from app.models.user import User
from app.models.module import Module, UserProgress
from app.models.simulation_rating import SimulationRating
from app.routes.main import SIMULATIONS
from app.forms import PhishingReportForm

security = Blueprint('security', __name__)

@security.route('/security-alerts')
@login_required
def alerts():
    """Affiche les alertes de sécurité récentes."""
    # Ces données seraient normalement issues de la base de données
    alerts = [
        {
            'title': 'Tentative de phishing Microsoft 365',
            'description': 'Une campagne de phishing ciblant les utilisateurs Microsoft 365 a été détectée.',
            'severity': 'high',
            'date': datetime.now(timezone.utc).strftime('%d/%m/%Y')
        },
        {
            'title': 'Mise à jour de sécurité Windows',
            'description': 'Microsoft a publié des correctifs importants pour Windows. Veuillez mettre à jour vos systèmes.',
            'severity': 'medium',
            'date': datetime.now(timezone.utc).strftime('%d/%m/%Y')
        },
        {
            'title': 'Nouvelle politique de mots de passe',
            'description': 'La politique de mots de passe de Tanger Alliance a été mise à jour. Consultez le module correspondant.',
            'severity': 'info',
            'date': datetime.now(timezone.utc).strftime('%d/%m/%Y')
        }
    ]
    
    return render_template('security/alerts.html', 
                          title='Alertes de sécurité',
                          alerts=alerts)

@security.route('/report-incident', methods=['GET', 'POST'])
@login_required
def report_incident():
    """Permet aux utilisateurs de signaler un incident de sécurité."""
    if request.method == 'POST':
        incident_type = request.form.get('incident_type')
        description = request.form.get('description')
        
        # Ici, on pourrait implémenter l'envoi d'un email ou l'enregistrement en base
        
        flash(Markup("Merci d'avoir signalé cet incident. Notre équipe de sécurité va l'examiner."), 'success')
        return redirect(url_for('main.dashboard'))
    
    incident_types = [
        ('phishing', 'Tentative de phishing'),
        ('malware', 'Malware ou virus'),
        ('unauthorized', 'Accès non autorisé'),
        ('data_breach', 'Fuite de données'),
        ('other', 'Autre')
    ]
    
    return render_template('security/report_incident.html', 
                          title='Signaler un incident',
                          incident_types=incident_types)

@security.route('/security-resources')
@login_required
def resources():
    """Affiche des ressources de sécurité supplémentaires."""
    resources = [
        {
            'title': 'Guide de sécurité des mots de passe',
            'description': 'Comment créer et gérer des mots de passe forts',
            'url': '#',
            'type': 'pdf'
        },
        {
            'title': 'Détection du phishing',
            'description': 'Signes révélateurs d\'une tentative de phishing',
            'url': '#',
            'type': 'video'
        },
        {
            'title': 'Sécurité mobile',
            'description': 'Bonnes pratiques pour protéger vos appareils mobiles',
            'url': '#',
            'type': 'article'
        }
    ]
    
    return render_template('security/resources.html', 
                          title='Ressources de sécurité',
                          resources=resources)

@security.route('/security-policy')
@login_required
def policy():
    """Affiche la politique de sécurité de Tanger Alliance."""
    return render_template('security/policy.html', 
                          title='Politique de sécurité')

@security.route('/simulations')
@login_required
def simulations():
    """Affiche les simulations de sécurité disponibles."""
    # For compatibility with tests that expect /security/simulations
    # We can reuse the SIMULATIONS data from main blueprint
    from app.models.simulation import SimulationAttempt
    from sqlalchemy import func
    
    user_stats = {}
    for sim in SIMULATIONS:
        stats = db.session.query(
            func.count(SimulationAttempt.id),
            func.sum(SimulationAttempt.success.cast(db.Integer)),
            func.max(SimulationAttempt.timestamp)
        ).filter(
            SimulationAttempt.user_id==current_user.id,
            SimulationAttempt.simulation_slug==sim['slug']
        ).first()
        total = stats[0] or 0
        success_count = stats[1] or 0
        last_success = db.session.query(func.max(SimulationAttempt.timestamp)).filter(
            SimulationAttempt.user_id==current_user.id,
            SimulationAttempt.simulation_slug==sim['slug'],
            SimulationAttempt.success==True
        ).scalar()
        user_stats[sim['slug']] = {
            'total': total,
            'success': success_count,
            'rate': int(100*success_count/total) if total else 0,
            'completed': success_count > 0,
            'last_success': last_success
        }
    
    return render_template('simulations/list.html', 
                          title='Simulations de sécurité', 
                          simulations=SIMULATIONS, 
                          user_stats=user_stats)

@security.route('/contact-security')
@login_required
def contact():
    """Affiche les informations de contact de l'équipe de sécurité."""
    contacts = [
        {
            'name': 'Équipe SOC',
            'email': 'soc@tangeralliance.ma',
            'phone': '+212 5XX XX XX XX',
            'for': 'Incidents urgents'
        },
        {
            'name': 'Responsable de la sécurité',
            'email': 'ciso@tangeralliance.ma',
            'phone': '+212 5XX XX XX XX',
            'for': 'Questions générales'
        }
    ]
    
    return render_template('security/contact.html', 
                          title='Contact sécurité',
                          contacts=contacts)
