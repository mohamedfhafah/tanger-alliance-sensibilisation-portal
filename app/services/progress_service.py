"""Progress Service

This service handles all user progress tracking including:
- Module progress management
- Progress calculations
- Completion tracking
- Progress analytics
"""

from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta
from sqlalchemy import func, and_
from app import db
from app.models.module_v2 import ModuleV2, ModuleProgressV2
from app.models.quiz_v2 import QuizAttemptV2


class ProgressService:
    """Service for progress tracking operations"""
    
    @staticmethod
    def get_or_create_progress(user_id: int, module_id: int) -> ModuleProgressV2:
        """Get or create progress record for user and module
        
        Args:
            user_id: User ID
            module_id: Module ID
            
        Returns:
            ModuleProgressV2 object
        """
        progress = ModuleProgressV2.query.filter_by(
            user_id=user_id,
            module_id=module_id
        ).first()
        
        if not progress:
            progress = ModuleProgressV2(
                user_id=user_id,
                module_id=module_id,
                status='not_started',
                progress_percentage=0.0
            )
            db.session.add(progress)
            db.session.flush()  # Get ID without committing
        
        return progress
    
    @staticmethod
    def get_module_progress(user_id: int, module_id: int) -> Optional[ModuleProgressV2]:
        """Get progress record for user and module
        
        Args:
            user_id: User ID
            module_id: Module ID
            
        Returns:
            ModuleProgressV2 object or None
        """
        return ModuleProgressV2.query.filter_by(
            user_id=user_id,
            module_id=module_id
        ).first()
    
    @staticmethod
    def get_user_progress_summary(user_id: int) -> Dict:
        """Get comprehensive progress summary for a user
        
        Args:
            user_id: User ID
            
        Returns:
            Progress summary dictionary
        """
        # Get all modules with progress
        modules_query = db.session.query(
            ModuleV2,
            ModuleProgressV2
        ).outerjoin(
            ModuleProgressV2,
            and_(
                ModuleProgressV2.module_id == ModuleV2.id,
                ModuleProgressV2.user_id == user_id
            )
        ).filter(ModuleV2.is_active == True).order_by(ModuleV2.order)
        
        modules_data = []
        total_modules = 0
        completed_modules = 0
        in_progress_modules = 0
        total_time_spent = timedelta()
        
        for module, progress in modules_query:
            total_modules += 1
            
            module_data = module.to_dict()
            
            if progress:
                module_data['progress'] = progress.to_dict()
                
                if progress.status == 'completed':
                    completed_modules += 1
                elif progress.status == 'in_progress':
                    in_progress_modules += 1
                
                if progress.time_spent:
                    total_time_spent += progress.time_spent
            else:
                module_data['progress'] = {
                    'status': 'not_started',
                    'progress_percentage': 0.0,
                    'time_spent': None,
                    'quiz_score': None,
                    'quiz_attempts': 0,
                    'quiz_passed': False
                }
            
            modules_data.append(module_data)
        
        # Calculate overall statistics
        overall_progress = (completed_modules / total_modules * 100) if total_modules > 0 else 0
        
        return {
            'modules': modules_data,
            'statistics': {
                'total_modules': total_modules,
                'completed_modules': completed_modules,
                'in_progress_modules': in_progress_modules,
                'not_started_modules': total_modules - completed_modules - in_progress_modules,
                'overall_progress_percentage': round(overall_progress, 2),
                'total_time_spent_minutes': int(total_time_spent.total_seconds() / 60),
                'average_time_per_module': int(total_time_spent.total_seconds() / 60 / max(completed_modules, 1))
            }
        }
    
    @staticmethod
    def start_module(user_id: int, module_id: int) -> Tuple[bool, str]:
        """Start a module for a user
        
        Args:
            user_id: User ID
            module_id: Module ID
            
        Returns:
            Tuple of (success, message)
        """
        # Check if user can access module
        from .module_service import ModuleService
        if not ModuleService.can_user_access_module(user_id, module_id):
            return False, "You don't have access to this module."
        
        progress = ProgressService.get_or_create_progress(user_id, module_id)
        
        if progress.status == 'completed':
            return False, "Module is already completed."
        
        if progress.status == 'not_started':
            progress.status = 'in_progress'
            progress.started_at = datetime.utcnow()
            db.session.commit()
        
        return True, "Module started successfully."
    
    @staticmethod
    def update_progress_percentage(user_id: int, module_id: int, percentage: float) -> Tuple[bool, str]:
        """Update progress percentage for a module
        
        Args:
            user_id: User ID
            module_id: Module ID
            percentage: Progress percentage (0-100)
            
        Returns:
            Tuple of (success, message)
        """
        if not 0 <= percentage <= 100:
            return False, "Progress percentage must be between 0 and 100."
        
        progress = ProgressService.get_or_create_progress(user_id, module_id)
        
        # Start module if not started
        if progress.status == 'not_started':
            progress.status = 'in_progress'
            progress.started_at = datetime.utcnow()
        
        progress.progress_percentage = percentage
        progress.last_accessed_at = datetime.utcnow()
        
        # Auto-complete if 100% and no quiz required
        module = ModuleV2.query.get(module_id)
        if percentage >= 100 and module and not module.has_quiz:
            progress.status = 'completed'
            progress.completed_at = datetime.utcnow()
        
        db.session.commit()
        
        return True, "Progress updated successfully."
    
    @staticmethod
    def complete_module(user_id: int, module_id: int) -> Tuple[bool, str]:
        """Mark a module as completed
        
        Args:
            user_id: User ID
            module_id: Module ID
            
        Returns:
            Tuple of (success, message)
        """
        progress = ProgressService.get_or_create_progress(user_id, module_id)
        module = ModuleV2.query.get(module_id)
        
        if not module:
            return False, "Module not found."
        
        # Check if module can be completed
        if module.has_quiz and not progress.quiz_passed:
            return False, "You must pass the quiz to complete this module."
        
        if progress.status == 'completed':
            return False, "Module is already completed."
        
        # Complete the module
        progress.status = 'completed'
        progress.progress_percentage = 100.0
        progress.completed_at = datetime.utcnow()
        
        if not progress.started_at:
            progress.started_at = datetime.utcnow()
        
        db.session.commit()
        
        return True, "Module completed successfully."
    
    @staticmethod
    def record_time_spent(user_id: int, module_id: int, minutes: int) -> Tuple[bool, str]:
        """Record time spent on a module
        
        Args:
            user_id: User ID
            module_id: Module ID
            minutes: Time spent in minutes
            
        Returns:
            Tuple of (success, message)
        """
        if minutes < 0:
            return False, "Time spent cannot be negative."
        
        progress = ProgressService.get_or_create_progress(user_id, module_id)
        
        # Start module if not started
        if progress.status == 'not_started':
            progress.status = 'in_progress'
            progress.started_at = datetime.utcnow()
        
        # Add time to existing time
        if progress.time_spent:
            progress.time_spent += timedelta(minutes=minutes)
        else:
            progress.time_spent = timedelta(minutes=minutes)
        
        progress.last_accessed_at = datetime.utcnow()
        
        db.session.commit()
        
        return True, "Time recorded successfully."
    
    @staticmethod
    def reset_module_progress(user_id: int, module_id: int) -> Tuple[bool, str]:
        """Reset progress for a module
        
        Args:
            user_id: User ID
            module_id: Module ID
            
        Returns:
            Tuple of (success, message)
        """
        progress = ProgressService.get_module_progress(user_id, module_id)
        
        if not progress:
            return False, "No progress found to reset."
        
        # Reset all progress data
        progress.status = 'not_started'
        progress.progress_percentage = 0.0
        progress.started_at = None
        progress.completed_at = None
        progress.last_accessed_at = None
        progress.time_spent = None
        progress.quiz_score = None
        progress.quiz_attempts = 0
        progress.quiz_passed = False
        
        db.session.commit()
        
        return True, "Module progress reset successfully."
    
    @staticmethod
    def get_module_analytics(module_id: int) -> Dict:
        """Get analytics for a specific module
        
        Args:
            module_id: Module ID
            
        Returns:
            Analytics dictionary
        """
        # Get basic statistics
        total_users = ModuleProgressV2.query.filter_by(module_id=module_id).count()
        completed_users = ModuleProgressV2.query.filter_by(
            module_id=module_id,
            status='completed'
        ).count()
        in_progress_users = ModuleProgressV2.query.filter_by(
            module_id=module_id,
            status='in_progress'
        ).count()
        
        # Calculate completion rate
        completion_rate = (completed_users / total_users * 100) if total_users > 0 else 0
        
        # Get average time spent
        avg_time_query = db.session.query(
            func.avg(func.extract('epoch', ModuleProgressV2.time_spent) / 60)
        ).filter(
            ModuleProgressV2.module_id == module_id,
            ModuleProgressV2.time_spent.isnot(None)
        ).scalar()
        
        avg_time_minutes = int(avg_time_query) if avg_time_query else 0
        
        # Get average progress percentage
        avg_progress = db.session.query(
            func.avg(ModuleProgressV2.progress_percentage)
        ).filter(ModuleProgressV2.module_id == module_id).scalar()
        
        avg_progress = round(avg_progress, 2) if avg_progress else 0
        
        # Get quiz statistics if module has quiz
        quiz_stats = None
        module = ModuleV2.query.get(module_id)
        if module and module.has_quiz:
            quiz_attempts = QuizAttemptV2.query.join(
                QuizAttemptV2.quiz
            ).filter(
                QuizAttemptV2.quiz.has(module_id=module_id),
                QuizAttemptV2.status == 'completed'
            ).count()
            
            passed_attempts = QuizAttemptV2.query.join(
                QuizAttemptV2.quiz
            ).filter(
                QuizAttemptV2.quiz.has(module_id=module_id),
                QuizAttemptV2.status == 'completed',
                QuizAttemptV2.passed == True
            ).count()
            
            avg_score = db.session.query(
                func.avg(QuizAttemptV2.score)
            ).join(
                QuizAttemptV2.quiz
            ).filter(
                QuizAttemptV2.quiz.has(module_id=module_id),
                QuizAttemptV2.status == 'completed'
            ).scalar()
            
            quiz_stats = {
                'total_attempts': quiz_attempts,
                'passed_attempts': passed_attempts,
                'pass_rate': (passed_attempts / quiz_attempts * 100) if quiz_attempts > 0 else 0,
                'average_score': round(avg_score, 2) if avg_score else 0
            }
        
        return {
            'module_id': module_id,
            'total_users': total_users,
            'completed_users': completed_users,
            'in_progress_users': in_progress_users,
            'not_started_users': total_users - completed_users - in_progress_users,
            'completion_rate': round(completion_rate, 2),
            'average_time_minutes': avg_time_minutes,
            'average_progress_percentage': avg_progress,
            'quiz_statistics': quiz_stats
        }
    
    @staticmethod
    def get_user_recent_activity(user_id: int, days: int = 7) -> List[Dict]:
        """Get user's recent module activity
        
        Args:
            user_id: User ID
            days: Number of days to look back
            
        Returns:
            List of recent activity records
        """
        since_date = datetime.utcnow() - timedelta(days=days)
        
        # Get recent progress updates
        recent_progress = ModuleProgressV2.query.filter(
            ModuleProgressV2.user_id == user_id,
            ModuleProgressV2.last_accessed_at >= since_date
        ).order_by(ModuleProgressV2.last_accessed_at.desc()).all()
        
        # Get recent quiz attempts
        recent_attempts = QuizAttemptV2.query.filter(
            QuizAttemptV2.user_id == user_id,
            QuizAttemptV2.started_at >= since_date
        ).order_by(QuizAttemptV2.started_at.desc()).all()
        
        activity = []
        
        # Add progress activities
        for progress in recent_progress:
            activity.append({
                'type': 'module_progress',
                'timestamp': progress.last_accessed_at,
                'module_id': progress.module_id,
                'module_title': progress.module.title,
                'details': {
                    'status': progress.status,
                    'progress_percentage': progress.progress_percentage
                }
            })
        
        # Add quiz activities
        for attempt in recent_attempts:
            activity.append({
                'type': 'quiz_attempt',
                'timestamp': attempt.started_at,
                'module_id': attempt.quiz.module_id,
                'module_title': attempt.quiz.module.title,
                'details': {
                    'quiz_title': attempt.quiz.title,
                    'status': attempt.status,
                    'score': attempt.score,
                    'passed': attempt.passed
                }
            })
        
        # Sort by timestamp and return
        activity.sort(key=lambda x: x['timestamp'], reverse=True)
        
        return activity
    
    @staticmethod
    def get_learning_path_progress(user_id: int) -> Dict:
        """Get user's progress through the learning path
        
        Args:
            user_id: User ID
            
        Returns:
            Learning path progress dictionary
        """
        # Get all modules in order
        modules = ModuleV2.query.filter_by(is_active=True).order_by(ModuleV2.order).all()
        
        path_progress = []
        current_module = None
        next_module = None
        
        for i, module in enumerate(modules):
            progress = ProgressService.get_module_progress(user_id, module.id)
            
            module_data = {
                'module': module.to_dict(),
                'progress': progress.to_dict() if progress else None,
                'is_accessible': False,
                'is_current': False,
                'is_next': False
            }
            
            # Check accessibility
            from .module_service import ModuleService
            module_data['is_accessible'] = ModuleService.can_user_access_module(user_id, module.id)
            
            # Determine current and next modules
            if progress:
                if progress.status == 'in_progress' and not current_module:
                    current_module = module_data
                    module_data['is_current'] = True
                elif progress.status == 'not_started' and not next_module and module_data['is_accessible']:
                    next_module = module_data
                    module_data['is_next'] = True
            elif module_data['is_accessible'] and not next_module:
                next_module = module_data
                module_data['is_next'] = True
            
            path_progress.append(module_data)
        
        # If no current module, find the first accessible incomplete module
        if not current_module:
            for module_data in path_progress:
                if (module_data['is_accessible'] and 
                    (not module_data['progress'] or module_data['progress']['status'] != 'completed')):
                    current_module = module_data
                    module_data['is_current'] = True
                    break
        
        return {
            'path': path_progress,
            'current_module': current_module,
            'next_module': next_module,
            'total_modules': len(modules),
            'completed_modules': len([m for m in path_progress if m['progress'] and m['progress']['status'] == 'completed'])
        }
    
    @staticmethod
    def bulk_update_progress(updates: List[Dict]) -> Tuple[bool, str, List[str]]:
        """Bulk update progress for multiple users/modules
        
        Args:
            updates: List of update dictionaries with user_id, module_id, and update data
            
        Returns:
            Tuple of (success, message, error_list)
        """
        errors = []
        updated_count = 0
        
        try:
            for update in updates:
                user_id = update.get('user_id')
                module_id = update.get('module_id')
                
                if not user_id or not module_id:
                    errors.append(f"Missing user_id or module_id in update: {update}")
                    continue
                
                progress = ProgressService.get_or_create_progress(user_id, module_id)
                
                # Update fields if provided
                if 'status' in update:
                    progress.status = update['status']
                
                if 'progress_percentage' in update:
                    progress.progress_percentage = update['progress_percentage']
                
                if 'time_spent_minutes' in update:
                    progress.time_spent = timedelta(minutes=update['time_spent_minutes'])
                
                if 'quiz_score' in update:
                    progress.quiz_score = update['quiz_score']
                
                if 'quiz_passed' in update:
                    progress.quiz_passed = update['quiz_passed']
                
                progress.last_accessed_at = datetime.utcnow()
                updated_count += 1
            
            db.session.commit()
            
            return True, f"Successfully updated {updated_count} progress records.", errors
            
        except Exception as e:
            db.session.rollback()
            return False, f"Bulk update failed: {str(e)}", errors