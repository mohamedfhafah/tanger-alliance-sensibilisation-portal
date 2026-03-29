from flask import Blueprint, render_template, flash, redirect, url_for, request, jsonify, current_app, session
from flask_login import login_required, current_user
from app import db
from app.models.module import Module, UserProgress, Quiz, Question, Choice, QuizProgress
from app.models.badge import Badge
from app.models.user import User
from datetime import datetime, timezone, timedelta

modules = Blueprint('modules', __name__)

# Fonction utilitaire pour attribuer un badge pour un module complété
def award_badge_for_module(user, module, db_session, app):
    """Attribue un badge à l'utilisateur s'il a complété un module avec succès.
    Returns: tuple (badge_object, was_newly_awarded)
    """
    badge_to_award = Badge.query.filter_by(module_id=module.id).first()
    was_newly_awarded = False
    
    if badge_to_award:
        app.logger.info(f'Found badge {badge_to_award.name} (ID: {badge_to_award.id}) for module {module.id}.')
        
        if badge_to_award not in user.badges:
            app.logger.info(f'User {user.id} does not have badge {badge_to_award.name}. Awarding.')
            user.badges.append(badge_to_award)
            was_newly_awarded = True
            flash(f'Nouveau badge débloqué : {badge_to_award.name}!', 'info')
            app.logger.info(f'Badge {badge_to_award.name} awarded to user {user.id}.')
        else:
            app.logger.info(f'User {user.id} already has badge {badge_to_award.name}.')
    else:
        app.logger.warning(f'No badge found for module_id {module.id} in the database.')
    
    return badge_to_award, was_newly_awarded

@modules.route('/')
@login_required
def index():
    """Affiche la liste des modules de formation disponibles."""
    # Check for search parameter
    search_query = request.args.get('search', '').strip()
    filter_param = request.args.get('filter', '').strip()
    
    # Start with base query
    query = Module.query
    
    if search_query:
        # Filter modules based on search query
        query = query.filter(
            db.or_(
                Module.title.ilike(f'%{search_query}%'),
                Module.description.ilike(f'%{search_query}%')
            ),
            Module.is_active == True
        )
    else:
        query = query.filter(Module.is_active == True)
    
    # Apply completion filter if specified
    if filter_param == 'completed':
        # Only show modules that the user has completed
        completed_module_ids = [p.module_id for p in UserProgress.query.filter_by(
            user_id=current_user.id, completed=True
        ).all()]
        if completed_module_ids:
            query = query.filter(Module.id.in_(completed_module_ids))
        else:
            # No completed modules, return empty result
            query = query.filter(Module.id == -1)
    elif filter_param == 'in_progress':
        # Only show modules that are in progress
        in_progress_module_ids = [p.module_id for p in UserProgress.query.filter_by(
            user_id=current_user.id, completed=False
        ).all()]
        if in_progress_module_ids:
            query = query.filter(Module.id.in_(in_progress_module_ids))
        else:
            # No in-progress modules, return empty result
            query = query.filter(Module.id == -1)
    elif filter_param == 'not_started':
        # Only show modules that haven't been started
        started_module_ids = [p.module_id for p in UserProgress.query.filter_by(
            user_id=current_user.id
        ).all()]
        if started_module_ids:
            query = query.filter(~Module.id.in_(started_module_ids))
        # If no started modules, show all active modules (no additional filter needed)
    
    all_modules = query.order_by(Module.order).all()
    user_progress = UserProgress.query.filter_by(user_id=current_user.id).all()
    
    # Créer un dictionnaire pour un accès facile à la progression de l'utilisateur
    progress_dict = {progress.module_id: progress for progress in user_progress}

    # Calculer la progression globale
    total_modules_count = len(all_modules)
    completed_modules_count = UserProgress.query.filter_by(user_id=current_user.id, completed=True).count()
    
    return render_template('modules/index.html', 
                          modules=all_modules,
                          progress=progress_dict,
                          total_modules=total_modules_count,
                          completed_modules=completed_modules_count,
                          search_query=search_query,
                          filter_param=filter_param,
                          title='Modules de formation')

@modules.route('/view/<int:module_id>')
@login_required
def view(module_id):
    """Affiche un module spécifique."""
    module = Module.query.get_or_404(module_id)
    
    # Check if module is active
    if not module.is_active:
        flash('Ce module n\'est pas actuellement disponible.', 'warning')
        return redirect(url_for('modules.index')), 302
    
    progress = UserProgress.query.filter_by(user_id=current_user.id, module_id=module.id).first()
    
    if not progress:
        # Créer un nouvel enregistrement de progression
        progress = UserProgress(user_id=current_user.id, module_id=module.id)
        db.session.add(progress)
        db.session.commit()
    
    # Use the quiz for all modules as needed
    quiz = Quiz.query.filter_by(module_id=module.id).first()
    quiz_available = quiz is not None
    
    # Try to find a specific template based on module title, fallback to generic
    module_title_lower = module.title.lower()
    
    # Define template mappings based on content
    if 'mot de passe' in module_title_lower or 'mots de passe' in module_title_lower or 'password' in module_title_lower:
        template_name = 'modules/password_module.html'
    elif 'phishing' in module_title_lower or 'hameçonnage' in module_title_lower:
        template_name = 'modules/phishing_awareness.html'
    elif ('vuln' in module_title_lower  # match any word starting with "vuln" (vulnérabilité, vulnerability, etc.)
          or 'vulnerability' in module_title_lower
          or 'vulnérabilit' in module_title_lower
          or module.id == 3):  # explicit fallback by ID for the Vulnerability Management module
        template_name = 'modules/vulnerability_management.html'
    elif 'données' in module_title_lower or 'data' in module_title_lower:
        template_name = 'modules/data_protection_module.html'
    elif 'mobile' in module_title_lower:
        template_name = 'modules/mobile_security_module.html'
    elif 'réseau' in module_title_lower or 'network' in module_title_lower:
        template_name = 'modules/network_security_module.html'
    else:
        # Use a generic template that can display module content
        template_name = 'modules/generic_module.html'
    
    try:
        return render_template(template_name, module=module, progress=progress, quiz=quiz, quiz_available=quiz_available)
    except Exception as e:
        current_app.logger.error(f"Template {template_name} not found for module {module.id}: {e}")
        # Fallback to a simple generic template
        return render_template('modules/generic_module.html', module=module, progress=progress, quiz=quiz, quiz_available=quiz_available)

# Les routes individuelles pour les sections du module de gestion des mots de passe 
# ont été supprimées car elles sont maintenant intégrées dans un seul template (password_module.html)

@modules.route('/update-progress', methods=['POST'])
@login_required
def update_progress():
    """Met à jour la progression de l'utilisateur pour un module."""
    data = request.json
    module_id = data.get('module_id')
    section = data.get('section')
    status = data.get('status')
    
    if not module_id:
        return jsonify({'success': False, 'message': 'ID du module manquant'}), 400
        
    # Convertir l'ID du module en entier si c'est une chaîne
    try:
        module_id = int(module_id)
    except ValueError:
        return jsonify({'success': False, 'message': 'ID du module invalide'}), 400
        
    progress = UserProgress.query.filter_by(user_id=current_user.id, module_id=module_id).first()
    
    if not progress:
        progress = UserProgress(user_id=current_user.id, module_id=module_id)
        db.session.add(progress)
    
    # Mettre à jour la progression
    if section and status == 'completed':
        # Enregistrer que l'utilisateur a complété une section
        current_app.logger.info(f"Section {section} marquée comme terminée pour le module {module_id}")
        
        # Marquer le module comme commencé si ce n'est pas déjà fait
        if not progress.started_at:
            progress.started_at = db.func.now()
        
        # Si c'est la section finale ou si on marque explicitement le module comme complet
        if section == 'complete':
            progress.completed = True
            progress.completed_at = db.func.now()
    
    db.session.commit()
    
    return jsonify({'success': True, 'message': 'Progression mise à jour'})

@modules.route('/<int:module_id>/quiz')
@login_required
def quiz(module_id):
    """Affiche le quiz pour un module spécifique."""
    module = Module.query.get_or_404(module_id)
    
    # Charger le quiz avec ses questions et choix en utilisant joinedload et trier les questions par ID
    quiz = Quiz.query.filter_by(module_id=module.id).first_or_404()
    
    # Charger explicitement les questions et les choix
    questions = Question.query.filter_by(quiz_id=quiz.id).order_by(Question.id).all()
    
    # Pour chaque question, charger ses choix
    for question in questions:
        question.choices = Choice.query.filter_by(question_id=question.id).order_by(Choice.id).all()
    
    # Assigner les questions au quiz
    quiz.questions = questions
    
    # Initialiser la progression de l'utilisateur s'il n'en a pas
    progress = UserProgress.query.filter_by(user_id=current_user.id, module_id=module.id).first()
    if not progress:
        progress = UserProgress(user_id=current_user.id, module_id=module_id)
        db.session.add(progress)
        db.session.commit()
    
    # Vérifier si l'utilisateur est en train de refaire un quiz (suite à l'appel de retake_quiz)
    retaking = request.args.get('retaking', 'false') == 'true' or session.get('retaking_quiz', False)
    force_quiz = request.args.get('force', 'false') == 'true'
    
    # Si l'utilisateur vient de cliquer sur "Refaire le quiz", initialiser la session
    if retaking and 'previous_completion' not in session:
        # Stocker l'historique de complétion dans la session pour le rétablir si nécessaire
        try:
            completed_at_str = progress.completed_at.isoformat() if progress.completed_at else None
            session['previous_completion'] = {
                'module_id': module_id,
                'completed': progress.completed,
                'score': progress.score,
                'completed_at': completed_at_str
            }
            session['retaking_quiz'] = True
            current_app.logger.info(f'User {current_user.id} accessing quiz for module {module_id} for retake. Previous completion status stored.')
        except Exception as e:
            current_app.logger.error(f'Error storing previous completion status: {str(e)}')
            session['previous_completion'] = {
                'module_id': module_id,
                'completed': progress.completed,
                'score': progress.score,
                'completed_at': None
            }
    
    # Si l'utilisateur a déjà complété ce quiz et ne demande pas à le refaire ou ne force pas l'affichage, rediriger vers les résultats
    if progress.completed and progress.score is not None and progress.score >= quiz.passing_score and not retaking and not force_quiz:
        return redirect(url_for('modules.quiz_results', module_id=module.id))

    # Utiliser le même template de quiz pour tous les modules
    # Pour certains modules, utiliser des templates spécifiques
    # Vérifier par le titre plutôt que par l'ID qui peut varier selon la base de données
    module_title_lower = module.title.lower()
    
    # Use unified quiz template for all modules with enhanced phishing visual examples
    return render_template('quiz/unified_quiz.html', module=module, quiz=quiz, progress=progress)

@modules.route('/<int:module_id>/submit-quiz', methods=['POST'])
@login_required
def submit_quiz(module_id):
    """Traite la soumission d'un quiz."""
    try:
        module = Module.query.get_or_404(module_id)
        quiz = Quiz.query.filter_by(module_id=module.id).first_or_404()
        
        # Load questions and choices explicitly
        questions = Question.query.filter_by(quiz_id=quiz.id).order_by(Question.id).all()
        
        if not questions:
            flash('Aucune question trouvée pour ce quiz.', 'error')
            return redirect(url_for('modules.quiz', module_id=module_id))
        
        # For each question, load its choices
        for question in questions:
            question.choices = Choice.query.filter_by(question_id=question.id).order_by(Choice.id).all()
        
        # Assign questions to quiz
        quiz.questions = questions
        
        # Récupérer les réponses du formulaire
        answers = []
        score = 0
        total_questions = len(quiz.questions)
        
        current_app.logger.info(f'Processing quiz submission for user {current_user.id}, module {module_id}, {total_questions} questions')
        
        for question in quiz.questions:
            answer_key = f'question_{question.id}'
            user_answer_id = request.form.get(answer_key)
            
            # Trouver la réponse correcte
            correct_choice = next((choice for choice in question.choices if choice.is_correct), None)
            
            if not correct_choice:
                current_app.logger.warning(f'No correct choice found for question {question.id}')
                continue
            
            # Récupérer le texte des réponses (pas seulement les IDs)
            user_choice = None
            if user_answer_id:
                try:
                    user_choice = Choice.query.get(int(user_answer_id))
                except (ValueError, TypeError) as e:
                    current_app.logger.error(f'Invalid answer ID {user_answer_id} for question {question.id}: {str(e)}')
                    user_choice = None
                
            is_correct = False
            if correct_choice and user_answer_id and user_choice and user_choice.id == correct_choice.id:
                score += 1
                is_correct = True
            
            # Ajouter les détails à la liste des réponses
            answers.append({
                'question_id': question.id,
                'question_text': question.content,
                'user_answer': user_choice.content if user_choice else "Aucune réponse",
                'correct_answer': correct_choice.content if correct_choice else "Inconnue",
                'is_correct': is_correct,
                'feedback': "Bonne réponse!" if is_correct else "Réponse incorrecte. Revoyez cette section du module."
            })
    
        # Calculer le pourcentage
        percentage = round((score / total_questions) * 100, 1) if total_questions > 0 else 0
        current_app.logger.info(f'Quiz score calculation: {score}/{total_questions} = {percentage:.1f}%')
        
        # Mettre à jour la progression de l'utilisateur (UserProgress pour compatibilité)
        progress = UserProgress.query.filter_by(user_id=current_user.id, module_id=module.id).first()
        # Si l'utilisateur n'a pas encore de progression pour ce module (par exemple, accès direct au quiz)
        if not progress:
            current_app.logger.warning(
                f'Création automatique d\'une progression pour l\'utilisateur {current_user.id} et le module {module_id}.'
            )
            progress = UserProgress(user_id=current_user.id, module_id=module.id, started_at=db.func.now())
            db.session.add(progress)
        
        # Mettre à jour ou créer QuizProgress pour le quiz spécifique
        quiz_progress = QuizProgress.query.filter_by(user_id=current_user.id, quiz_id=quiz.id).first()
        
        if not quiz_progress:
            quiz_progress = QuizProgress(user_id=current_user.id, quiz_id=quiz.id)
            db.session.add(quiz_progress)
        
        # Incrémenter le nombre de tentatives (assurer qu'il est initialisé)
        if quiz_progress.attempts is None:
            quiz_progress.attempts = 1
        else:
            quiz_progress.attempts += 1
        
        # Vérifier si l'utilisateur est en train de refaire un quiz
        is_retaking = session.get('retaking_quiz', False)
        previous_completion = session.get('previous_completion', {})
        # Score précédent sauvegardé, utilisé quel que soit le chemin d'exécution suivant
        previous_score = previous_completion.get('score')
        
        if progress:
            # Cas de reprise d'un quiz avec un état de complétion précédent
            if is_retaking and previous_completion and str(module.id) == str(previous_completion.get('module_id')):
                # previous_score déjà défini plus haut
                
                # Mettre à jour QuizProgress avec le nouveau score
                quiz_progress.score = percentage
                quiz_progress.completed = percentage >= quiz.passing_score
                if quiz_progress.completed:
                    quiz_progress.completed_at = db.func.now()
                
                # Ne mettre à jour le score que s'il est meilleur que le score précédent ou si aucun score précédent n'existe
                if previous_score is None or percentage > previous_score:
                    progress.score = percentage
                    current_app.logger.info(f'User {current_user.id} improved score for module {module.id} from {previous_score} to {percentage}.')
                    
                    # Si le nouveau score permet de valider le module mais pas l'ancien
                    if percentage >= quiz.passing_score and (previous_score is None or previous_score < quiz.passing_score):
                        progress.completed = True
                        progress.completed_at = db.func.now()
                    # Tentative d'attribution de badge
                    badge, was_newly_awarded = award_badge_for_module(current_user, module, db, current_app)
                    if was_newly_awarded:
                        # Store badge info in session for congratulations page
                        session['newly_awarded_badge'] = {
                            'badge_id': badge.id,
                            'badge_name': badge.name,
                            'badge_description': badge.description,
                            'badge_image': badge.image_filename,
                            'module_id': module.id,
                            'module_title': module.title,
                            'score': percentage
                        }
                    flash(f'Félicitations! Vous avez réussi le quiz avec un score de {percentage:.1f}%.', 'success')
                else:
                    flash(f'Vous avez amélioré votre score à {percentage:.1f}% (précédemment: {previous_score:.1f}%).', 'success')
            else:
                # Restaurer l'état de complétion précédent si le nouveau score n'est pas meilleur
                progress.score = previous_score
                progress.completed = previous_completion.get('completed', False)
                
                # Gérer la restauration de la date de complétion avec une meilleure gestion des erreurs
                completed_at_str = previous_completion.get('completed_at')
                if completed_at_str:
                    try:
                        from datetime import datetime
                        progress.completed_at = datetime.fromisoformat(completed_at_str)
                        current_app.logger.info(f'Date de complétion restaurée: {completed_at_str}')
                    except (ValueError, TypeError) as e:
                        # En cas d'erreur de conversion, conserver la date actuelle
                        current_app.logger.warning(f'Impossible de convertir la date de complétion: {str(e)}')
                        if progress.completed and not progress.completed_at:
                            progress.completed_at = db.func.now()
                elif progress.completed and not progress.completed_at:
                    # Si le module est complété mais sans date, ajouter la date actuelle
                    progress.completed_at = db.func.now()
                
                # Still update QuizProgress even if module score is not improved
                quiz_progress.score = percentage
                quiz_progress.completed = percentage >= quiz.passing_score
                if quiz_progress.completed:
                    quiz_progress.completed_at = db.func.now()
                
                flash(f'Votre score précédent de {previous_score:.1f}% a été conservé car il est supérieur à votre nouveau score de {percentage:.1f}%.', 'info')
        else:
            # Cas standard (première complétion ou non lié à une reprise)
            # Update QuizProgress
            quiz_progress.score = percentage
            quiz_progress.completed = percentage >= quiz.passing_score
            if quiz_progress.completed:
                quiz_progress.completed_at = db.func.now()
            
            # Update UserProgress for backward compatibility
            progress.score = percentage
            if percentage >= quiz.passing_score:
                progress.completed = True
                progress.completed_at = db.func.now()
                current_app.logger.info(f'User {current_user.id} completed module {module.id}. Attempting to award badge.')
                # Award badge
                badge, was_newly_awarded = award_badge_for_module(current_user, module, db, current_app)
                if was_newly_awarded:
                    # Store badge info in session for congratulations page
                    session['newly_awarded_badge'] = {
                        'badge_id': badge.id,
                        'badge_name': badge.name,
                        'badge_description': badge.description,
                        'badge_image': badge.image_filename,
                        'module_id': module.id,
                        'module_title': module.title,
                        'score': percentage
                    }
                flash(f'Félicitations! Vous avez réussi le quiz avec un score de {percentage:.1f}%.', 'success')
            else:
                flash(f'Vous avez obtenu un score de {percentage:.1f}%. Le score minimum requis est de {quiz.passing_score}%.', 'warning')
        
        db.session.commit() # Commit après toutes les modifications
        
        # Stocker les réponses dans la session pour l'affichage des résultats
        session['quiz_answers'] = answers
        session['quiz_score'] = percentage
        
        # Check if a badge was newly awarded and redirect to congratulations page first
        if 'newly_awarded_badge' in session:
            return redirect(url_for('modules.congratulations', module_id=module.id))
        
        # Rediriger vers la page de résultats
        return redirect(url_for('modules.quiz_results', module_id=module.id, score=percentage))
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Error in quiz submission for user {current_user.id}, module {module_id}: {str(e)}')
        flash('Une erreur est survenue lors de la soumission du quiz. Veuillez réessayer.', 'error')
        return redirect(url_for('modules.quiz', module_id=module_id))
    finally:
        # Toujours nettoyer les variables de session liées à la reprise du quiz
        # même en cas d'erreur ou de redirection anticipée
        if 'retaking_quiz' in session:
            del session['retaking_quiz']
            current_app.logger.info(f'Cleaned retaking_quiz session variable for user {current_user.id}')
        if 'previous_completion' in session:
            del session['previous_completion']
            current_app.logger.info(f'Cleaned previous_completion session variable for user {current_user.id}')

@modules.route('/<int:module_id>/congratulations')
@login_required
def congratulations(module_id):
    """Affiche la page de félicitations après l'obtention d'un badge."""
    # Check if there's badge info in session
    badge_info = session.get('newly_awarded_badge')
    if not badge_info or badge_info.get('module_id') != module_id:
        # No badge info or wrong module, redirect to results
        return redirect(url_for('modules.quiz_results', module_id=module_id))
    
    module = Module.query.get_or_404(module_id)
    badge = db.session.get(Badge, badge_info['badge_id'])
    
    if not badge:
        # Badge not found, redirect to results
        return redirect(url_for('modules.quiz_results', module_id=module_id))
    
    return render_template('modules/congratulations.html',
                         title='Félicitations!',
                         module=module,
                         badge=badge,
                         badge_info=badge_info,
                         user=current_user)

@modules.route('/<int:module_id>/continue-to-results')
@login_required
def continue_to_results(module_id):
    """Nettoie la session et redirige vers les résultats après la page de félicitations."""
    # Clean up the badge session data
    if 'newly_awarded_badge' in session:
        del session['newly_awarded_badge']
    
    # Get score from session for redirect
    score = session.get('quiz_score', 0)
    return redirect(url_for('modules.quiz_results', module_id=module_id, score=score))

@modules.route('/<int:module_id>/results')
@login_required
def quiz_results(module_id):
    """Affiche les résultats d'un quiz."""
    # Get score from URL, default to 0 if not found, and convert to float
    try:
        score = float(request.args.get('score', 0))
    except ValueError:
        score = 0.0
    
    # Récupérer les réponses stockées dans la session
    feedback = session.get('quiz_answers', [])
    session_score = session.get('quiz_score', 0)
    
    # Utiliser le score de la session s'il est disponible
    if session_score and not score:
        score = session_score
    
    module = Module.query.get_or_404(module_id)
    quiz = Quiz.query.filter_by(module_id=module.id).first_or_404()
    progress = UserProgress.query.filter_by(user_id=current_user.id, module_id=module.id).first_or_404()
    
    # Vérifier si tous les modules sont complétés pour afficher un message sur le certificat
    all_modules = Module.query.count()
    completed_modules = UserProgress.query.filter_by(user_id=current_user.id, completed=True).count()
    all_completed = (all_modules == completed_modules)
    
    # Utiliser des templates spécifiques pour certains modules en fonction de leur titre
    module_title_lower = module.title.lower()
    
    # Module de gestion des mots de passe
    if 'mot de passe' in module_title_lower or 'password' in module_title_lower:
        return render_template('modules/password_results.html', 
                           title='Résultats du Quiz - Gestion des mots de passe',
                           module=module,
                           quiz=quiz,
                           progress=progress,
                           score=score,
                           feedback=feedback,
                           all_completed=all_completed)
    # Module de phishing
    elif 'phishing' in module_title_lower or 'hameçonnage' in module_title_lower:
        # Calculer le pourcentage et nombre total de questions pour le template
        percentage = score
        total = len(quiz.questions)
        return render_template('modules/phishing_results.html', 
                           title='Résultats du Quiz - Sensibilisation au Phishing',
                           module=module,
                           quiz=quiz,
                           progress=progress,
                           score=score,
                           percentage=percentage,
                           total=total,
                           feedback=feedback,
                           all_completed=all_completed)
    # Pour les autres modules, utiliser le template générique
    else:
        return render_template('modules/results.html', 
                           title='Résultats du Quiz',
                           module=module,
                           quiz=quiz,
                           progress=progress,
                           score=score,
                           feedback=feedback,
                           all_completed=all_completed)

@modules.route('/certificate')
@login_required
def certificate():
    """Génère un certificat basé sur les modules complétés et les badges obtenus."""
    # Récupérer les modules complétés
    user_progress = UserProgress.query.filter_by(user_id=current_user.id, completed=True).all()
    if not user_progress:
        flash('Vous devez compléter au moins un module pour obtenir votre certificat.', 'warning')
        return redirect(url_for('modules.index'))
    # Calcul du score moyen en excluant les scores None
    scores = [p.score for p in user_progress if p.score is not None]
    avg_score = sum(scores) / len(scores) if scores else 0
    # Modules complétés et badges
    module_ids = [p.module_id for p in user_progress]
    completed_modules = Module.query.filter(Module.id.in_(module_ids)).all()
    badges = current_user.badges.all()  # Fix: call .all() to get actual badge objects
    # Afficher le certificat
    return render_template('modules/certificate.html',
                           title='Certificat de réussite',
                           user=current_user,
                           date=datetime.now(timezone.utc),
                           avg_score=avg_score,
                           modules=completed_modules,
                           badges=badges)

@modules.route('/phishing-simulation')
@login_required
def phishing_simulation():
    return render_template('modules/phishing_simulation.html',
                          title='Simulateur de Phishing')

@modules.route('/password-simulator')
@login_required
def password_simulator():
    return render_template('modules/password_simulator.html',
                          title='Simulateur de Force de Mot de Passe')

@modules.route('/phishing-simulation/evaluate', methods=['POST'])
@login_required
def evaluate_phishing():
    """Évalue les réponses de l'utilisateur à la simulation de phishing."""
    data = request.form
    score = 0
    total = 5  # Nombre total d'exemples d'emails
    
    # Vérifier les réponses (clés example_1, example_2, etc.)
    # Dans un cas réel, vous auriez une logique plus élaborée avec des réponses stockées en BDD
    correct_answers = {
        'example_1': 'phishing',
        'example_2': 'legitimate',
        'example_3': 'phishing',
        'example_4': 'legitimate',
        'example_5': 'phishing'
    }
    
    for key, correct in correct_answers.items():
        if data.get(key) == correct:
            score += 1
    
    percentage = round((score / total) * 100, 1)
    
    # Trouver le module de phishing
    phishing_module = Module.query.filter_by(title='Sensibilisation au Phishing').first()
    
    if phishing_module:
        # Mettre à jour la progression
        progress = UserProgress.query.filter_by(user_id=current_user.id, module_id=phishing_module.id).first()
        
        if progress:
            progress.score = percentage
            if percentage >= 80:  # Seuil de réussite
                progress.completed = True
                progress.completed_at = db.func.now()
                # Award badge
                badge_to_award = Badge.query.filter_by(module_id=phishing_module.id).first()
                if badge_to_award and badge_to_award not in current_user.badges:
                    current_user.badges.append(badge_to_award)
                    flash(f'Nouveau badge débloqué : {badge_to_award.name}!', 'info')
            db.session.commit() # Commit after potential badge awarding and score update
    
    return render_template('modules/phishing_results.html',
                          title='Résultats de la simulation',
                          score=score,
                          total=total,
                          percentage=percentage)

@modules.route('/password-simulator/evaluate', methods=['POST'])
@login_required
def evaluate_password_simulator():
    data = request.form
    score = 0
    total = 11  # Total des questions à évaluer
    
    # Exercice 1: Évaluation de la force des mots de passe (5 questions)
    password_strength = {
        'password1': 'weak',   # Tanger2023
        'password2': 'medium', # P@ssw0rd$123!
        'password3': 'weak',   # tangport1234
        'password4': 'strong', # T@ng3rAll!anc3P0rt#2023
        'password5': 'weak'    # 12345678
    }
    
    for pwd, correct in password_strength.items():
        if data.get(pwd) == correct:
            score += 1
    
    # Exercice 2: Création d'un mot de passe sécurisé (3 questions)
    if data.get('min_length') == '12':
        score += 1
    
    # Pour les types de caractères, on vérifie si au moins 3 sont sélectionnés
    char_types = request.form.getlist('char_types')
    if len(char_types) >= 3:
        score += 1
    
    if data.get('change_frequency') == '90':
        score += 1
    
    # Exercice 3: Gestion des mots de passe (3 questions)
    if data.get('same_password') == 'bad':
        score += 1
    
    if data.get('password_manager') == 'good':
        score += 1
    
    if data.get('password_postit') == 'bad':
        score += 1
    
    percentage = round((score / total) * 100, 1)
    
    # Mise à jour de la progression de l'utilisateur
    password_module = Module.query.filter_by(title='Gestion des mots de passe').first()
    if password_module:
        progress = UserProgress.query.filter_by(user_id=current_user.id, module_id=password_module.id).first()
        if progress:
            progress.score = percentage
            if percentage >= 80:
                progress.completed = True
                progress.completed_at = db.func.now()
                # Award badge
                badge_to_award = Badge.query.filter_by(module_id=password_module.id).first()
                if badge_to_award and badge_to_award not in current_user.badges:
                    current_user.badges.append(badge_to_award)
                    flash(f'Nouveau badge débloqué : {badge_to_award.name}!', 'info')
            db.session.commit() # Commit after potential badge awarding and score update
    
    return render_template('modules/password_results.html',
                          title='Résultats du Simulateur de Mots de Passe',
                          score=score,
                          total=total,
                          percentage=percentage)

@modules.route('/<int:module_id>/retake-quiz', methods=['POST'])
@login_required
def retake_quiz(module_id):
    module = Module.query.get_or_404(module_id)
    progress = UserProgress.query.filter_by(user_id=current_user.id, module_id=module.id).first()

    # Vérifier si le module a des quiz associés
    if not module.quizzes:  # Vérifie si la liste est vide
        flash('Ce module n\'a pas de quiz à refaire.', 'warning')
        return redirect(url_for('modules.view', module_id=module_id))

    if progress:
        # Stocker l'historique de complétion dans la session pour le rétablir si nécessaire
        try:
            completed_at_str = progress.completed_at.isoformat() if progress.completed_at else None
            session['previous_completion'] = {
                'module_id': module_id,
                'completed': progress.completed,
                'score': progress.score,
                'completed_at': completed_at_str
            }
            current_app.logger.info(f'User {current_user.id} is retaking quiz for module {module_id}. Previous completion status stored in session.')
        except Exception as e:
            # En cas d'erreur lors de la conversion, stocker une version simplifiée
            current_app.logger.warning(f"Erreur lors de la conversion de données de progression: {str(e)}")
            session['previous_completion'] = {
                'module_id': module_id,
                'completed': progress.completed,
                'score': progress.score,
                'completed_at': None
            }
            current_app.logger.info(f'User {current_user.id} is retaking quiz for module {module_id}. Simplified completion status stored due to error.')
        
        # Ne pas réinitialiser l'état de complétion, juste marquer qu'un nouveau quiz est en cours
        session['retaking_quiz'] = True
        db.session.commit()
        flash('Vous pouvez maintenant refaire le quiz. Votre progression précédente est sauvegardée.', 'info')
    else:
        # Should not happen if they are retaking, but as a safeguard
        current_app.logger.warning(f'User {current_user.id} attempted to retake quiz for module {module_id} but no prior progress found. Allowing quiz attempt.')
    
    return redirect(url_for('modules.quiz', module_id=module_id, retaking='true'))

@modules.route('/report-phishing', methods=['GET', 'POST'])
@login_required
def report_phishing():
    """Permet aux utilisateurs de signaler des tentatives de phishing."""
    if request.method == 'POST':
        email_sender = request.form.get('email_sender')
        email_subject = request.form.get('email_subject')
        description = request.form.get('description')
        
        # Ici, vous pourriez implémenter l'envoi d'une notification aux administrateurs
        # ou l'enregistrement dans une base de données
        
        flash('Merci d\'avoir signalé cette tentative de phishing. Notre équipe de sécurité va l\'examiner.', 'success')
        return redirect(url_for('main.dashboard'))
    
    return render_template('modules/report_phishing.html', title='Signaler un Phishing')

@modules.route('/<int:module_id>/start', methods=['POST'])
@login_required
def start_module(module_id):
    """Démarre un module pour l'utilisateur."""
    module = Module.query.get_or_404(module_id)
    
    # Check if module is active
    if not module.is_active:
        flash('Ce module n\'est pas disponible actuellement.', 'warning')
        return redirect(url_for('modules.index'))
    
    progress = UserProgress.query.filter_by(user_id=current_user.id, module_id=module.id).first()
    
    if not progress:
        # Créer un nouvel enregistrement de progression
        progress = UserProgress(user_id=current_user.id, module_id=module.id)
        db.session.add(progress)
        db.session.commit()
        flash('Module démarré avec succès!', 'success')
    else:
        flash('Module déjà démarré.', 'info')
    
    return redirect(url_for('modules.view', module_id=module.id))

@modules.route('/<int:module_id>/complete', methods=['POST'])
@login_required
def complete_module(module_id):
    """Marque un module comme complété pour l'utilisateur."""
    module = Module.query.get_or_404(module_id)
    
    # Check if module is active
    if not module.is_active:
        flash('Ce module n\'est pas disponible actuellement.', 'warning')
        return redirect(url_for('modules.index'))
    
    progress = UserProgress.query.filter_by(user_id=current_user.id, module_id=module.id).first()
    
    if not progress:
        # Créer un nouvel enregistrement de progression et le marquer comme complété
        progress = UserProgress(user_id=current_user.id, module_id=module.id, completed=True, completed_at=datetime.now())
        db.session.add(progress)
    else:
        # Marquer comme complété
        progress.completed = True
        progress.completed_at = datetime.now()
    
    db.session.commit()
    flash('Module complété avec succès!', 'success')
    
    return redirect(url_for('modules.view', module_id=module.id))
