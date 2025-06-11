"""Service Layer Package

This package contains the business logic services for the application.
Services handle complex operations and coordinate between models and routes.

Services included:
- ModuleService: Module management and progress tracking
- QuizService: Quiz operations and scoring
- ProgressService: User progress tracking
- BadgeService: Badge management and awarding
- ContentService: Content management and delivery
"""

from .module_service import ModuleService
from .quiz_service import QuizService
from .progress_service import ProgressService
from .badge_service import BadgeService
from .content_service import ContentService

__all__ = [
    'ModuleService',
    'QuizService', 
    'ProgressService',
    'BadgeService',
    'ContentService'
]