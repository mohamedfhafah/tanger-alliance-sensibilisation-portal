"""Module Routes V2

Refactored module routes with clean separation of concerns:
- Simplified route handlers
- Service layer integration
- Proper error handling
- RESTful API design
"""

from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from flask_login import login_required, current_user
from typing import Dict, Any, Optional
import logging

from app.services.module_service import ModuleService
from app.services.quiz_service import QuizService
from app.services.progress_service import ProgressService
from app.services.content_service import ContentService
from app.services.badge_service import BadgeService

# Create blueprint
modules_v2_bp = Blueprint('modules_v2', __name__, url_prefix='/modules/v2')

# Setup logging
logger = logging.getLogger(__name__)


@modules_v2_bp.route('/')
@login_required
def module_list():
    """Display list of all modules"""
    try:
        # Get modules with user progress
        modules = ModuleService.get_modules_with_progress(current_user.id)
        
        # Get user's overall progress summary
        progress_summary = ProgressService.get_user_progress_summary(current_user.id)
        
        # Get recent badges
        recent_badges = BadgeService.get_user_badges(current_user.id, limit=3)
        
        return render_template(
            'modules_v2/module_list.html',
            modules=modules,
            progress_summary=progress_summary,
            recent_badges=recent_badges,
            title="Security Training Modules"
        )
        
    except Exception as e:
        logger.error(f"Error loading module list: {str(e)}")
        flash("An error occurred while loading modules.", "error")
        return redirect(url_for('main.dashboard'))


@modules_v2_bp.route('/<int:module_id>')
@login_required
def module_detail(module_id: int):
    """Display module detail page"""
    try:
        # Get module with content
        module_data = ContentService.get_module_content(module_id, current_user.id)
        if not module_data:
            flash("Module not found or not accessible.", "error")
            return redirect(url_for('modules_v2.module_list'))
        
        # Check prerequisites
        can_access, missing_prereqs = ModuleService.check_prerequisites(
            module_id, current_user.id
        )
        
        if not can_access:
            return render_template(
                'modules_v2/module_prerequisites.html',
                module=module_data['module'],
                missing_prerequisites=missing_prereqs,
                title=f"Prerequisites Required - {module_data['module']['title']}"
            )
        
        # Get user progress for this module
        progress = ProgressService.get_user_module_progress(current_user.id, module_id)
        
        # Get associated quiz if exists
        quiz_data = None
        if module_data['module'].get('has_quiz'):
            quiz_data = QuizService.get_quiz_by_module(module_id)
        
        # Start module progress if not started
        if not progress:
            ProgressService.start_module(current_user.id, module_id)
            progress = ProgressService.get_user_module_progress(current_user.id, module_id)
        
        return render_template(
            'modules_v2/module_detail.html',
            module_data=module_data,
            progress=progress,
            quiz_data=quiz_data,
            title=module_data['module']['title']
        )
        
    except Exception as e:
        logger.error(f"Error loading module {module_id}: {str(e)}")
        flash("An error occurred while loading the module.", "error")
        return redirect(url_for('modules_v2.module_list'))


@modules_v2_bp.route('/<int:module_id>/complete', methods=['POST'])
@login_required
def complete_module(module_id: int):
    """Mark module as completed"""
    try:
        # Check if user can access module
        can_access, _ = ModuleService.check_prerequisites(module_id, current_user.id)
        if not can_access:
            return jsonify({
                'success': False,
                'message': 'Prerequisites not met.'
            }), 403
        
        # Complete the module
        success, message = ProgressService.complete_module(current_user.id, module_id)
        
        if success:
            # Check for new badges
            new_badges = BadgeService.check_and_award_badges(current_user.id)
            
            return jsonify({
                'success': True,
                'message': message,
                'new_badges': [badge.to_dict() for badge in new_badges],
                'redirect_url': url_for('modules_v2.module_list')
            })
        else:
            return jsonify({
                'success': False,
                'message': message
            }), 400
            
    except Exception as e:
        logger.error(f"Error completing module {module_id}: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'An error occurred while completing the module.'
        }), 500


@modules_v2_bp.route('/<int:module_id>/progress', methods=['POST'])
@login_required
def update_progress(module_id: int):
    """Update module progress"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'message': 'No data provided.'
            }), 400
        
        # Validate progress percentage
        progress_percentage = data.get('progress_percentage')
        if progress_percentage is None or not (0 <= progress_percentage <= 100):
            return jsonify({
                'success': False,
                'message': 'Invalid progress percentage.'
            }), 400
        
        # Update progress
        success, message = ProgressService.update_progress_percentage(
            current_user.id, module_id, progress_percentage
        )
        
        if success:
            # Record time spent if provided
            time_spent = data.get('time_spent_minutes')
            if time_spent:
                ProgressService.record_time_spent(
                    current_user.id, module_id, time_spent
                )
            
            return jsonify({
                'success': True,
                'message': message
            })
        else:
            return jsonify({
                'success': False,
                'message': message
            }), 400
            
    except Exception as e:
        logger.error(f"Error updating progress for module {module_id}: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'An error occurred while updating progress.'
        }), 500


@modules_v2_bp.route('/<int:module_id>/quiz')
@login_required
def module_quiz(module_id: int):
    """Display module quiz"""
    try:
        # Check module access
        can_access, missing_prereqs = ModuleService.check_prerequisites(
            module_id, current_user.id
        )
        
        if not can_access:
            flash("You must complete the required prerequisites first.", "warning")
            return redirect(url_for('modules_v2.module_detail', module_id=module_id))
        
        # Get quiz data
        quiz_data = QuizService.get_quiz_by_module(module_id)
        if not quiz_data:
            flash("Quiz not found for this module.", "error")
            return redirect(url_for('modules_v2.module_detail', module_id=module_id))
        
        # Get user's quiz attempts
        attempts = QuizService.get_user_attempts(current_user.id, quiz_data['id'])
        
        # Check if user can take quiz (attempt limits, etc.)
        can_attempt, reason = QuizService.can_user_attempt_quiz(
            current_user.id, quiz_data['id']
        )
        
        if not can_attempt:
            flash(f"Cannot take quiz: {reason}", "warning")
            return redirect(url_for('modules_v2.module_detail', module_id=module_id))
        
        return render_template(
            'modules_v2/module_quiz.html',
            quiz_data=quiz_data,
            attempts=attempts,
            module_id=module_id,
            title=f"Quiz - {quiz_data['title']}"
        )
        
    except Exception as e:
        logger.error(f"Error loading quiz for module {module_id}: {str(e)}")
        flash("An error occurred while loading the quiz.", "error")
        return redirect(url_for('modules_v2.module_detail', module_id=module_id))


@modules_v2_bp.route('/<int:module_id>/quiz/attempt', methods=['POST'])
@login_required
def start_quiz_attempt(module_id: int):
    """Start a new quiz attempt"""
    try:
        # Get quiz data
        quiz_data = QuizService.get_quiz_by_module(module_id)
        if not quiz_data:
            return jsonify({
                'success': False,
                'message': 'Quiz not found.'
            }), 404
        
        # Check if user can attempt
        can_attempt, reason = QuizService.can_user_attempt_quiz(
            current_user.id, quiz_data['id']
        )
        
        if not can_attempt:
            return jsonify({
                'success': False,
                'message': reason
            }), 403
        
        # Start attempt
        success, message, attempt_data = QuizService.start_quiz_attempt(
            current_user.id, quiz_data['id']
        )
        
        if success:
            return jsonify({
                'success': True,
                'message': message,
                'attempt_id': attempt_data['id'],
                'redirect_url': url_for(
                    'modules_v2.quiz_attempt',
                    module_id=module_id,
                    attempt_id=attempt_data['id']
                )
            })
        else:
            return jsonify({
                'success': False,
                'message': message
            }), 400
            
    except Exception as e:
        logger.error(f"Error starting quiz attempt for module {module_id}: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'An error occurred while starting the quiz.'
        }), 500


@modules_v2_bp.route('/<int:module_id>/quiz/attempt/<int:attempt_id>')
@login_required
def quiz_attempt(module_id: int, attempt_id: int):
    """Display quiz attempt page"""
    try:
        # Get attempt data
        attempt_data = QuizService.get_attempt_details(attempt_id, current_user.id)
        if not attempt_data:
            flash("Quiz attempt not found.", "error")
            return redirect(url_for('modules_v2.module_quiz', module_id=module_id))
        
        # Check if attempt is still active
        if attempt_data['status'] != 'in_progress':
            flash("This quiz attempt is no longer active.", "warning")
            return redirect(url_for('modules_v2.quiz_results', 
                                  module_id=module_id, attempt_id=attempt_id))
        
        return render_template(
            'modules_v2/quiz_attempt.html',
            attempt_data=attempt_data,
            module_id=module_id,
            title=f"Quiz Attempt - {attempt_data['quiz']['title']}"
        )
        
    except Exception as e:
        logger.error(f"Error loading quiz attempt {attempt_id}: {str(e)}")
        flash("An error occurred while loading the quiz attempt.", "error")
        return redirect(url_for('modules_v2.module_quiz', module_id=module_id))


@modules_v2_bp.route('/<int:module_id>/quiz/attempt/<int:attempt_id>/submit', methods=['POST'])
@login_required
def submit_quiz_attempt(module_id: int, attempt_id: int):
    """Submit quiz attempt"""
    try:
        data = request.get_json()
        if not data or 'answers' not in data:
            return jsonify({
                'success': False,
                'message': 'No answers provided.'
            }), 400
        
        # Submit attempt
        success, message, results = QuizService.submit_quiz_attempt(
            attempt_id, current_user.id, data['answers']
        )
        
        if success:
            # Check for module completion and badges
            if results.get('passed'):
                # Complete module if quiz passed
                ProgressService.complete_module(current_user.id, module_id)
                
                # Check for new badges
                new_badges = BadgeService.check_and_award_badges(current_user.id)
                results['new_badges'] = [badge.to_dict() for badge in new_badges]
            
            return jsonify({
                'success': True,
                'message': message,
                'results': results,
                'redirect_url': url_for(
                    'modules_v2.quiz_results',
                    module_id=module_id,
                    attempt_id=attempt_id
                )
            })
        else:
            return jsonify({
                'success': False,
                'message': message
            }), 400
            
    except Exception as e:
        logger.error(f"Error submitting quiz attempt {attempt_id}: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'An error occurred while submitting the quiz.'
        }), 500


@modules_v2_bp.route('/<int:module_id>/quiz/attempt/<int:attempt_id>/results')
@login_required
def quiz_results(module_id: int, attempt_id: int):
    """Display quiz results"""
    try:
        # Get attempt results
        results = QuizService.get_attempt_results(attempt_id, current_user.id)
        if not results:
            flash("Quiz results not found.", "error")
            return redirect(url_for('modules_v2.module_quiz', module_id=module_id))
        
        # Get module data for context
        module_data = ModuleService.get_module_by_id(module_id)
        
        return render_template(
            'modules_v2/quiz_results.html',
            results=results,
            module_data=module_data,
            module_id=module_id,
            title=f"Quiz Results - {results['quiz']['title']}"
        )
        
    except Exception as e:
        logger.error(f"Error loading quiz results {attempt_id}: {str(e)}")
        flash("An error occurred while loading quiz results.", "error")
        return redirect(url_for('modules_v2.module_quiz', module_id=module_id))


@modules_v2_bp.route('/search')
@login_required
def search_modules():
    """Search modules and content"""
    try:
        query = request.args.get('q', '').strip()
        if not query:
            return redirect(url_for('modules_v2.module_list'))
        
        # Search modules
        modules = ModuleService.search_modules(query, current_user.id)
        
        # Search content
        content_results = ContentService.search_content(query)
        
        return render_template(
            'modules_v2/search_results.html',
            query=query,
            modules=modules,
            content_results=content_results,
            title=f"Search Results for '{query}'"
        )
        
    except Exception as e:
        logger.error(f"Error searching modules: {str(e)}")
        flash("An error occurred while searching.", "error")
        return redirect(url_for('modules_v2.module_list'))


@modules_v2_bp.route('/progress')
@login_required
def user_progress():
    """Display user's overall progress"""
    try:
        # Get comprehensive progress data
        progress_summary = ProgressService.get_user_progress_summary(current_user.id)
        module_analytics = ProgressService.get_user_module_analytics(current_user.id)
        recent_activity = ProgressService.get_recent_activity(current_user.id, limit=10)
        
        # Get badges
        user_badges = BadgeService.get_user_badges(current_user.id)
        badge_progress = BadgeService.get_badge_progress(current_user.id)
        
        return render_template(
            'modules_v2/user_progress.html',
            progress_summary=progress_summary,
            module_analytics=module_analytics,
            recent_activity=recent_activity,
            user_badges=user_badges,
            badge_progress=badge_progress,
            title="My Progress"
        )
        
    except Exception as e:
        logger.error(f"Error loading user progress: {str(e)}")
        flash("An error occurred while loading progress data.", "error")
        return redirect(url_for('modules_v2.module_list'))


@modules_v2_bp.route('/badges')
@login_required
def user_badges():
    """Display user's badges"""
    try:
        # Get user badges
        user_badges = BadgeService.get_user_badges(current_user.id)
        badge_stats = BadgeService.get_user_badge_stats(current_user.id)
        
        # Get leaderboard
        leaderboard = BadgeService.get_leaderboard(limit=10)
        
        return render_template(
            'modules_v2/user_badges.html',
            user_badges=user_badges,
            badge_stats=badge_stats,
            leaderboard=leaderboard,
            title="My Badges"
        )
        
    except Exception as e:
        logger.error(f"Error loading user badges: {str(e)}")
        flash("An error occurred while loading badges.", "error")
        return redirect(url_for('modules_v2.module_list'))


# API Endpoints for AJAX requests
@modules_v2_bp.route('/api/modules')
@login_required
def api_modules():
    """API endpoint to get modules data"""
    try:
        modules = ModuleService.get_modules_with_progress(current_user.id)
        return jsonify({
            'success': True,
            'modules': modules
        })
    except Exception as e:
        logger.error(f"API error getting modules: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Failed to load modules.'
        }), 500


@modules_v2_bp.route('/api/progress/<int:module_id>')
@login_required
def api_module_progress(module_id: int):
    """API endpoint to get module progress"""
    try:
        progress = ProgressService.get_user_module_progress(current_user.id, module_id)
        return jsonify({
            'success': True,
            'progress': progress
        })
    except Exception as e:
        logger.error(f"API error getting module progress: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Failed to load progress.'
        }), 500


# Error handlers
@modules_v2_bp.errorhandler(404)
def not_found_error(error):
    """Handle 404 errors"""
    return render_template(
        'modules_v2/error.html',
        error_code=404,
        error_message="The requested module or page was not found.",
        title="Page Not Found"
    ), 404


@modules_v2_bp.errorhandler(403)
def forbidden_error(error):
    """Handle 403 errors"""
    return render_template(
        'modules_v2/error.html',
        error_code=403,
        error_message="You don't have permission to access this resource.",
        title="Access Forbidden"
    ), 403


@modules_v2_bp.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    logger.error(f"Internal server error: {str(error)}")
    return render_template(
        'modules_v2/error.html',
        error_code=500,
        error_message="An internal server error occurred. Please try again later.",
        title="Server Error"
    ), 500