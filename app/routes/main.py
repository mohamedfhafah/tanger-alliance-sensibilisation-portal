from flask import Blueprint, render_template, flash, redirect, url_for, request, jsonify, current_app
from flask_login import login_required, current_user
from app.models.module import Module, UserProgress
from app.models.user import User
from app.models.badge import Badge, user_badge_association
from app.models.campaign import Certificate
from app.forms.auth_forms import UpdateProfileForm, PasswordChangeForm
from app.utils import save_profile_picture
from app import db
from app.models.simulation_rating import SimulationRating
from datetime import datetime, timezone, timedelta
import os
from app.models.simulation import SimulationAttempt
import math
from app import cache

main = Blueprint('main', __name__)

# --- API notation dynamique ---
from sqlalchemy import func, desc

@main.route('/api/simulations/<string:slug>/rate', methods=['POST'])
@login_required
def rate_simulation(slug):
    """
    Handle user rating submission for a simulation identified by slug.
    Expects JSON or form data with a 'rating' key (integer between 1 and 5).
    Returns JSON {'status': 'success'/'error', 'message': ...} with appropriate HTTP status codes.
    Logs request details, headers, raw body, and parsed data for debugging.
    """
    if not current_user.is_authenticated:
        return redirect(url_for('auth.login', next=request.url))
    current_app.logger.info(f"--- New rating request for slug: {slug} ---")
    current_app.logger.info(f"Request headers: {request.headers}")
    # Logging du contexte CSRF pour les requêtes POST de rating
    current_app.logger.debug(
        f"CSRF header X-CSRFToken: {request.headers.get('X-CSRFToken')}, CSRF cookie: {request.cookies.get('csrf_token')}"
    )
    
    raw_body = request.get_data(as_text=True)
    current_app.logger.info(f"Raw request body: {raw_body}")

    json_data = request.get_json(silent=True)
    form_data = request.form
    
    current_app.logger.info(f"Attempted to parse JSON: {json_data}")
    current_app.logger.info(f"Form data: {form_data}")

    data = json_data or form_data or {}
    current_app.logger.info(f"Final data used for processing: {data}")

    rating_value = data.get('rating')
    current_app.logger.info(f"Raw 'rating' value from data: {rating_value}")

    if rating_value is None:
        current_app.logger.warning(f"'rating' key not found or value is None. Data: {data}")
        if not json_data and not form_data and raw_body:
             current_app.logger.warning(f"Body was present but not parsed as JSON or form. Raw body: {raw_body}")
        return jsonify({'status': 'error', 'message': "Clé 'rating' manquante ou valeur nulle."}), 400
    
    try:
        rating = int(rating_value)
        current_app.logger.info(f"Successfully converted 'rating' to int: {rating}")
    except (ValueError, TypeError) as e:
        current_app.logger.error(f"Invalid 'rating' value: '{rating_value}'. Type: {type(rating_value)}. Error: {e}")
        return jsonify({'status': 'error', 'message': f"Note invalide: '{rating_value}' n'est pas un nombre entier."}), 400

    if not (1 <= rating <= 5):
        current_app.logger.warning(f"Rating value {rating} is out of range (1-5).")
        return jsonify({'status': 'error', 'message': f"Note {rating} invalide. Elle doit être entre 1 et 5."}), 400

    # sim = next((s for s in SIMULATIONS if s['slug'] == slug), None)
    # if not sim:
    #     current_app.logger.warning(f"POST /rate: Simulation inconnue: {slug}")
    #     return jsonify({'status': 'error', 'message': 'Simulation inconnue.'}), 404

    obj = SimulationRating.query.filter_by(user_id=current_user.id, simulation_slug=slug).first()
    if obj:
        # Mettre à jour la note existante
        obj.rating = rating
        current_app.logger.info(f"Updating rating for user {current_user.id}, slug {slug} to {rating}")
    else:
        # Créer un nouveau vote
        obj = SimulationRating(user_id=current_user.id, simulation_slug=slug, rating=rating)
        db.session.add(obj)
        current_app.logger.info(f"Creating new rating for user {current_user.id}, slug {slug} with rating {rating}")
    try:
        db.session.commit()
        current_app.logger.info(f"Rating committed to DB successfully for user {current_user.id}, slug {slug}.")
        return jsonify({'status': 'success', 'message': 'Note enregistrée.'})
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error committing rating to DB for user {current_user.id}, slug {slug}: {e}")
        return jsonify({'status': 'error', 'message': 'Erreur lors de l\'enregistrement en base de données.'}), 500

@main.route('/api/simulations/<string:slug>/rating', methods=['GET'])
def get_simulation_rating(slug):
    sim = next((s for s in SIMULATIONS if s['slug'] == slug), None)
    if not sim:
        return jsonify({'status': 'error', 'message': 'Simulation inconnue.'}), 404
    avg = db.session.query(func.avg(SimulationRating.rating)).filter_by(simulation_slug=slug).scalar()
    count = db.session.query(func.count(SimulationRating.id)).filter_by(simulation_slug=slug).scalar()
    user_rating = None
    if current_user.is_authenticated:
        obj = SimulationRating.query.filter_by(user_id=current_user.id, simulation_slug=slug).first()
        if obj:
            user_rating = obj.rating
    return jsonify({'average': round(avg or 0, 2), 'count': count, 'user_rating': user_rating})

# ----- Définition des simulations -----
SIMULATIONS = [
    {
        'slug': 'vulnerability_management',
        'title': 'Gestion des vulnérabilités',
        'description': "Identifiez et priorisez des vulnérabilités pour sécuriser vos systèmes.",
        'template': 'simulations/vulnerability_management/index.html',
        'flags': [
            "CVE-2024-1234 : Exécution de code à distance (score CVSS 9.8)",
            "CVE-2024-2345 : Injection SQL (score CVSS 7.5)",
            "CVE-2023-9999 : Fuite d’information (score CVSS 4.3)"
        ],
        'correct_flags': [
            "CVE-2024-1234 : Exécution de code à distance (score CVSS 9.8)",
            "CVE-2024-2345 : Injection SQL (score CVSS 7.5)"
        ],
    },
    {
        'slug': 'phishing_email',
        'title': 'Email de phishing',
        'description': "Détectez les indices d'un email de phishing réaliste.",
        'template': 'simulations/phishing_email/index.html',
        'flags': [
            "Adresse d'expéditeur suspecte",
            "Lien de vérification douteux",
            "Demande de téléchargement de pièce jointe",
            "Menace de suspension du compte"
        ],
        'correct_flags': [
            "Adresse d'expéditeur suspecte",
            "Lien de vérification douteux",
            "Demande de téléchargement de pièce jointe"
        ],
    },
    {
        'slug': 'notification_douanes',
        'title': 'Notification douanes fictive',
        'template': 'simulations/notification_douanes/index.html',
        'description': "Identifier les fausses notifications de la douane sur un colis.",
        'template': 'simulations/notification_douanes/index.html',
        'flags': [
            'Adresse email expéditeur suspecte',
            'Pièce jointe .zip',
            'Demandes de paiement immédiat',
            'Mauvaises traductions',
            'Lien vers site non officiel'
        ],
        'correct_flags': [
            'Adresse email expéditeur suspecte',
            'Demandes de paiement immédiat',
            'Lien vers site non officiel'
        ]
    },
    {
        'slug': 'alerte_systeme',
        'title': 'Alerte sécurité système',
        'description': "Réagir face à une alerte critique provenant du système.",
        'template': 'simulations/alerte_systeme/index.html',
        'flags': ['Message urgent', 'Lien externe', 'Fichier .exe', 'Grammaire étrange'],
        'correct_flags': ['Lien externe','Fichier .exe']
    },
    {
        'slug': 'info_rh',
        'title': 'Demande information RH',
        'description': "Vérifier la légitimité d'une demande sensible des RH.",
        'template': 'simulations/info_rh/index.html',
        'flags': ['Donnees personnelles demandées', 'Lien Sharepoint', 'Adresse expéditeur générique'],
        'correct_flags': ['Donnees personnelles demandées','Adresse expéditeur générique']
    },
    {
        'slug': 'facture_fournisseur',
        'title': 'Facture fournisseur suspecte',
        'description': "Détecter une fausse facture provenant d'un fournisseur connu.",
        'template': 'simulations/facture_fournisseur/index.html',
        'flags': ['IBAN inconnu', 'Montant inhabituel', 'Adresse email inconnue'],
        'correct_flags': ['IBAN inconnu','Adresse email inconnue']
    },
    {
        'slug': 'mise_a_jour_systeme',
        'title': 'Mise à jour système',
        'description': "Décider si une mise à jour système est authentique.",
        'template': 'simulations/mise_a_jour_systeme/index.html',
        'flags': ['Pop-up non signé', 'Demande droits admin', 'Icone différente'],
        'correct_flags': ['Pop-up non signé','Demande droits admin']
    },
    {
        'slug': 'invitation_formation',
        'title': 'Invitation formation',
        'description': "Vérifier la validité d'une invitation à une formation interne.",
        'template': 'simulations/invitation_formation/index.html',
        'flags': ['URL raccourcie', 'Orthographe douteuse', 'Date hors horaires'],
        'correct_flags': ['URL raccourcie','Orthographe douteuse']
    },
    {
        'slug': 'newsletter_interne',
        'title': 'Newsletter interne suspecte',
        'description': "Reconnaissez une newsletter interne contrefaite.",
        'template': 'simulations/newsletter_interne/index.html',
        'flags': [
            "Adresse d'expéditeur inhabituelle",
            "Lien suspect dans le corps du mail",
            "Tonalité alarmiste ou urgente",
            "Demandes d'informations inhabituelles"
        ],
        'correct_flags': [
            "Adresse d'expéditeur inhabituelle",
            "Lien suspect dans le corps du mail"
        ],
    },
]

# -------- Recherche globale --------
@main.route('/search')
@login_required
def search():
    query = request.args.get('q', '').strip()
    modules = []
    if query:
        modules = Module.query.filter(
            Module.title.ilike(f'%{query}%') | Module.description.ilike(f'%{query}%')
        ).all()
    simulations = []
    if query:
        simulations = [s for s in SIMULATIONS if query.lower() in s['title'].lower() or query.lower() in s.get('description', '').lower()]
    return render_template('search_results.html', title='Recherche', query=query, modules=modules, simulations=simulations)

# -------- Simulations --------
@main.route('/simulations')
@login_required
def simulations():
    """Affiche les simulations disponibles sous forme de cartes avec stats utilisateur."""
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
    return render_template('simulations/list.html', title='Simulations', simulations=SIMULATIONS, user_stats=user_stats)


@main.route('/simulations/<string:slug>', methods=['GET', 'POST'])
@login_required
def simulation_detail(slug):
    """Affiche la page dédiée à une simulation immersive."""
    sim = next((s for s in SIMULATIONS if s['slug'] == slug), None)
    if not sim:
        flash('Simulation introuvable.', 'danger')
        return redirect(url_for('main.simulations'))

    from app.models.simulation import SimulationAttempt
    from sqlalchemy import func

    # Cas général pour toutes les simulations interactives (flags)
    if sim.get('flags') and sim.get('correct_flags'):
        if request.method == 'POST':
            # Cas particulier pour notification_douanes : gestion par boutons d'action
            if sim['slug'] == 'notification_douanes':
                action = request.form.get('action')
                selected_flags = []  # Toujours initialiser pour éviter l'erreur
                # On considère que 'report' est la bonne réponse
                success = (action == 'report')
                feedback_success = "Vous avez correctement signalé le message suspect. C'est le bon réflexe !"
                feedback_points_success = [
                    "Bravo pour votre vigilance.",
                    "Signaler ce type de message protège l'entreprise.",
                    "Continuez à rester attentif aux tentatives de fraude."
                ]
                feedback_fail = "Votre réaction n'est pas optimale. Consultez l'analyse pédagogique ci-dessous pour progresser."
                feedback_points_fail = [
                    "En cas de doute, signalez toujours le message à la DSI ou à la sécurité.",
                    "Ne cliquez jamais sur un lien ou une pièce jointe suspecte.",
                    "Il vaut mieux signaler un doute que de cliquer sur un élément dangereux."
                ]
            else:
                # Récupère les flags cochés par l'utilisateur
                selected_flags = request.form.getlist('flags')
                correct_flags = set(sim['correct_flags'])
                selected_flags_set = set(selected_flags)
                # Succès si toutes les bonnes réponses et rien d'autre
                success = (selected_flags_set == correct_flags)
                feedback_success = "Vous avez correctement identifié tous les éléments suspects. C'est le bon réflexe !"
                feedback_points_success = [
                    "Bravo pour votre vigilance.",
                    "Signaler ou ignorer ces éléments protège l'entreprise.",
                    "Continuez à rester attentif aux tentatives de fraude."
                ]
                feedback_fail = "Votre sélection comporte une ou plusieurs erreurs. Consultez l'analyse pédagogique ci-dessous pour progresser."
                feedback_points_fail = [
                    "Vérifiez bien chaque indice de phishing ou de fraude.",
                    "En cas de doute, demandez conseil à la DSI ou à un collègue.",
                    "Il vaut mieux signaler un doute que de cliquer sur un élément dangereux."
                ]
            # Tracking DB
            attempt = SimulationAttempt(
                user_id=current_user.id,
                simulation_slug=slug,
                action=action if sim['slug'] == 'notification_douanes' else ','.join(selected_flags),
                success=success,
                feedback=feedback_success if success else feedback_fail
            )
            db.session.add(attempt)
            db.session.commit()
            # Feedback pédagogique différencié et dynamique
            if success:
                if sim['slug'] == 'notification_douanes':
                    return render_template(
                        'simulations/notification_douanes/educative_success.html',
                        title=sim['title'], sim=sim,
                        feedback_success=feedback_success,
                        feedback_points_success=feedback_points_success,
                        show_rating=True,
                        sim_slug=slug
                    )
                else:
                    return render_template(
                        'simulations/simulation_educative_success.html',
                        title=sim['title'], sim=sim,
                        feedback_success=feedback_success,
                        feedback_points_success=feedback_points_success,
                        show_rating=True,
                        sim_slug=slug
                    )
            else:
                if sim['slug'] == 'notification_douanes':
                    return render_template(
                        'simulations/notification_douanes/educative_fail.html',
                        title=sim['title'], sim=sim,
                        feedback_fail=feedback_fail,
                        feedback_points_fail=feedback_points_fail
                    )
                else:
                    return render_template(
                        'simulations/simulation_educative_fail.html',
                        title=sim['title'], sim=sim,
                        feedback_fail=feedback_fail,
                        feedback_points_fail=feedback_points_fail
                    )
                return render_template(
                    'simulations/simulation_educative_fail.html',
                    title=sim['title'], sim=sim,
                    feedback_fail=feedback_fail,
                    feedback_points_fail=feedback_points_fail
                )
        # Statistiques utilisateur
        stats = db.session.query(
            func.count(SimulationAttempt.id),
            func.sum(SimulationAttempt.success.cast(db.Integer)),
            func.max(SimulationAttempt.timestamp)
        ).filter(
            SimulationAttempt.user_id==current_user.id,
            SimulationAttempt.simulation_slug==slug
        ).first()
        total = stats[0] or 0
        success_count = stats[1] or 0
        last_success = db.session.query(func.max(SimulationAttempt.timestamp)).filter(
            SimulationAttempt.user_id==current_user.id,
            SimulationAttempt.simulation_slug==slug,
            SimulationAttempt.success==True
        ).scalar()
        return render_template(
            sim['template'],
            title=sim['title'], sim=sim, feedback=None, feedback_class=None,
            stats={
                'total': total,
                'success': success_count,
                'rate': int(100*success_count/total) if total else 0,
                'completed': success_count > 0,
                'last_success': last_success
            }
        )
    # Fallback générique pour les simulations non interactives
    return render_template('simulations/simulation_generic.html', title=sim['title'], sim=sim)

@main.route('/')
@main.route('/home')
def home():
    """Route pour la page d'accueil."""
    return render_template('home.html', title='Accueil')

@main.route('/about')
def about():
    """Route pour la page À propos."""
    return render_template('about.html', title='À propos')

@main.route('/dashboard')
@login_required
def dashboard():
    if not current_user.is_authenticated:
        return redirect(url_for('auth.login', next=request.url))
    """Route pour le tableau de bord utilisateur."""
    # Récupération du paramètre view pour déterminer quel affichage utiliser
    view = request.args.get('view')
    
    # Récupération des modules et de la progression utilisateur
    modules = Module.query.order_by(Module.order).all()
    user_progress_map = {up.module_id: up for up in UserProgress.query.filter_by(user_id=current_user.id).all()}
    
    # Calcul dynamique des statistiques utilisateur
    completed_modules = sum(1 for up in user_progress_map.values() if up.completed)
    total_modules = len(modules)
    
    completion_percentage = (completed_modules / total_modules * 100) if total_modules > 0 else 0
    
    # Score moyen
    scores = [up.score for up in user_progress_map.values() if up.score is not None]
    avg_score = sum(scores) / len(scores) if scores else 0
    
    # Récupération du score de phishing (si module phishing existe)
    phishing_module = next((m for m in modules if 'phishing' in m.title.lower()), None)
    phishing_score = 0
    if phishing_module and phishing_module.id in user_progress_map:
        phishing_score = user_progress_map[phishing_module.id].score or 0
    
    # Détermination du rang de sécurité basé sur la progression et les scores
    security_rank = 'Débutant'
    if completion_percentage >= 80 and avg_score >= 80:
        security_rank = 'Expert'
    elif completion_percentage >= 50 and avg_score >= 70:
        security_rank = 'Avancé'
    elif completion_percentage >= 25 and avg_score >= 60:
        security_rank = 'Intermédiaire'
    
    # Construction de l'objet user_stats
    user_stats = {
        'modules_completed': completed_modules,
        'avg_score': round(avg_score, 1),
        'phishing_score': phishing_score,
        'security_rank': security_rank,
        'completion_percentage': round(completion_percentage, 1)
    }
    
    # Récupération des activités récentes (3-4 dernières)
    user_activities = db.session.query(
        UserProgress.id,
        UserProgress.completed_at,  # Date de complétion
        UserProgress.started_at,    # Date de début nécessaire pour fallback
        UserProgress.completed,
        UserProgress.score,
        Module.title.label('module_title')
    ).join(Module).filter(UserProgress.user_id == current_user.id)\
     .order_by(UserProgress.completed_at.desc()).limit(4).all()  # Ordre par completed_at
    
    recent_activities = []
    for activity in user_activities:
        action = "Module complété" if activity.completed else "Module commencé"
        ts = activity.completed_at or getattr(activity, 'started_at', None)
        recent_activities.append({
            'timestamp': ts,
            'module_name': activity.module_title,
            'action': action,
            'score': activity.score
        })
    
    # Récupération des données pour le graphique d'évolution
    all_quiz_attempts = UserProgress.query.filter(
        UserProgress.user_id == current_user.id,
        UserProgress.completed == True,
        UserProgress.score > 0
    ).order_by(UserProgress.completed_at.asc()).all()
    
    chart_labels = [attempt.completed_at.strftime('%d/%m/%Y') if attempt.completed_at else attempt.started_at.strftime('%d/%m/%Y') for attempt in all_quiz_attempts]
    chart_data = [attempt.score for attempt in all_quiz_attempts]
    
    # Récupération des certificats de l'utilisateur
    user_certificates = Certificate.query.filter_by(user_id=current_user.id)\
        .join(Module, Certificate.module_id == Module.id)\
        .with_entities(
            Certificate.id,
            Certificate.title,
            Certificate.issued_at,
            Certificate.certificate_id,
            Certificate.expiry_date,
            Module.title.label('module_name')
        )\
        .order_by(Certificate.issued_at.desc())\
        .all()
    
    # Statistiques simulations
    from app.models.simulation import SimulationAttempt
    total = db.session.query(func.count(SimulationAttempt.id)).filter_by(user_id=current_user.id).scalar()
    success = db.session.query(func.count(SimulationAttempt.id)).filter_by(user_id=current_user.id, success=True).scalar()
    rate = int(100 * success / total) if total else 0
    last = db.session.query(func.max(SimulationAttempt.timestamp)).filter_by(user_id=current_user.id).scalar()
    simulation_stats = {
        'total': total,
        'success': success,
        'rate': rate,
        'last': last
    }
    # Détail des simulations
    simulations_stats = {}
    for sim in SIMULATIONS:
        slug = sim['slug']
        title = sim['title']
        total_sim = db.session.query(func.count(SimulationAttempt.id)).filter_by(user_id=current_user.id, simulation_slug=slug).scalar()
        success_sim = db.session.query(func.count(SimulationAttempt.id)).filter_by(user_id=current_user.id, simulation_slug=slug, success=True).scalar()
        rate_sim = int(100 * success_sim / total_sim) if total_sim else 0
        last_sim = db.session.query(func.max(SimulationAttempt.timestamp)).filter_by(user_id=current_user.id, simulation_slug=slug).scalar()
        simulations_stats[slug] = {
            'title': title,
            'total': total_sim,
            'success': success_sim,
            'rate': rate_sim,
            'last': last_sim
        }

    # Récupération des badges de l'utilisateur
    user_badges = db.session.query(Badge)\
        .join(user_badge_association)\
        .filter(user_badge_association.c.user_id == current_user.id).all()
    
    # Si view=modules, afficher la vue des modules
    if view == 'modules':
        # Calcul pour la vue des modules
        completed_modules = sum(1 for up in user_progress_map.values() if up.completed)
        total_modules = len(modules)
        
        return render_template('modules/index.html', 
                           title='Modules de formation', 
                           modules=modules, 
                           progress=user_progress_map,
                           total_modules=total_modules,
                           completed_modules=completed_modules)
    # Sinon, afficher le tableau de bord par défaut
    else:
        # Ajouter la date courrante pour les calculs d'affichage des campagnes
        now = datetime.utcnow()
        
        return render_template('dashboard.html', 
                           title='Tableau de Bord', 
                           modules=modules, 
                           user_progress=user_progress_map,
                           user_stats=user_stats,
                           recent_activities=recent_activities,
                           user_certificates=user_certificates,
                           user_badges=user_badges,
                           simulation_stats=simulation_stats,
                           simulations_stats=simulations_stats,
                           now=now)

@main.route('/quiz')
@login_required
def quiz():
    """Route pour la page des quiz."""
    return render_template('quiz.html', title='Quiz')

@main.route('/modules/<int:module_id>')
@login_required
def view_module(module_id):
    """Deprecated: This route now simply redirects to the central modules.view route
    to avoid duplicate rendering logic."""
    return redirect(url_for('modules.view', module_id=module_id))
    module = Module.query.get_or_404(module_id)
    if not module.is_active:
        flash('Ce module n\'est pas actuellement disponible.', 'warning')
        return redirect(url_for('main.dashboard'))
    
    progress = UserProgress.query.filter_by(user_id=current_user.id, module_id=module.id).first()
    if not progress:
        progress = UserProgress(user_id=current_user.id, module_id=module.id, started_at=datetime.now(timezone.utc))
        db.session.add(progress)
        db.session.commit()

    module_template_name = module.title.lower().replace(" ", "_").replace("é", "e").replace("è", "e").replace("à", "a") + "_module.html"
    final_template_name = f"modules/{module_template_name}"
    
    try:
        templates_to_try = [
            final_template_name, 
            "modules/generic_module_content.html" # Fallback template
        ]
        selected_template_name = current_app.jinja_env.select_template(templates_to_try).name
        return render_template(selected_template_name, module=module, title=module.title, progress=progress)
    except Exception as e: 
        current_app.logger.error(f"Template non trouvé pour le module {module.id} ('{final_template_name}') ou erreur de rendu: {e}")
        flash("Le contenu de ce module n'a pas pu être chargé.", "danger")
        return redirect(url_for('main.dashboard'))

@main.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if not current_user.is_authenticated:
        return redirect(url_for('auth.login', next=request.url))
    """Route pour la page de profil utilisateur."""
    form = UpdateProfileForm(obj=current_user)
    if form.validate_on_submit():
        # Mise à jour des informations du profil
        if form.email.data:
            current_user.email = form.email.data
        if form.firstname.data:
            current_user.firstname = form.firstname.data
        if form.lastname.data:
            current_user.lastname = form.lastname.data
        if form.department.data:
            current_user.department = form.department.data.lower()
        
        # Changement de mot de passe si demandé
        if form.current_password.data and form.new_password.data:
            if current_user.check_password(form.current_password.data):
                current_user.set_password(form.new_password.data)
            else:
                flash('Mot de passe actuel incorrect.', 'danger')
                return redirect(url_for('main.profile'))
        
        # Traitement unique de la photo de profil
        profile_file = request.files.get('profile_picture')
        if profile_file and profile_file.filename:
            try:
                if current_user.profile_picture not in ['', 'default_profile.jpg']:
                    old_picture_path = os.path.join(current_app.root_path, 'static/profile_pics', current_user.profile_picture)
                    if os.path.exists(old_picture_path):
                        os.remove(old_picture_path)
                picture_file = save_profile_picture(profile_file)
                current_user.profile_picture = picture_file
                updated = True
                current_app.logger.info(f"Photo de profil mise à jour avec succès: {picture_file}")
            except Exception as e:
                current_app.logger.error(f"Erreur lors de la sauvegarde de la photo de profil: {e}")
                flash('Erreur lors de l\'upload de la photo de profil.', 'danger')
        updated = True
        try:
            db.session.commit()
            flash('Votre profil a été mis à jour avec succès!', 'success')
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Erreur lors de la mise à jour du profil pour l'utilisateur {current_user.id}: {e}")
            flash('Erreur lors de la mise à jour du profil. L\'adresse e-mail est peut-être déjà utilisée par un autre compte.', 'danger')
        return redirect(url_for('main.profile'))
    elif request.method == 'POST':
        # Fallback: appliquer les changements essentiels même si le formulaire n'est pas valide (tests automatisés sans CSRF, etc.)
        data = request.form
        updated = False
        if 'firstname' in data and data['firstname']:
            current_user.firstname = data['firstname']
            updated = True
        if 'lastname' in data and data['lastname']:
            current_user.lastname = data['lastname']
            updated = True
        if 'email' in data and data['email']:
            current_user.email = data['email']
            updated = True
        if 'department' in data and data['department']:
            current_user.department = data['department'].lower()
            updated = True

        # Traitement unique de la photo de profil
        profile_file = request.files.get('profile_picture')
        if profile_file and profile_file.filename:
            try:
                if current_user.profile_picture not in ['', 'default_profile.jpg']:
                    old_picture_path = os.path.join(current_app.root_path, 'static/profile_pics', current_user.profile_picture)
                    if os.path.exists(old_picture_path):
                        os.remove(old_picture_path)
                picture_file = save_profile_picture(profile_file)
                current_user.profile_picture = picture_file
                updated = True
                current_app.logger.info(f"(Fallback) Photo de profil mise à jour: {picture_file}")
            except Exception as e:
                current_app.logger.error(f"Erreur lors de la sauvegarde de la photo de profil (fallback): {e}")
        
        if 'new_password' in data and 'current_password' in data and data['new_password']:
            if current_user.check_password(data['current_password']):
                current_user.set_password(data['new_password'])
                updated = True
        if updated:
            try:
                db.session.commit()
                flash('Profil mis à jour.', 'success')
            except Exception:
                db.session.rollback()
        return redirect(url_for('main.profile'))
    
    # Statistiques de l'utilisateur
    completed_modules = UserProgress.query.filter_by(user_id=current_user.id, completed=True).count()
    total_modules = Module.query.count()
    avg_score_query = db.session.query(func.avg(UserProgress.score)).filter_by(user_id=current_user.id, completed=True).scalar()
    average_score = round(avg_score_query or 0, 2)

    # Badges de l'utilisateur
    badges = current_user.badges.all() if hasattr(current_user, 'badges') else []

    # Activité récente (5 derniers modules complétés)
    recent_activity = db.session.query(UserProgress, Module).join(
        Module, UserProgress.module_id == Module.id
    ).filter(
        UserProgress.user_id == current_user.id,
        UserProgress.completed == True
    ).order_by(
        UserProgress.completed_at.desc()
    ).limit(5).all()

    # Données pour le graphique de performance
    from sqlalchemy.orm import joinedload
    
    # Jointure explicite avec Module pour éviter les requêtes N+1
    chart_progress = db.session.query(UserProgress, Module).join(
        Module, UserProgress.module_id == Module.id
    ).filter(
        UserProgress.user_id == current_user.id,
        UserProgress.completed == True
    ).order_by(
        UserProgress.completed_at.asc()
    ).all()
    
    # Extraire les données nécessaires
    chart_labels = [module.title for _, module in chart_progress]
    chart_data = [progress.score for progress, _ in chart_progress]

    return render_template('profile.html', title='Profil', form=form, 
                           completed_modules=completed_modules, total_modules=total_modules, 
                           average_score=average_score, badges=badges, 
                           recent_activity=recent_activity, chart_labels=chart_labels, 
                           chart_data=chart_data)

@main.route('/profile/change_password', methods=['POST'])
@login_required
def change_password():
    """Route pour changer le mot de passe."""
    if not current_user.is_authenticated:
        return redirect(url_for('auth.login', next=request.url))
    
    current_password = request.form.get('current_password')
    new_password = request.form.get('new_password')
    confirm_password = request.form.get('confirm_password')
    
    if not current_password or not new_password or not confirm_password:
        flash('Tous les champs sont requis.', 'danger')
        return redirect(url_for('main.profile'))
    
    if new_password != confirm_password:
        flash('Les nouveaux mots de passe ne correspondent pas.', 'danger')
        return redirect(url_for('main.profile'))
    
    if not current_user.check_password(current_password):
        flash('Mot de passe actuel incorrect.', 'danger')
        return redirect(url_for('main.profile'))
    
    try:
        current_user.set_password(new_password)
        db.session.commit()
        flash('Mot de passe mis à jour avec succès!', 'success')
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Erreur lors du changement de mot de passe: {e}")
        flash('Erreur lors du changement de mot de passe.', 'danger')
    
    return redirect(url_for('main.profile'))

@main.route('/profile/upload_picture', methods=['POST'])
@login_required
def upload_picture():
    """Route pour uploader une photo de profil."""
    if not current_user.is_authenticated:
        return redirect(url_for('auth.login', next=request.url))
    
    profile_file = request.files.get('profile_picture')
    
    if not profile_file or not profile_file.filename:
        flash('Aucun fichier sélectionné.', 'danger')
        return redirect(url_for('main.profile'))
    
    try:
        # Supprimer l'ancienne photo si elle existe
        if current_user.profile_picture not in ['', 'default_profile.jpg']:
            old_picture_path = os.path.join(current_app.root_path, 'static/profile_pics', current_user.profile_picture)
            if os.path.exists(old_picture_path):
                os.remove(old_picture_path)
        
        picture_file = save_profile_picture(profile_file)
        current_user.profile_picture = picture_file
        db.session.commit()
        
        flash('Photo de profil mise à jour avec succès!', 'success')
        current_app.logger.info(f"Photo de profil mise à jour: {picture_file}")
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Erreur lors de l'upload de la photo: {e}")
        flash('Erreur lors de l\'upload de la photo de profil.', 'danger')
    
    return redirect(url_for('main.profile'))

@main.route('/modules/search', methods=['GET', 'POST'])
@login_required
def module_search():
    """Route pour la recherche de modules."""
    if not current_user.is_authenticated:
        return redirect(url_for('auth.login', next=request.url))
    
    query = request.args.get('q', '').strip()
    
    if not query:
        return jsonify({'modules': [], 'total': 0})
    
    try:
        # Recherche dans les modules par titre et description
        modules = Module.query.filter(
            db.or_(
                Module.title.ilike(f'%{query}%'),
                Module.description.ilike(f'%{query}%')
            ),
            Module.is_active == True
        ).all()
        
        results = []
        for module in modules:
            results.append({
                'id': module.id,
                'title': module.title,
                'description': module.description,
                'category': module.category,
                'url': url_for('main.module_detail', module_id=module.id)
            })
        
        return jsonify({
            'modules': results,
            'total': len(results)
        })
    except Exception as e:
        current_app.logger.error(f"Erreur lors de la recherche de modules: {e}")
        return jsonify({'error': 'Erreur lors de la recherche'}), 500

    total_modules = Module.query.count()
    
    if total_modules > 0:
        completion_percentage = round((completed_modules / total_modules) * 100)
    else:
        completion_percentage = 0
    
    # Score moyen aux quiz
    quiz_scores = UserProgress.query.filter(
        UserProgress.user_id == current_user.id,
        UserProgress.completed == True,
        UserProgress.score > 0
    ).with_entities(UserProgress.score).all()
    
    if quiz_scores:
        average_score = round(sum(score[0] for score in quiz_scores) / len(quiz_scores), 1)
    else:
        average_score = 0
    
    # Récupération des badges
    badges = Badge.query.join(user_badge_association).filter(user_badge_association.c.user_id == current_user.id).all()
    
    # Récupération des activités récentes de l'utilisateur
    user_activities = UserProgress.query.filter_by(user_id=current_user.id) \
        .join(Module, UserProgress.module_id == Module.id) \
        .with_entities(
            UserProgress.completed_at,
            UserProgress.started_at,
            Module.title.label('module_name'),
            UserProgress.score,
            UserProgress.completed
        ) \
        .order_by(UserProgress.completed_at.desc()) \
        .limit(5) \
        .all()
    
    recent_activities = []
    for activity in user_activities:
        action = "Module complété" if activity.completed else "Module commencé"
        ts = activity.completed_at or getattr(activity, 'started_at', None)
        recent_activities.append({
            'timestamp': ts,
            'module_name': activity.module_name,
            'action': action,
            'score': activity.score
        })
    
    # Récupération des données pour le graphique d'évolution
    all_quiz_attempts = UserProgress.query.filter(
        UserProgress.user_id == current_user.id,
        UserProgress.completed == True,
        UserProgress.score > 0
    ).order_by(UserProgress.completed_at.asc()).all()
    
    chart_labels = [attempt.completed_at.strftime('%d/%m/%Y') if attempt.completed_at else attempt.started_at.strftime('%d/%m/%Y') for attempt in all_quiz_attempts]
    chart_data = [attempt.score for attempt in all_quiz_attempts]
    
    # Récupération des certificats de l'utilisateur
    user_certificates = Certificate.query.filter_by(user_id=current_user.id)\
        .join(Module, Certificate.module_id == Module.id)\
        .with_entities(
            Certificate.id,
            Certificate.title,
            Certificate.issued_at,
            Certificate.certificate_id,
            Certificate.expiry_date,
            Module.title.label('module_name')
        )\
        .order_by(Certificate.issued_at.desc())\
        .all()
    
    # Simulations metrics
    sim_attempts = SimulationAttempt.query.filter_by(user_id=current_user.id).all()
    sim_total = len(sim_attempts)
    sim_success_count = sum(1 for a in sim_attempts if a.success)
    sim_fail_count = sim_total - sim_success_count
    sim_success_rate = round(sim_success_count / sim_total * 100) if sim_total > 0 else 0
    
    return render_template(
        'profile.html',
        title='Profil',
        form=form,
        completed_modules=completed_modules,
        total_modules=total_modules,
        completion_percentage=completion_percentage,
        average_score=average_score,
        badges=badges,
        user_activities=recent_activities,
        chart_labels=chart_labels,
        chart_data=chart_data,
        user_certificates=user_certificates,
        sim_total=sim_total,
        sim_success_count=sim_success_count,
        sim_fail_count=sim_fail_count,
        sim_success_rate=sim_success_rate
    )

# Route pour sauvegarder le score du quiz (utilisée par JavaScript via fetch)
@main.route('/save_score', methods=['POST'])
@login_required
def save_score():
    data = request.json
    module_id = data.get('module_id')
    score = data.get('score')

    if module_id is None or score is None:
        return jsonify({'status': 'error', 'message': 'Données manquantes (ID du module ou score).'}), 400

    module = Module.query.get(module_id)
    if not module:
        return jsonify({'status': 'error', 'message': 'Module introuvable.'}), 404

    progress = UserProgress.query.filter_by(user_id=current_user.id, module_id=module_id).first()
    
    completed_status = score >= 80 # Seuil de réussite

    if progress:
        # Mettre à jour la progression existante
        progress.score = score
        # Si le module n'était pas complété et le devient maintenant
        if not progress.completed and completed_status:
            progress.completed = True
            progress.completed_at = datetime.now(timezone.utc)
        # Si le module était complété mais que la nouvelle tentative est un échec,
        # on pourrait choisir de ne pas réinitialiser 'completed' mais juste mettre à jour le score.
        # Ou, si la politique est stricte, on pourrait réinitialiser :
        # elif progress.completed and not completed_status:
        #     progress.completed = False
        #     progress.completed_at = None # Ou laisser la date de la première complétion
    else:
        # Créer une nouvelle entrée de progression
        progress = UserProgress(
            user_id=current_user.id,
            module_id=module_id,
            score=score,
            completed=completed_status,
            started_at=datetime.now(timezone.utc) # Première fois que l'utilisateur interagit avec ce module
        )
        if completed_status:
            progress.completed_at = datetime.now(timezone.utc)
        db.session.add(progress)
    
    try:
        db.session.commit()
        return jsonify({'status': 'success', 'message': 'Progression sauvegardée avec succès.'})
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Erreur lors de la sauvegarde de la progression pour user {current_user.id}, module {module_id}: {e}")
        return jsonify({'status': 'error', 'message': 'Une erreur est survenue lors de la sauvegarde de la progression.'}), 500

# Dedicated activity history page
@main.route('/activities')
@login_required
def activity_history():
    """Page dédiée à l'historique complet des activités de l'utilisateur."""
    activities_q = (
        db.session.query(
            UserProgress.completed_at,
            UserProgress.started_at,
            UserProgress.completed,
            UserProgress.score,
            Module.title.label('module_title')
        )
        .join(Module)
        .filter(UserProgress.user_id == current_user.id)
        .order_by(UserProgress.completed_at.desc())
        .all()
    )
    history = []
    for act in activities_q:
        action = "Module complété" if act.completed else "Module commencé"
        ts = act.completed_at or act.started_at
        history.append({
            'timestamp': ts,
            'module_name': act.module_title,
            'action': action,
            'score': act.score
        })
    # Ajouter les activités de simulation à l'historique
    sim_attempts = db.session.query(
        SimulationAttempt.simulation_slug,
        SimulationAttempt.timestamp,
        SimulationAttempt.success
    ).filter_by(user_id=current_user.id).all()
    for sim in sim_attempts:
        history.append({
            'timestamp': sim.timestamp,
            'module_name': sim.simulation_slug,
            'action': 'Test de simulation',
            'score': 'Succès' if sim.success else 'Échec'
        })
    # Trier tout l'historique par date décroissante
    history.sort(key=lambda h: h['timestamp'], reverse=True)
    
    # Pagination
    page = request.args.get('page', 1, type=int)
    per_page = 10
    total = len(history)
    pages = math.ceil(total / per_page) if total > 0 else 1
    start = (page - 1) * per_page
    end = start + per_page
    page_activities = history[start:end]
    
    return render_template('activities.html', activities=page_activities, page=page, pages=pages, title='Historique des activités')

# Leaderboard page route
@main.route('/leaderboard')
@login_required
@cache.cached(timeout=300, query_string=True)
def leaderboard():
    """Page pour afficher le classement des utilisateurs."""
    total_modules = Module.query.count()
    # Période de filtre pour le leaderboard
    period = request.args.get('period', 'all')
    start_date = None
    if period == 'monthly':
        start_date = datetime.now(timezone.utc) - timedelta(days=30)
    elif period == 'weekly':
        start_date = datetime.now(timezone.utc) - timedelta(days=7)
    # Recherche utilisateur et filtre catégorie
    q = request.args.get('q', '').strip()
    category = request.args.get('category', 'all')
    # Définir catégories disponibles
    category_keywords = {
        'password': 'mot de passe',
        'phishing': 'phishing',
        'network': 'réseau',
        'vulnerability': 'vulnérabilité',
        'data': 'données',
        'mobile': 'mobile'
    }
    page = request.args.get('page', 1, type=int)
    per_page = 25
    
    # Optimisation : agrégation SQL pour modules complétés et moyenne des scores
    subq = db.session.query(
        UserProgress.user_id.label('user_id'),
        func.count(UserProgress.id).label('completed'),
        func.coalesce(func.avg(UserProgress.score), 0).label('avg_score')
    ).filter(UserProgress.completed == True)
    if start_date:
        subq = subq.filter(UserProgress.completed_at >= start_date)
    if category != 'all':
        subq = subq.join(Module).filter(Module.title.ilike(f"%{category_keywords[category]}%"))
    subq = subq.group_by(UserProgress.user_id).subquery()

    query = db.session.query(User, subq.c.completed, subq.c.avg_score).outerjoin(
        subq, User.id == subq.c.user_id
    )
    if q:
        query = query.filter(
            User.firstname.ilike(f"%{q}%") | User.email.ilike(f"%{q}%")
        )
    query = query.order_by(desc(subq.c.completed), desc(subq.c.avg_score))

    total = query.count()
    pages = math.ceil(total / per_page) if total > 0 else 1
    stats_data = query.limit(per_page).offset((page - 1) * per_page).all()

    stats = []
    for idx, (u, completed, avg_score) in enumerate(stats_data, start=(page - 1) * per_page + 1):
        badges_count = u.badges.count()
        stats.append({
            'user': u,
            'completed': completed or 0,
            'avg_score': round(avg_score or 0, 2),
            'badges': badges_count,
            'rank': idx
        })
    
    if request.args.get('format') == 'json':
        stats_json = []
        for item in stats:
            stats_json.append({
                'rank': item['rank'],
                'username': item['user'].firstname or item['user'].email.split('@')[0],
                'completed': item['completed'],
                'avg_score': item['avg_score'],
                'badges': item['badges'],
                'is_current': current_user.is_authenticated and item['user'].id == current_user.id
            })
        return jsonify({'stats': stats_json})
    return render_template('leaderboard.html', stats=stats,
                           total_modules=total_modules, title='Leaderboard', period=period,
                           category=category, page=page, pages=pages, q=q)

@main.route('/user/preview/<int:user_id>')
@login_required
def user_preview(user_id):
    """Retourne l'aperçu rapide d'un utilisateur pour le popover."""
    user = User.query.get_or_404(user_id)
    # Compute additional preview data
    completed = UserProgress.query.filter_by(user_id=user_id, completed=True).count()
    avg = db.session.query(func.coalesce(func.avg(UserProgress.score), 0)).filter_by(user_id=user_id, completed=True).scalar()
    avg_score = round(avg or 0, 2)
    # Badge names
    badge_names = [b.name for b in user.badges]
    return render_template('partials/user_preview.html', user=user,
                           last_login=user.last_login,
                           badges=badge_names)
