"""
Routes pour les simulations de phishing
Gestion des campagnes, envoi, tracking et résultats
"""

from flask import Blueprint, render_template, flash, redirect, url_for, request, jsonify, current_app
from flask_login import login_required, current_user
from datetime import datetime, timezone, timedelta, time
from sqlalchemy import func, desc, and_
import uuid
import json

from app import db
from app.models.user import User
from app.models.campaign import Campaign, PhishingSimulation, PhishingTarget
from app.models.module import Module
from app.models.simulation import SimulationAttempt
from app.forms import PhishingCampaignForm
from app.utils.decorators import admin_required

phishing = Blueprint('phishing', __name__, url_prefix='/phishing')

# Templates disponibles pour les simulations
PHISHING_TEMPLATES = {
    'fake_shipping_manifest': {
        'name': 'Faux Manifeste d\'Expédition',
        'description': 'Simulation d\'un email frauduleux imitant un manifeste d\'expédition Maersk',
        'template_file': 'phishing_templates/fake_shipping_manifest.html',
        'difficulty': 'intermediate',
        'sector': 'logistics'
    },
    'fake_customs_notification': {
        'name': 'Fausse Notification Douanes',
        'description': 'Simulation d\'une notification frauduleuse des douanes marocaines',
        'template_file': 'phishing_templates/fake_customs_notification.html',
        'difficulty': 'advanced',
        'sector': 'customs'
    },
    'fake_portnet_security_alert': {
        'name': 'Fausse Alerte Sécurité PortNet',
        'description': 'Simulation d\'une alerte de sécurité frauduleuse du système PortNet',
        'template_file': 'phishing_templates/fake_portnet_security_alert.html',
        'difficulty': 'intermediate',
        'sector': 'port_systems'
    }
}

@phishing.route('/campaigns')
@login_required
@admin_required
def campaigns():
    """Liste toutes les campagnes de phishing"""
    campaigns_list = Campaign.query.filter_by(type='Phishing Email').order_by(desc(Campaign.created_at)).all()
    
    # Statistiques pour chaque campagne
    campaign_stats = {}
    for campaign in campaigns_list:
        stats = db.session.query(
            func.count(PhishingTarget.id).label('total_targets'),
            func.sum(PhishingTarget.sent.cast(db.Integer)).label('sent'),
            func.sum(PhishingTarget.opened.cast(db.Integer)).label('opened'),
            func.sum(PhishingTarget.clicked.cast(db.Integer)).label('clicked'),
            func.sum(PhishingTarget.reported.cast(db.Integer)).label('reported')
        ).join(PhishingSimulation).filter(
            PhishingSimulation.campaign_id == campaign.id
        ).first()
        
        campaign_stats[campaign.id] = {
            'total_targets': stats.total_targets or 0,
            'sent': stats.sent or 0,
            'opened': stats.opened or 0,
            'clicked': stats.clicked or 0,
            'reported': stats.reported or 0,
            'click_rate': round((stats.clicked / stats.sent * 100), 1) if stats.sent else 0,
            'report_rate': round((stats.reported / stats.sent * 100), 1) if stats.sent else 0
        }
    
    return render_template('phishing/campaigns.html', 
                         title='Campagnes de Phishing',
                         campaigns=campaigns_list,
                         stats=campaign_stats,
                         templates=PHISHING_TEMPLATES)

@phishing.route('/campaigns/new', methods=['GET', 'POST'])
@login_required
@admin_required
def new_campaign():
    """Créer une nouvelle campagne de phishing"""
    form = PhishingCampaignForm()
    
    # Charger les utilisateurs pour la sélection des cibles
    users = User.query.filter(User.role != 'admin').all()
    departments = db.session.query(User.department).distinct().all()
    department_choices = [(dept[0], dept[0]) for dept in departments if dept[0]]
    user_choices = [(str(user.id), f'{user.firstname} {user.lastname} ({user.department or "N/A"})') for user in users]

    form.template.choices = [(key, value['name']) for key, value in PHISHING_TEMPLATES.items()]
    form.target_departments.choices = department_choices
    form.department.choices = [('', 'Sélectionner un département')] + department_choices
    form.target_users.choices = user_choices
    
    if form.validate_on_submit():
        start_at = (
            datetime.combine(form.start_date.data, time.min, tzinfo=timezone.utc)
            if form.start_date.data
            else datetime.now(timezone.utc)
        )
        end_at = (
            datetime.combine(form.end_date.data, time.max, tzinfo=timezone.utc)
            if form.end_date.data
            else None
        )

        # Créer la campagne
        campaign = Campaign(
            name=form.name.data,
            type='Phishing Email',
            description=form.description.data or '',
            start_date=start_at,
            end_date=end_at,
            status='active'
        )
        db.session.add(campaign)
        db.session.flush()  # Pour obtenir l'ID de la campagne
        
        # Créer la simulation de phishing
        simulation = PhishingSimulation(
            campaign_id=campaign.id,
            title=form.simulation_title.data,
            template=form.template.data,
            description=form.simulation_description.data or ''
        )
        db.session.add(simulation)
        db.session.flush()  # Pour obtenir l'ID de la simulation
        
        # Ajouter les cibles
        target_users = []
        if form.target_all.data:
            target_users = User.query.filter(User.role != 'admin').all()
        elif form.target_departments.data:
            selected_depts = form.target_departments.data
            target_users = User.query.filter(
                and_(User.department.in_(selected_depts), User.role != 'admin')
            ).all()
        elif form.target_users.data:
            user_ids = [int(uid) for uid in form.target_users.data]
            target_users = User.query.filter(User.id.in_(user_ids)).all()
        
        for user in target_users:
            target = PhishingTarget(
                simulation_id=simulation.id,
                user_id=user.id
            )
            db.session.add(target)
        
        db.session.commit()
        
        flash(f'Campagne "{campaign.name}" créée avec succès. {len(target_users)} utilisateurs ciblés.', 'success')
        return redirect(url_for('phishing.campaigns'))
    
    return render_template('phishing/new_campaign.html',
                         title='Nouvelle Campagne de Phishing',
                         form=form,
                         users=users,
                         departments=[d[0] for d in departments if d[0]],
                         templates=PHISHING_TEMPLATES)

@phishing.route('/campaigns/<int:campaign_id>')
@login_required
@admin_required
def campaign_detail(campaign_id):
    """Détails d'une campagne de phishing"""
    campaign = Campaign.query.get_or_404(campaign_id)
    
    # Récupérer les simulations de cette campagne
    simulations = PhishingSimulation.query.filter_by(campaign_id=campaign_id).all()
    
    # Statistiques détaillées
    targets = db.session.query(PhishingTarget, User, PhishingSimulation).join(
        User, PhishingTarget.user_id == User.id
    ).join(
        PhishingSimulation, PhishingTarget.simulation_id == PhishingSimulation.id
    ).filter(
        PhishingSimulation.campaign_id == campaign_id
    ).all()
    
    # Statistiques par département
    dept_stats = db.session.query(
        User.department,
        func.count(PhishingTarget.id).label('total'),
        func.sum(PhishingTarget.clicked.cast(db.Integer)).label('clicked'),
        func.sum(PhishingTarget.reported.cast(db.Integer)).label('reported')
    ).join(User, PhishingTarget.user_id == User.id).join(
        PhishingSimulation, PhishingTarget.simulation_id == PhishingSimulation.id
    ).filter(
        PhishingSimulation.campaign_id == campaign_id
    ).group_by(User.department).all()
    
    return render_template('phishing/campaign_detail.html',
                         title=f'Campagne: {campaign.name}',
                         campaign=campaign,
                         simulations=simulations,
                         targets=targets,
                         dept_stats=dept_stats)

@phishing.route('/simulate/<string:template_key>/<string:token>')
def simulate_email(template_key, token):
    """Affiche le template de phishing avec tracking"""
    # Vérifier si le template existe
    if template_key not in PHISHING_TEMPLATES:
        flash('Template de simulation introuvable.', 'error')
        return redirect(url_for('main.dashboard'))
    
    # Décoder le token pour identifier l'utilisateur et la simulation
    try:
        # Dans un vrai système, vous utiliseriez un système de signature sécurisé
        # Ici, nous utilisons une approche simplifiée
        target = PhishingTarget.query.filter_by(id=int(token)).first()
        if not target:
            flash('Lien de simulation invalide.', 'error')
            return redirect(url_for('main.dashboard'))
        
        # Marquer comme ouvert si pas déjà fait
        if not target.opened:
            target.opened = True
            target.opened_at = datetime.now(timezone.utc)
            db.session.commit()
        
        template_info = PHISHING_TEMPLATES[template_key]
        
        return render_template(template_info['template_file'],
                             title=template_info['name'],
                             target_id=target.id,
                             template_key=template_key)
    
    except (ValueError, TypeError):
        flash('Lien de simulation invalide.', 'error')
        return redirect(url_for('main.dashboard'))

@phishing.route('/click/<int:target_id>')
def handle_click(target_id):
    """Gère le clic sur un lien de phishing"""
    target = PhishingTarget.query.get_or_404(target_id)
    phishing_module = Module.query.filter(Module.title.ilike('%phishing%')).first()
    
    # Marquer comme cliqué
    if not target.clicked:
        target.clicked = True
        target.clicked_at = datetime.now(timezone.utc)
        db.session.commit()
        
        # Enregistrer l'tentative pour les statistiques
        attempt = SimulationAttempt(
            user_id=target.user_id,
            simulation_slug=f"phishing_campaign_{target.simulation.campaign_id}",
            action='clicked_link',
            success=False,  # Cliquer est considéré comme un échec
            feedback='Vous avez cliqué sur un lien de phishing. Attention aux emails suspects!'
        )
        db.session.add(attempt)
        db.session.commit()
    
    # Rediriger vers la page éducative
    return render_template('phishing/educative_click.html',
                         title='Attention - Simulation de Phishing',
                         target=target,
                         phishing_module=phishing_module)

@phishing.route('/report/<int:target_id>')
def handle_report(target_id):
    """Gère le signalement d'un email de phishing"""
    target = PhishingTarget.query.get_or_404(target_id)
    phishing_module = Module.query.filter(Module.title.ilike('%phishing%')).first()
    
    # Marquer comme signalé
    if not target.reported:
        target.reported = True
        target.reported_at = datetime.now(timezone.utc)
        db.session.commit()
        
        # Enregistrer l'tentative pour les statistiques
        attempt = SimulationAttempt(
            user_id=target.user_id,
            simulation_slug=f"phishing_campaign_{target.simulation.campaign_id}",
            action='reported_email',
            success=True,  # Signaler est considéré comme un succès
            feedback='Excellent! Vous avez correctement identifié et signalé cet email de phishing.'
        )
        db.session.add(attempt)
        db.session.commit()
    
    # Rediriger vers la page de félicitations
    return render_template('phishing/educative_report.html',
                         title='Félicitations - Bon Réflexe!',
                         target=target,
                         phishing_module=phishing_module)

@phishing.route('/api/campaign/<int:campaign_id>/send', methods=['POST'])
@login_required
@admin_required
def send_campaign(campaign_id):
    """Envoie les emails de simulation pour une campagne"""
    campaign = Campaign.query.get_or_404(campaign_id)
    
    # Récupérer toutes les cibles non envoyées
    targets = db.session.query(PhishingTarget).join(
        PhishingSimulation
    ).filter(
        PhishingSimulation.campaign_id == campaign_id,
        PhishingTarget.sent == False
    ).all()
    
    if not targets:
        return jsonify({'error': 'Aucune cible à traiter'}), 400
    
    # Dans un vrai système, vous enverriez de vrais emails
    # Ici, nous marquons simplement comme envoyé
    sent_count = 0
    for target in targets:
        # Générer un lien unique pour chaque cible
        simulation_link = url_for('phishing.simulate_email',
                                template_key=target.simulation.template,
                                token=str(target.id),
                                _external=True)
        
        # Marquer comme envoyé
        target.sent = True
        sent_count += 1
        
        # Dans un vrai système, vous utiliseriez Flask-Mail ici
        current_app.logger.info(f'Simulation email sent to user {target.user_id}: {simulation_link}')
    
    # Mettre à jour la date d'envoi de la simulation
    simulation = PhishingSimulation.query.filter_by(campaign_id=campaign_id).first()
    if simulation:
        simulation.sent_at = datetime.now(timezone.utc)
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'sent_count': sent_count,
        'message': f'{sent_count} emails de simulation envoyés avec succès'
    })

@phishing.route('/api/campaign/<int:campaign_id>/stats')
@login_required
@admin_required
def campaign_stats(campaign_id):
    """Retourne les statistiques en temps réel d'une campagne"""
    stats = db.session.query(
        func.count(PhishingTarget.id).label('total_targets'),
        func.sum(PhishingTarget.sent.cast(db.Integer)).label('sent'),
        func.sum(PhishingTarget.opened.cast(db.Integer)).label('opened'),
        func.sum(PhishingTarget.clicked.cast(db.Integer)).label('clicked'),
        func.sum(PhishingTarget.reported.cast(db.Integer)).label('reported')
    ).join(PhishingSimulation).filter(
        PhishingSimulation.campaign_id == campaign_id
    ).first()
    
    # Évolution temporelle (dernières 24h par heure)
    time_stats = db.session.query(
        func.date_trunc('hour', PhishingTarget.clicked_at).label('hour'),
        func.count(PhishingTarget.id).label('clicks')
    ).join(PhishingSimulation).filter(
        PhishingSimulation.campaign_id == campaign_id,
        PhishingTarget.clicked_at >= datetime.now(timezone.utc) - timedelta(hours=24)
    ).group_by(func.date_trunc('hour', PhishingTarget.clicked_at)).all()
    
    return jsonify({
        'total_targets': stats.total_targets or 0,
        'sent': stats.sent or 0,
        'opened': stats.opened or 0,
        'clicked': stats.clicked or 0,
        'reported': stats.reported or 0,
        'click_rate': round((stats.clicked / stats.sent * 100), 1) if stats.sent else 0,
        'report_rate': round((stats.reported / stats.sent * 100), 1) if stats.sent else 0,
        'timeline': [{'hour': str(t.hour), 'clicks': t.clicks} for t in time_stats]
    })

@phishing.route('/dashboard')
@login_required
@admin_required
def dashboard():
    """Dashboard principal des simulations de phishing"""
    # Statistiques globales
    total_campaigns = Campaign.query.filter_by(type='Phishing Email').count()
    active_campaigns = Campaign.query.filter_by(type='Phishing Email', status='active').count()
    
    # Statistiques des 30 derniers jours
    since_date = datetime.now(timezone.utc) - timedelta(days=30)
    recent_stats = db.session.query(
        func.count(PhishingTarget.id).label('total_targets'),
        func.sum(PhishingTarget.clicked.cast(db.Integer)).label('clicked'),
        func.sum(PhishingTarget.reported.cast(db.Integer)).label('reported')
    ).join(PhishingSimulation).join(Campaign).filter(
        Campaign.created_at >= since_date
    ).first()
    
    # Top des utilisateurs les plus vulnérables (le plus de clics)
    vulnerable_users = db.session.query(
        User.firstname,
        User.lastname,
        User.department,
        func.count(PhishingTarget.id).label('total_simulations'),
        func.sum(PhishingTarget.clicked.cast(db.Integer)).label('total_clicks')
    ).join(PhishingTarget, User.id == PhishingTarget.user_id).join(
        PhishingSimulation
    ).join(Campaign).filter(
        Campaign.created_at >= since_date
    ).group_by(User.id, User.firstname, User.lastname, User.department).having(
        func.sum(PhishingTarget.clicked.cast(db.Integer)) > 0
    ).order_by(desc('total_clicks')).limit(10).all()
    
    # Campagnes récentes
    recent_campaigns = Campaign.query.filter_by(type='Phishing Email').order_by(
        desc(Campaign.created_at)
    ).limit(5).all()
    
    return render_template('phishing/dashboard.html',
                         title='Dashboard Phishing',
                         total_campaigns=total_campaigns,
                         active_campaigns=active_campaigns,
                         recent_stats=recent_stats,
                         vulnerable_users=vulnerable_users,
                         recent_campaigns=recent_campaigns)
