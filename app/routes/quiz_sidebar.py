from flask import Blueprint, render_template, jsonify, request
from flask_login import login_required, current_user
from app.models.module import Module, Quiz, UserProgress, QuizProgress
from app import db

quiz_sidebar_bp = Blueprint('quiz_sidebar', __name__)

@quiz_sidebar_bp.route('/api/quiz-sidebar-data')
@login_required
def get_quiz_sidebar_data():
    """API endpoint to get quiz data for sidebar with multi-level support"""
    
    # Get all modules with their quizzes
    modules = Module.query.filter_by(is_active=True).order_by(Module.order).all()
    
    quiz_data = []
    
    for module in modules:
        # Get all quizzes for this module ordered by difficulty level
        quizzes = Quiz.query.filter_by(
            module_id=module.id, 
            is_active=True
        ).order_by(Quiz.order).all()
        
        if not quizzes:
            continue
        
        # Get user progress for this module (legacy)
        module_progress = UserProgress.query.filter_by(
            user_id=current_user.id,
            module_id=module.id
        ).first()
        
        # Get quiz-specific progress
        quiz_progress_records = QuizProgress.query.filter_by(
            user_id=current_user.id
        ).filter(QuizProgress.quiz_id.in_([q.id for q in quizzes])).all()
        
        quiz_progress_map = {record.quiz_id: record for record in quiz_progress_records}
        
        for quiz in quizzes:
            quiz_progress = quiz_progress_map.get(quiz.id)
            
            # Determine quiz status
            quiz_status = 'locked'
            quiz_score = None
            quiz_completed = False
            
            # Check if quiz is unlocked
            if quiz.is_unlocked_for_user(current_user.id):
                quiz_status = 'unlocked'
                
                if quiz_progress:
                    if quiz_progress.completed and quiz_progress.score is not None:
                        quiz_completed = quiz_progress.score >= quiz.passing_score
                        quiz_status = 'completed' if quiz_completed else 'failed'
                        quiz_score = quiz_progress.score
            
            quiz_info = {
                'id': quiz.id,
                'title': quiz.title,
                'module_id': module.id,
                'module_title': module.title,
                'difficulty_level': quiz.difficulty_level,
                'order': quiz.order,
                'status': quiz_status,
                'score': quiz_score,
                'completed': quiz_completed,
                'passing_score': quiz.passing_score,
                'attempts': quiz_progress.attempts if quiz_progress else 0,
                'is_unlocked': quiz.is_unlocked_for_user(current_user.id)
            }
            
            quiz_data.append(quiz_info)
    
    # Group quizzes by module, keeping multiple difficulty levels together
    modules_map = {}
    
    for quiz in quiz_data:
        module_id = quiz['module_id']
        module_title = quiz['module_title']
        
        if module_id not in modules_map:
            modules_map[module_id] = {
                'title': module_title,
                'quizzes': [],
                'total_quizzes': 0,
                'completed_quizzes': 0,
                'category': 'Autres'  # Default category
            }
            
            # Categorize module
            title_lower = module_title.lower()
            if 'mot de passe' in title_lower or 'password' in title_lower:
                modules_map[module_id]['category'] = 'Sécurité des mots de passe'
            elif 'phishing' in title_lower or 'hameçonnage' in title_lower:
                modules_map[module_id]['category'] = 'Sensibilisation au phishing'
            elif 'vulnérabilité' in title_lower or 'vulnerability' in title_lower:
                modules_map[module_id]['category'] = 'Gestion des vulnérabilités'
            elif 'données' in title_lower or 'data' in title_lower or 'protection' in title_lower:
                modules_map[module_id]['category'] = 'Protection des données'
            elif 'mobile' in title_lower:
                modules_map[module_id]['category'] = 'Sécurité mobile'
            elif 'réseau' in title_lower or 'network' in title_lower:
                modules_map[module_id]['category'] = 'Sécurité réseau'
        
        # Add difficulty level indicators
        difficulty_mapping = {
            'beginner': {'stars': '⭐', 'text': 'Débutant', 'level': 1, 'color': 'success'},
            'intermediate': {'stars': '⭐⭐', 'text': 'Intermédiaire', 'level': 2, 'color': 'warning'},
            'advanced': {'stars': '⭐⭐⭐', 'text': 'Avancé', 'level': 3, 'color': 'danger'}
        }
        
        difficulty_info = difficulty_mapping.get(quiz['difficulty_level'], 
                                               difficulty_mapping['beginner'])
        
        quiz['difficulty_display'] = {
            'stars': difficulty_info['stars'],
            'text': difficulty_info['text'],
            'level': difficulty_info['level'],
            'color': difficulty_info['color']
        }
        
        modules_map[module_id]['quizzes'].append(quiz)
        modules_map[module_id]['total_quizzes'] += 1
        
        if quiz['completed']:
            modules_map[module_id]['completed_quizzes'] += 1
    
    # Group by categories
    grouped_quizzes = {}
    for module_data in modules_map.values():
        category = module_data['category']
        if category not in grouped_quizzes:
            grouped_quizzes[category] = []
        
        # Calculate module completion percentage
        completion_percentage = 0
        if module_data['total_quizzes'] > 0:
            completion_percentage = round((module_data['completed_quizzes'] / module_data['total_quizzes']) * 100)
        
        module_data['completion_percentage'] = completion_percentage
        grouped_quizzes[category].append(module_data)
    
    # Sort modules within each category by completion status and then by title
    for category in grouped_quizzes:
        grouped_quizzes[category].sort(key=lambda x: (-x['completion_percentage'], x['title']))
    
    # Remove empty categories
    grouped_quizzes = {k: v for k, v in grouped_quizzes.items() if v}
    
    return jsonify({
        'success': True,
        'quiz_groups': grouped_quizzes
    })