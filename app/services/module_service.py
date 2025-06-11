"""Module Service

This service handles all module-related business logic including:
- Module retrieval and management
- Progress tracking
- Prerequisite checking
- Module completion logic
"""

from typing import List, Dict, Optional, Tuple
from datetime import datetime
from app import db
from app.models.module_v2 import ModuleV2, ModuleProgressV2, ModulePrerequisite
from app.models.quiz_v2 import QuizV2
from app.models.user import User
from .progress_service import ProgressService
from .badge_service import BadgeService


class ModuleService:
    """Service for module operations"""
    
    @staticmethod
    def get_all_modules(user_id: Optional[int] = None) -> List[Dict]:
        """Get all active modules with optional user progress
        
        Args:
            user_id: Optional user ID to include progress data
            
        Returns:
            List of module dictionaries with progress data
        """
        modules = ModuleV2.get_active_modules()
        result = []
        
        for module in modules:
            module_data = module.to_dict()
            
            if user_id:
                progress = ProgressService.get_module_progress(user_id, module.id)
                module_data['progress'] = progress.to_dict() if progress else None
                module_data['can_access'] = ModuleService.can_user_access_module(user_id, module.id)
            
            result.append(module_data)
        
        return result
    
    @staticmethod
    def get_module_with_progress(module_id: int, user_id: int) -> Optional[Dict]:
        """Get a specific module with user progress data
        
        Args:
            module_id: Module ID
            user_id: User ID
            
        Returns:
            Module dictionary with progress data or None if not found
        """
        module = ModuleV2.query.filter_by(id=module_id, is_active=True).first()
        if not module:
            return None
        
        # Check if user can access this module
        if not ModuleService.can_user_access_module(user_id, module_id):
            return None
        
        module_data = module.to_dict()
        
        # Add progress data
        progress = ProgressService.get_module_progress(user_id, module_id)
        module_data['progress'] = progress.to_dict() if progress else None
        
        # Add quiz data if exists
        if module.quiz:
            module_data['quiz'] = module.quiz.to_dict()
            
            # Add user's quiz attempts
            from .quiz_service import QuizService
            attempts = QuizService.get_user_attempts(user_id, module.quiz.id)
            module_data['quiz_attempts'] = [attempt.to_dict() for attempt in attempts]
        
        # Add content sections
        from .content_service import ContentService
        content = ContentService.get_module_content(module_id)
        module_data['content'] = content
        
        # Add prerequisite information
        prerequisites = ModuleService.get_module_prerequisites(module_id)
        module_data['prerequisites'] = prerequisites
        
        return module_data
    
    @staticmethod
    def can_user_access_module(user_id: int, module_id: int) -> bool:
        """Check if user can access a module based on prerequisites
        
        Args:
            user_id: User ID
            module_id: Module ID
            
        Returns:
            True if user can access the module, False otherwise
        """
        module = ModuleV2.query.get(module_id)
        if not module or not module.is_active:
            return False
        
        # Check prerequisites
        prerequisites = module.get_prerequisites()
        
        for prereq_id in prerequisites:
            prereq_progress = ProgressService.get_module_progress(user_id, prereq_id)
            if not prereq_progress or prereq_progress.status != 'completed':
                return False
        
        return True
    
    @staticmethod
    def get_module_prerequisites(module_id: int) -> List[Dict]:
        """Get prerequisite modules for a module
        
        Args:
            module_id: Module ID
            
        Returns:
            List of prerequisite module dictionaries
        """
        module = ModuleV2.query.get(module_id)
        if not module:
            return []
        
        prerequisite_ids = module.get_prerequisites()
        prerequisites = ModuleV2.query.filter(ModuleV2.id.in_(prerequisite_ids)).all()
        
        return [prereq.to_dict() for prereq in prerequisites]
    
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
        if not ModuleService.can_user_access_module(user_id, module_id):
            return False, "You don't have access to this module. Please complete the prerequisites first."
        
        # Get or create progress record
        progress = ProgressService.get_or_create_progress(user_id, module_id)
        
        # Start the module if not already started
        if progress.status == 'not_started':
            progress.start_module()
            db.session.commit()
            return True, "Module started successfully."
        
        return True, "Module already started."
    
    @staticmethod
    def update_module_progress(user_id: int, module_id: int, percentage: int) -> Tuple[bool, str]:
        """Update user's progress in a module
        
        Args:
            user_id: User ID
            module_id: Module ID
            percentage: Progress percentage (0-100)
            
        Returns:
            Tuple of (success, message)
        """
        if not (0 <= percentage <= 100):
            return False, "Invalid progress percentage. Must be between 0 and 100."
        
        progress = ProgressService.get_or_create_progress(user_id, module_id)
        progress.update_progress(percentage)
        
        # If progress is 100% and module doesn't require quiz, complete it
        if percentage == 100:
            module = ModuleV2.query.get(module_id)
            if module and not module.quiz:
                ModuleService.complete_module(user_id, module_id)
        
        db.session.commit()
        return True, "Progress updated successfully."
    
    @staticmethod
    def complete_module(user_id: int, module_id: int, quiz_score: Optional[int] = None) -> Tuple[bool, str]:
        """Complete a module for a user
        
        Args:
            user_id: User ID
            module_id: Module ID
            quiz_score: Optional quiz score if module has a quiz
            
        Returns:
            Tuple of (success, message)
        """
        progress = ProgressService.get_or_create_progress(user_id, module_id)
        progress.complete_module(quiz_score)
        
        # Award badge if applicable
        BadgeService.check_and_award_module_badge(user_id, module_id)
        
        db.session.commit()
        return True, "Module completed successfully."
    
    @staticmethod
    def get_user_module_stats(user_id: int) -> Dict:
        """Get user's overall module statistics
        
        Args:
            user_id: User ID
            
        Returns:
            Dictionary with user's module statistics
        """
        return ModuleProgressV2.get_user_module_stats(user_id)
    
    @staticmethod
    def get_next_available_module(user_id: int) -> Optional[Dict]:
        """Get the next module the user can access
        
        Args:
            user_id: User ID
            
        Returns:
            Next available module dictionary or None
        """
        modules = ModuleV2.get_active_modules()
        
        for module in modules:
            progress = ProgressService.get_module_progress(user_id, module.id)
            
            # If module not started and user can access it
            if (not progress or progress.status == 'not_started') and \
               ModuleService.can_user_access_module(user_id, module.id):
                return module.to_dict()
        
        return None
    
    @staticmethod
    def get_module_completion_rate() -> float:
        """Get overall module completion rate across all users
        
        Returns:
            Completion rate as percentage
        """
        total_progress_records = ModuleProgressV2.query.count()
        completed_records = ModuleProgressV2.query.filter_by(status='completed').count()
        
        if total_progress_records == 0:
            return 0.0
        
        return (completed_records / total_progress_records) * 100
    
    @staticmethod
    def search_modules(query: str, user_id: Optional[int] = None) -> List[Dict]:
        """Search modules by title or description
        
        Args:
            query: Search query
            user_id: Optional user ID to include progress data
            
        Returns:
            List of matching module dictionaries
        """
        modules = ModuleV2.query.filter(
            ModuleV2.is_active == True,
            db.or_(
                ModuleV2.title.ilike(f'%{query}%'),
                ModuleV2.description.ilike(f'%{query}%')
            )
        ).order_by(ModuleV2.order).all()
        
        result = []
        for module in modules:
            module_data = module.to_dict()
            
            if user_id:
                progress = ProgressService.get_module_progress(user_id, module.id)
                module_data['progress'] = progress.to_dict() if progress else None
                module_data['can_access'] = ModuleService.can_user_access_module(user_id, module.id)
            
            result.append(module_data)
        
        return result
    
    @staticmethod
    def get_modules_by_status(user_id: int, status: str) -> List[Dict]:
        """Get modules filtered by user's progress status
        
        Args:
            user_id: User ID
            status: Progress status ('not_started', 'in_progress', 'completed')
            
        Returns:
            List of module dictionaries
        """
        if status == 'not_started':
            # Get modules with no progress record or not_started status
            all_modules = ModuleV2.get_active_modules()
            result = []
            
            for module in all_modules:
                progress = ProgressService.get_module_progress(user_id, module.id)
                if not progress or progress.status == 'not_started':
                    module_data = module.to_dict()
                    module_data['progress'] = progress.to_dict() if progress else None
                    module_data['can_access'] = ModuleService.can_user_access_module(user_id, module.id)
                    result.append(module_data)
            
            return result
        else:
            # Get modules with specific status
            progress_records = ModuleProgressV2.query.filter_by(
                user_id=user_id,
                status=status
            ).all()
            
            module_ids = [p.module_id for p in progress_records]
            modules = ModuleV2.query.filter(
                ModuleV2.id.in_(module_ids),
                ModuleV2.is_active == True
            ).order_by(ModuleV2.order).all()
            
            result = []
            for module in modules:
                module_data = module.to_dict()
                progress = next((p for p in progress_records if p.module_id == module.id), None)
                module_data['progress'] = progress.to_dict() if progress else None
                module_data['can_access'] = True  # User already has progress, so they can access
                result.append(module_data)
            
            return result
    
    @staticmethod
    def add_prerequisite(module_id: int, prerequisite_id: int) -> Tuple[bool, str]:
        """Add a prerequisite to a module
        
        Args:
            module_id: Module ID
            prerequisite_id: Prerequisite module ID
            
        Returns:
            Tuple of (success, message)
        """
        # Validate modules exist
        module = ModuleV2.query.get(module_id)
        prerequisite = ModuleV2.query.get(prerequisite_id)
        
        if not module or not prerequisite:
            return False, "One or both modules not found."
        
        # Check for self-reference
        if module_id == prerequisite_id:
            return False, "A module cannot be its own prerequisite."
        
        # Check if prerequisite already exists
        existing = ModulePrerequisite.query.filter_by(
            module_id=module_id,
            prerequisite_id=prerequisite_id
        ).first()
        
        if existing:
            return False, "Prerequisite already exists."
        
        # Check for circular dependencies
        if ModuleService._would_create_circular_dependency(module_id, prerequisite_id):
            return False, "Adding this prerequisite would create a circular dependency."
        
        # Add prerequisite
        prereq = ModulePrerequisite(
            module_id=module_id,
            prerequisite_id=prerequisite_id
        )
        db.session.add(prereq)
        db.session.commit()
        
        return True, "Prerequisite added successfully."
    
    @staticmethod
    def remove_prerequisite(module_id: int, prerequisite_id: int) -> Tuple[bool, str]:
        """Remove a prerequisite from a module
        
        Args:
            module_id: Module ID
            prerequisite_id: Prerequisite module ID
            
        Returns:
            Tuple of (success, message)
        """
        prerequisite = ModulePrerequisite.query.filter_by(
            module_id=module_id,
            prerequisite_id=prerequisite_id
        ).first()
        
        if not prerequisite:
            return False, "Prerequisite not found."
        
        db.session.delete(prerequisite)
        db.session.commit()
        
        return True, "Prerequisite removed successfully."
    
    @staticmethod
    def _would_create_circular_dependency(module_id: int, prerequisite_id: int) -> bool:
        """Check if adding a prerequisite would create a circular dependency
        
        Args:
            module_id: Module ID
            prerequisite_id: Prerequisite module ID
            
        Returns:
            True if circular dependency would be created
        """
        # Use depth-first search to check for cycles
        visited = set()
        
        def has_path(start: int, target: int) -> bool:
            if start == target:
                return True
            
            if start in visited:
                return False
            
            visited.add(start)
            
            # Get all modules that have 'start' as a prerequisite
            dependent_modules = ModulePrerequisite.query.filter_by(
                prerequisite_id=start
            ).all()
            
            for dep in dependent_modules:
                if has_path(dep.module_id, target):
                    return True
            
            return False
        
        # Check if prerequisite_id has a path to module_id
        return has_path(prerequisite_id, module_id)