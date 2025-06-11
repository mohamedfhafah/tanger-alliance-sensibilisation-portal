"""Quiz Service

This service handles all quiz-related business logic including:
- Quiz management and retrieval
- Quiz attempt handling
- Score calculation and validation
- Quiz analytics
"""

from typing import List, Dict, Optional, Tuple
from datetime import datetime
from app import db
from app.models.quiz_v2 import QuizV2, QuestionV2, ChoiceV2, QuizAttemptV2, QuizAnalyticsV2
from app.models.module_v2 import ModuleProgressV2
from .progress_service import ProgressService
from .badge_service import BadgeService


class QuizService:
    """Service for quiz operations"""
    
    @staticmethod
    def get_quiz_by_module(module_id: int) -> Optional[Dict]:
        """Get quiz for a specific module
        
        Args:
            module_id: Module ID
            
        Returns:
            Quiz dictionary or None if not found
        """
        quiz = QuizV2.get_by_module(module_id)
        return quiz.to_dict(include_questions=True) if quiz else None
    
    @staticmethod
    def get_quiz_for_attempt(quiz_id: int, user_id: int) -> Optional[Dict]:
        """Get quiz data for a new attempt
        
        Args:
            quiz_id: Quiz ID
            user_id: User ID
            
        Returns:
            Quiz dictionary with questions (without correct answers) or None
        """
        quiz = QuizV2.query.filter_by(id=quiz_id, is_active=True).first()
        if not quiz:
            return None
        
        # Check if user can take the quiz
        can_attempt, message = QuizService.can_user_attempt_quiz(user_id, quiz_id)
        if not can_attempt:
            return None
        
        # Get quiz data without correct answers
        quiz_data = quiz.to_dict()
        
        # Get questions for this attempt (randomized if configured)
        questions = quiz.get_questions_for_attempt()
        quiz_data['questions'] = [
            q.to_dict(include_choices=True, include_correct_answer=False) 
            for q in questions
        ]
        
        # Add user's attempt history
        attempts = QuizService.get_user_attempts(user_id, quiz_id)
        quiz_data['user_attempts'] = len(attempts)
        quiz_data['max_attempts_reached'] = len(attempts) >= quiz.max_attempts
        
        return quiz_data
    
    @staticmethod
    def can_user_attempt_quiz(user_id: int, quiz_id: int) -> Tuple[bool, str]:
        """Check if user can attempt a quiz
        
        Args:
            user_id: User ID
            quiz_id: Quiz ID
            
        Returns:
            Tuple of (can_attempt, message)
        """
        quiz = QuizV2.query.get(quiz_id)
        if not quiz or not quiz.is_active:
            return False, "Quiz not found or inactive."
        
        # Check if user can access the module
        from .module_service import ModuleService
        if not ModuleService.can_user_access_module(user_id, quiz.module_id):
            return False, "You don't have access to this module."
        
        # Check attempt limit
        attempts = QuizService.get_user_attempts(user_id, quiz_id)
        if len(attempts) >= quiz.max_attempts:
            return False, f"Maximum attempts ({quiz.max_attempts}) reached."
        
        # Check if there's an active attempt
        active_attempt = QuizAttemptV2.query.filter_by(
            user_id=user_id,
            quiz_id=quiz_id,
            status='in_progress'
        ).first()
        
        if active_attempt:
            return False, "You have an active quiz attempt. Please complete or abandon it first."
        
        return True, "You can attempt this quiz."
    
    @staticmethod
    def start_quiz_attempt(user_id: int, quiz_id: int) -> Tuple[bool, str, Optional[Dict]]:
        """Start a new quiz attempt
        
        Args:
            user_id: User ID
            quiz_id: Quiz ID
            
        Returns:
            Tuple of (success, message, attempt_data)
        """
        # Check if user can attempt
        can_attempt, message = QuizService.can_user_attempt_quiz(user_id, quiz_id)
        if not can_attempt:
            return False, message, None
        
        # Create new attempt
        attempt = QuizAttemptV2.create_new_attempt(user_id, quiz_id)
        db.session.commit()
        
        # Get quiz data for the attempt
        quiz_data = QuizService.get_quiz_for_attempt(quiz_id, user_id)
        
        return True, "Quiz attempt started successfully.", {
            'attempt_id': attempt.id,
            'quiz': quiz_data
        }
    
    @staticmethod
    def submit_quiz_attempt(attempt_id: int, answers: Dict[str, str]) -> Tuple[bool, str, Optional[Dict]]:
        """Submit a quiz attempt
        
        Args:
            attempt_id: Quiz attempt ID
            answers: Dictionary with question_id as key and choice_id as value
            
        Returns:
            Tuple of (success, message, result_data)
        """
        attempt = QuizAttemptV2.query.get(attempt_id)
        if not attempt:
            return False, "Quiz attempt not found.", None
        
        if attempt.status != 'in_progress':
            return False, "Quiz attempt is not active.", None
        
        # Complete the attempt
        attempt.complete_attempt(answers)
        
        # Update module progress if quiz passed
        if attempt.passed:
            progress = ProgressService.get_or_create_progress(attempt.user_id, attempt.quiz.module_id)
            progress.record_quiz_attempt(attempt.score)
            
            # Award badge if applicable
            BadgeService.check_and_award_module_badge(attempt.user_id, attempt.quiz.module_id)
        
        # Update quiz analytics
        QuizAnalyticsV2.update_quiz_analytics(attempt.quiz_id)
        
        db.session.commit()
        
        # Prepare result data
        result_data = {
            'attempt': attempt.to_dict(),
            'passed': attempt.passed,
            'score': attempt.score,
            'correct_answers': attempt.correct_answers,
            'total_questions': attempt.total_questions
        }
        
        # Add detailed results if quiz allows showing correct answers
        if attempt.quiz.show_correct_answers:
            result_data['detailed_results'] = QuizService._get_detailed_results(attempt)
        
        return True, "Quiz submitted successfully.", result_data
    
    @staticmethod
    def abandon_quiz_attempt(attempt_id: int) -> Tuple[bool, str]:
        """Abandon an active quiz attempt
        
        Args:
            attempt_id: Quiz attempt ID
            
        Returns:
            Tuple of (success, message)
        """
        attempt = QuizAttemptV2.query.get(attempt_id)
        if not attempt:
            return False, "Quiz attempt not found."
        
        if attempt.status != 'in_progress':
            return False, "Quiz attempt is not active."
        
        attempt.abandon_attempt()
        db.session.commit()
        
        return True, "Quiz attempt abandoned."
    
    @staticmethod
    def get_user_attempts(user_id: int, quiz_id: int) -> List[QuizAttemptV2]:
        """Get all attempts for a user and quiz
        
        Args:
            user_id: User ID
            quiz_id: Quiz ID
            
        Returns:
            List of quiz attempts
        """
        return QuizAttemptV2.get_user_attempts(user_id, quiz_id)
    
    @staticmethod
    def get_user_best_attempt(user_id: int, quiz_id: int) -> Optional[Dict]:
        """Get user's best attempt for a quiz
        
        Args:
            user_id: User ID
            quiz_id: Quiz ID
            
        Returns:
            Best attempt dictionary or None
        """
        attempt = QuizAttemptV2.get_best_attempt(user_id, quiz_id)
        return attempt.to_dict() if attempt else None
    
    @staticmethod
    def get_quiz_analytics(quiz_id: int) -> Optional[Dict]:
        """Get analytics for a quiz
        
        Args:
            quiz_id: Quiz ID
            
        Returns:
            Analytics dictionary or None
        """
        analytics = QuizAnalyticsV2.query.filter_by(quiz_id=quiz_id).first()
        if not analytics:
            # Create analytics if they don't exist
            analytics = QuizAnalyticsV2.update_quiz_analytics(quiz_id)
            db.session.commit()
        
        return analytics.to_dict() if analytics else None
    
    @staticmethod
    def get_active_attempt(user_id: int, quiz_id: int) -> Optional[Dict]:
        """Get user's active attempt for a quiz
        
        Args:
            user_id: User ID
            quiz_id: Quiz ID
            
        Returns:
            Active attempt dictionary or None
        """
        attempt = QuizAttemptV2.query.filter_by(
            user_id=user_id,
            quiz_id=quiz_id,
            status='in_progress'
        ).first()
        
        if not attempt:
            return None
        
        attempt_data = attempt.to_dict()
        
        # Add quiz data
        quiz_data = QuizService.get_quiz_for_attempt(quiz_id, user_id)
        attempt_data['quiz'] = quiz_data
        
        return attempt_data
    
    @staticmethod
    def validate_quiz_answers(quiz_id: int, answers: Dict[str, str]) -> Tuple[bool, str]:
        """Validate quiz answers format
        
        Args:
            quiz_id: Quiz ID
            answers: Dictionary with question_id as key and choice_id as value
            
        Returns:
            Tuple of (valid, message)
        """
        quiz = QuizV2.query.get(quiz_id)
        if not quiz:
            return False, "Quiz not found."
        
        # Check if all questions are answered
        question_ids = {str(q.id) for q in quiz.questions}
        answered_ids = set(answers.keys())
        
        missing_questions = question_ids - answered_ids
        if missing_questions:
            return False, f"Missing answers for questions: {', '.join(missing_questions)}"
        
        # Check if all answers are valid choices
        for question_id, choice_id in answers.items():
            question = QuestionV2.query.get(question_id)
            if not question or question.quiz_id != quiz_id:
                return False, f"Invalid question ID: {question_id}"
            
            choice = ChoiceV2.query.get(choice_id)
            if not choice or choice.question_id != int(question_id):
                return False, f"Invalid choice ID: {choice_id} for question: {question_id}"
        
        return True, "Answers are valid."
    
    @staticmethod
    def get_quiz_summary(quiz_id: int) -> Optional[Dict]:
        """Get a summary of quiz statistics
        
        Args:
            quiz_id: Quiz ID
            
        Returns:
            Quiz summary dictionary or None
        """
        quiz = QuizV2.query.get(quiz_id)
        if not quiz:
            return None
        
        # Get basic quiz info
        summary = quiz.to_dict()
        
        # Get analytics
        analytics = QuizService.get_quiz_analytics(quiz_id)
        if analytics:
            summary['analytics'] = analytics
        
        # Get recent attempts
        recent_attempts = QuizAttemptV2.query.filter_by(
            quiz_id=quiz_id,
            status='completed'
        ).order_by(QuizAttemptV2.completed_at.desc()).limit(10).all()
        
        summary['recent_attempts'] = [attempt.to_dict() for attempt in recent_attempts]
        
        return summary
    
    @staticmethod
    def _get_detailed_results(attempt: QuizAttemptV2) -> List[Dict]:
        """Get detailed results for a quiz attempt
        
        Args:
            attempt: Quiz attempt object
            
        Returns:
            List of detailed question results
        """
        if not attempt.answers:
            return []
        
        results = []
        
        for question in attempt.quiz.questions:
            user_choice_id = attempt.answers.get(str(question.id))
            correct_choice = question.get_correct_choice()
            
            user_choice = None
            if user_choice_id:
                user_choice = ChoiceV2.query.get(user_choice_id)
            
            result = {
                'question': question.to_dict(include_choices=True, include_correct_answer=True),
                'user_choice': user_choice.to_dict() if user_choice else None,
                'correct_choice': correct_choice.to_dict() if correct_choice else None,
                'is_correct': user_choice_id == str(correct_choice.id) if correct_choice else False
            }
            
            results.append(result)
        
        return results
    
    @staticmethod
    def get_user_quiz_history(user_id: int) -> List[Dict]:
        """Get user's complete quiz history
        
        Args:
            user_id: User ID
            
        Returns:
            List of quiz attempt summaries
        """
        attempts = QuizAttemptV2.query.filter_by(
            user_id=user_id,
            status='completed'
        ).order_by(QuizAttemptV2.completed_at.desc()).all()
        
        history = []
        for attempt in attempts:
            attempt_data = attempt.to_dict()
            attempt_data['quiz_title'] = attempt.quiz.title
            attempt_data['module_title'] = attempt.quiz.module.title
            history.append(attempt_data)
        
        return history
    
    @staticmethod
    def reset_quiz_attempts(user_id: int, quiz_id: int) -> Tuple[bool, str]:
        """Reset all quiz attempts for a user (admin function)
        
        Args:
            user_id: User ID
            quiz_id: Quiz ID
            
        Returns:
            Tuple of (success, message)
        """
        attempts = QuizAttemptV2.query.filter_by(
            user_id=user_id,
            quiz_id=quiz_id
        ).all()
        
        if not attempts:
            return False, "No attempts found to reset."
        
        # Delete all attempts
        for attempt in attempts:
            db.session.delete(attempt)
        
        # Reset module progress quiz data
        quiz = QuizV2.query.get(quiz_id)
        if quiz:
            progress = ProgressService.get_module_progress(user_id, quiz.module_id)
            if progress:
                progress.quiz_score = None
                progress.quiz_attempts = 0
                progress.quiz_passed = False
                
                # If module was only completed due to quiz, reset status
                if progress.status == 'completed' and quiz.module.requires_completion:
                    progress.status = 'in_progress'
                    progress.completed_at = None
        
        # Update analytics
        QuizAnalyticsV2.update_quiz_analytics(quiz_id)
        
        db.session.commit()
        
        return True, f"Reset {len(attempts)} quiz attempts."