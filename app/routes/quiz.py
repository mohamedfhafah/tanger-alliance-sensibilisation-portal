from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify, abort
from flask_login import login_required, current_user
from app.models.module import Quiz, Question, Module, UserProgress, Choice, QuizProgress
from app import db
from app.utils import get_or_404

quiz_bp = Blueprint('quiz', __name__, url_prefix='/quiz')

@quiz_bp.route('/')
@login_required
def quiz_list():
    """Display all quizzes grouped by module with difficulty levels"""
    # Get all active modules with their quizzes
    modules = Module.query.filter_by(is_active=True).order_by(Module.order).all()
    
    # Get user's quiz progress
    user_quiz_progress = {}
    if current_user.is_authenticated:
        progress_records = QuizProgress.query.filter_by(user_id=current_user.id).all()
        for record in progress_records:
            user_quiz_progress[record.quiz_id] = record
    
    # Organize quizzes by module and add unlock status
    modules_data = []
    for module in modules:
        # Get quizzes for this module ordered by difficulty level
        quizzes = Quiz.query.filter_by(
            module_id=module.id, 
            is_active=True
        ).order_by(Quiz.order).all()
        
        # Add unlock status to each quiz
        for quiz in quizzes:
            quiz.is_unlocked = quiz.is_unlocked_for_user(current_user.id)
            quiz.user_progress = user_quiz_progress.get(quiz.id)
        
        if quizzes:  # Only include modules that have quizzes
            modules_data.append({
                'module': module,
                'quizzes': quizzes
            })
    
    return render_template('quiz/quiz_list.html', modules_data=modules_data)

@quiz_bp.route('/module/<int:module_id>')
@login_required
def module_quizzes(module_id):
    """Display all quizzes for a specific module"""
    module = get_or_404(Module, module_id)
    
    if not module.is_active:
        abort(404)
    
    # Get quizzes for this module ordered by difficulty level
    quizzes = Quiz.query.filter_by(
        module_id=module.id, 
        is_active=True
    ).order_by(Quiz.order).all()
    
    # Get user's quiz progress
    user_quiz_progress = {}
    if current_user.is_authenticated:
        progress_records = QuizProgress.query.filter_by(
            user_id=current_user.id
        ).filter(QuizProgress.quiz_id.in_([q.id for q in quizzes])).all()
        
        for record in progress_records:
            user_quiz_progress[record.quiz_id] = record
    
    # Add unlock status and progress to each quiz
    for quiz in quizzes:
        quiz.is_unlocked = quiz.is_unlocked_for_user(current_user.id)
        quiz.user_progress = user_quiz_progress.get(quiz.id)
    
    return render_template('quiz/module_quizzes.html', module=module, quizzes=quizzes)

@quiz_bp.route('/<int:quiz_id>')
@login_required
def view_quiz(quiz_id):
    """Display a quiz with its questions"""
    quiz = get_or_404(Quiz, quiz_id)
    
    # Check if user has access to the module
    module = quiz.module
    if not module or not module.is_active:
        abort(404)
    
    # Check if quiz is unlocked for this user
    if not quiz.is_unlocked_for_user(current_user.id):
        flash('Ce quiz n\'est pas encore déverrouillé. Vous devez d\'abord compléter le quiz précédent.', 'warning')
        return redirect(url_for('main.quiz'))
    
    # Load questions and choices explicitly
    questions = Question.query.filter_by(quiz_id=quiz_id).order_by(Question.id).all()
    
    # For each question, load its choices
    for question in questions:
        question.choices = Choice.query.filter_by(question_id=question.id).order_by(Choice.id).all()
    
    # Assign questions to quiz
    quiz.questions = questions
    
    # Get user progress for the module (backward compatibility)
    progress = UserProgress.query.filter_by(
        user_id=current_user.id,
        module_id=quiz.module_id
    ).first()
    
    if not progress:
        progress = UserProgress(user_id=current_user.id, module_id=quiz.module_id)
        db.session.add(progress)
        db.session.commit()
    
    # Get quiz-specific progress
    quiz_progress = QuizProgress.query.filter_by(
        user_id=current_user.id,
        quiz_id=quiz_id
    ).first()
    
    if not quiz_progress:
        quiz_progress = QuizProgress(user_id=current_user.id, quiz_id=quiz_id)
        db.session.add(quiz_progress)
        db.session.commit()
    
    # Check if already completed and not retaking
    retaking = request.args.get('retaking', 'false') == 'true'
    force_quiz = request.args.get('force', 'false') == 'true'
    
    if (quiz_progress.completed and quiz_progress.score is not None and 
        quiz_progress.score >= quiz.passing_score and not retaking and not force_quiz):
        return redirect(url_for('quiz.quiz_results', quiz_id=quiz_id))
    
    # Use unified quiz template for all modules
    return render_template('quiz/unified_quiz.html', 
                         quiz=quiz, 
                         questions=questions,
                         progress=progress,
                         quiz_progress=quiz_progress,
                         module=module)

@quiz_bp.route('/<int:quiz_id>/submit', methods=['POST'])
@login_required
def submit_quiz(quiz_id):
    """Handle quiz submission by redirecting to modules submit route"""
    quiz = get_or_404(Quiz, quiz_id)
    module = quiz.module
    
    # Check if user has access to the module
    if not module or not module.is_active:
        abort(404)
    
    # Redirect to the modules submit route which has all the badge logic
    return redirect(url_for('modules.submit_quiz', module_id=module.id), code=307)

@quiz_bp.route('/<int:quiz_id>/start', methods=['GET', 'POST'])
@login_required
def start_quiz(quiz_id):
    """Start a quiz session"""
    quiz = get_or_404(Quiz, quiz_id)
    
    # Check if user has access to the module
    module = quiz.module
    if not module or not module.is_active:
        abort(404)
    
    questions = Question.query.filter_by(quiz_id=quiz_id).all()
    
    return render_template('quiz/start.html', 
                         quiz=quiz, 
                         questions=questions,
                         module=module)

@quiz_bp.route('/<int:quiz_id>/question/<int:question_num>')
@login_required
def view_question(quiz_id, question_num):
    """Display a specific question in the quiz"""
    quiz = get_or_404(Quiz, quiz_id)
    
    # Check if user has access to the module
    module = quiz.module
    if not module or not module.is_active:
        abort(404)
    
    questions = Question.query.filter_by(quiz_id=quiz_id).all()
    
    if question_num < 1 or question_num > len(questions):
        abort(404)
    
    question = questions[question_num - 1]
    
    return render_template('quiz/question.html', 
                         quiz=quiz, 
                         question=question,
                         question_num=question_num,
                         total_questions=len(questions),
                         module=module)

@quiz_bp.route('/<int:quiz_id>/answer', methods=['POST'])
@login_required
def submit_answer(quiz_id):
    """Submit an answer for a quiz question"""
    quiz = get_or_404(Quiz, quiz_id)
    
    question_id = request.form.get('question_id')
    answer = request.form.get('answer')
    
    if not question_id or not answer:
        flash('Réponse invalide', 'error')
        return redirect(url_for('quiz.view_quiz', quiz_id=quiz_id))
    
    try:
        question_id = int(question_id)
    except (ValueError, TypeError):
        return jsonify({'error': 'ID de question invalide'}), 400
    
    # Validate that the question exists and belongs to this quiz
    question = Question.query.filter_by(id=question_id, quiz_id=quiz_id).first()
    if not question:
        return jsonify({'error': 'Question non trouvée'}), 404
    
    # Here you would typically save the answer to the database
    # For now, just return success
    
    return jsonify({'success': True, 'message': 'Réponse enregistrée'})

@quiz_bp.route('/<int:quiz_id>/results')
@login_required
def quiz_results(quiz_id):
    """Display quiz results"""
    quiz = get_or_404(Quiz, quiz_id)
    
    # Check if user has access to the module
    module = quiz.module
    if not module or not module.is_active:
        abort(404)
    
    # Get quiz-specific progress
    quiz_progress = QuizProgress.query.filter_by(
        user_id=current_user.id,
        quiz_id=quiz_id
    ).first()
    
    # Get module progress for backward compatibility
    progress = UserProgress.query.filter_by(
        user_id=current_user.id,
        module_id=quiz.module_id
    ).first()
    
    return render_template('quiz/results.html', 
                         quiz=quiz, 
                         progress=progress,
                         quiz_progress=quiz_progress)

@quiz_bp.route('/<int:quiz_id>/review')
def review_quiz(quiz_id):
    """Review quiz answers and results"""
    quiz = get_or_404(Quiz, quiz_id)
    
    # Check if user has access to the module
    module = quiz.module
    if not module or not module.is_active:
        abort(404)
    
    # Get user progress
    progress = None
    if current_user.is_authenticated:
        progress = UserProgress.query.filter_by(
            user_id=current_user.id,
            module_id=quiz.module_id
        ).first()
    
    questions = Question.query.filter_by(quiz_id=quiz_id).all()
    
    return render_template('quiz/review.html', 
                         quiz=quiz, 
                         questions=questions,
                         progress=progress,
                         module=module)

@quiz_bp.route('/<int:quiz_id>/retake', methods=['POST'])
@login_required
def retake_quiz(quiz_id):
    """Allow user to retake a quiz"""
    quiz = get_or_404(Quiz, quiz_id)
    
    # Check if user has access to the module
    module = quiz.module
    if not module or not module.is_active:
        abort(404)
    
    # Reset quiz progress for retake
    if current_user.is_authenticated:
        # Reset quiz-specific progress
        quiz_progress = QuizProgress.query.filter_by(
            user_id=current_user.id,
            quiz_id=quiz_id
        ).first()
        
        if quiz_progress:
            quiz_progress.completed = False
            quiz_progress.score = None
            quiz_progress.completed_at = None
            quiz_progress.attempts += 1
        
        # Also reset module progress for backward compatibility
        progress = UserProgress.query.filter_by(
            user_id=current_user.id,
            module_id=quiz.module_id
        ).first()
        
        if progress:
            progress.completed = False
            progress.score = None
            progress.completed_at = None
        
        db.session.commit()
    
    flash('Quiz réinitialisé. Vous pouvez le reprendre maintenant.', 'success')
    return redirect(url_for('quiz.view_quiz', quiz_id=quiz_id))

@quiz_bp.route('/<int:quiz_id>/validate', methods=['POST'])
@login_required
def validate_quiz_session(quiz_id):
    """Validate quiz session before allowing submission"""
    quiz = get_or_404(Quiz, quiz_id)
    
    # Check if user has access to the module
    module = quiz.module
    if not module or not module.is_active:
        return jsonify({'error': 'Quiz non disponible'}), 404
    
    # Check if user is authenticated properly
    if not current_user.is_authenticated:
        return redirect(url_for('auth.login'))
    
    return jsonify({'success': True, 'message': 'Session valide'})
