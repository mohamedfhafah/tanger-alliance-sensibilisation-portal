"""Badge Service

This service handles all badge-related operations including:
- Badge awarding logic
- Badge validation
- Achievement tracking
- Badge analytics
"""

from typing import List, Dict, Optional, Tuple
from datetime import datetime
from sqlalchemy import func
from app import db
from app.models.module import Badge, User  # Using existing badge model
from app.models.module_v2 import ModuleV2, ModuleProgressV2
from app.models.quiz_v2 import QuizAttemptV2


class BadgeService:
    """Service for badge operations"""
    
    @staticmethod
    def check_and_award_module_badge(user_id: int, module_id: int) -> Tuple[bool, Optional[Dict]]:
        """Check if user should receive a badge for completing a module
        
        Args:
            user_id: User ID
            module_id: Module ID
            
        Returns:
            Tuple of (badge_awarded, badge_data)
        """
        # Check if module is completed
        progress = ModuleProgressV2.query.filter_by(
            user_id=user_id,
            module_id=module_id,
            status='completed'
        ).first()
        
        if not progress:
            return False, None
        
        # Get module information
        module = ModuleV2.query.get(module_id)
        if not module:
            return False, None
        
        # Check if badge already exists for this module
        existing_badge = Badge.query.filter_by(
            user_id=user_id,
            module_id=module_id
        ).first()
        
        if existing_badge:
            return False, None
        
        # Determine badge type based on performance
        badge_type = BadgeService._determine_badge_type(user_id, module_id, progress)
        
        # Create badge
        badge = Badge(
            user_id=user_id,
            module_id=module_id,
            badge_type=badge_type,
            earned_at=datetime.utcnow(),
            description=f"Completed {module.title}"
        )
        
        db.session.add(badge)
        db.session.commit()
        
        return True, badge.to_dict() if hasattr(badge, 'to_dict') else {
            'id': badge.id,
            'badge_type': badge.badge_type,
            'module_title': module.title,
            'earned_at': badge.earned_at.isoformat(),
            'description': badge.description
        }
    
    @staticmethod
    def _determine_badge_type(user_id: int, module_id: int, progress: ModuleProgressV2) -> str:
        """Determine the type of badge to award based on performance
        
        Args:
            user_id: User ID
            module_id: Module ID
            progress: Module progress object
            
        Returns:
            Badge type string
        """
        # Default badge type
        badge_type = 'completion'
        
        # Check for excellence criteria
        module = ModuleV2.query.get(module_id)
        
        # If module has quiz, check quiz performance
        if module and module.has_quiz and progress.quiz_passed:
            if progress.quiz_score and progress.quiz_score >= 95:
                badge_type = 'excellence'
            elif progress.quiz_score and progress.quiz_score >= 85:
                badge_type = 'proficiency'
            elif progress.quiz_attempts == 1:
                badge_type = 'first_try'
        
        # Check for speed completion
        if progress.time_spent and module.estimated_duration:
            time_ratio = progress.time_spent.total_seconds() / (module.estimated_duration * 60)
            if time_ratio <= 0.75:  # Completed in 75% or less of estimated time
                if badge_type == 'excellence':
                    badge_type = 'mastery'  # Excellence + Speed = Mastery
                elif badge_type == 'completion':
                    badge_type = 'efficiency'
        
        return badge_type
    
    @staticmethod
    def get_user_badges(user_id: int) -> List[Dict]:
        """Get all badges for a user
        
        Args:
            user_id: User ID
            
        Returns:
            List of badge dictionaries
        """
        badges = Badge.query.filter_by(user_id=user_id).order_by(Badge.earned_at.desc()).all()
        
        badge_list = []
        for badge in badges:
            badge_data = {
                'id': badge.id,
                'badge_type': badge.badge_type,
                'earned_at': badge.earned_at.isoformat(),
                'description': badge.description
            }
            
            # Add module information if available
            if badge.module_id:
                module = ModuleV2.query.get(badge.module_id)
                if module:
                    badge_data['module'] = {
                        'id': module.id,
                        'title': module.title,
                        'category': module.category
                    }
            
            badge_list.append(badge_data)
        
        return badge_list
    
    @staticmethod
    def get_badge_statistics(user_id: int) -> Dict:
        """Get badge statistics for a user
        
        Args:
            user_id: User ID
            
        Returns:
            Badge statistics dictionary
        """
        # Count badges by type
        badge_counts = db.session.query(
            Badge.badge_type,
            func.count(Badge.id)
        ).filter_by(user_id=user_id).group_by(Badge.badge_type).all()
        
        badge_stats = {badge_type: count for badge_type, count in badge_counts}
        
        # Get total badges
        total_badges = sum(badge_stats.values())
        
        # Get recent badges (last 30 days)
        recent_date = datetime.utcnow().replace(day=1)  # Start of current month
        recent_badges = Badge.query.filter(
            Badge.user_id == user_id,
            Badge.earned_at >= recent_date
        ).count()
        
        # Calculate badge score (weighted by badge type)
        badge_weights = {
            'completion': 1,
            'proficiency': 2,
            'excellence': 3,
            'first_try': 2,
            'efficiency': 2,
            'mastery': 5
        }
        
        badge_score = sum(
            badge_stats.get(badge_type, 0) * weight
            for badge_type, weight in badge_weights.items()
        )
        
        return {
            'total_badges': total_badges,
            'badge_counts': badge_stats,
            'recent_badges': recent_badges,
            'badge_score': badge_score,
            'badge_types': {
                'completion': badge_stats.get('completion', 0),
                'proficiency': badge_stats.get('proficiency', 0),
                'excellence': badge_stats.get('excellence', 0),
                'first_try': badge_stats.get('first_try', 0),
                'efficiency': badge_stats.get('efficiency', 0),
                'mastery': badge_stats.get('mastery', 0)
            }
        }
    
    @staticmethod
    def check_special_achievements(user_id: int) -> List[Dict]:
        """Check for special achievements that span multiple modules
        
        Args:
            user_id: User ID
            
        Returns:
            List of special achievement dictionaries
        """
        achievements = []
        
        # Get user's completed modules
        completed_modules = ModuleProgressV2.query.filter_by(
            user_id=user_id,
            status='completed'
        ).count()
        
        # Get user's badges
        user_badges = Badge.query.filter_by(user_id=user_id).all()
        badge_counts = {}
        for badge in user_badges:
            badge_counts[badge.badge_type] = badge_counts.get(badge.badge_type, 0) + 1
        
        # Check for milestone achievements
        milestones = [
            (5, 'First Steps', 'Completed 5 modules'),
            (10, 'Getting Started', 'Completed 10 modules'),
            (25, 'Dedicated Learner', 'Completed 25 modules'),
            (50, 'Expert', 'Completed 50 modules'),
            (100, 'Master', 'Completed 100 modules')
        ]
        
        for milestone_count, title, description in milestones:
            if completed_modules >= milestone_count:
                # Check if achievement already exists
                existing = Badge.query.filter_by(
                    user_id=user_id,
                    badge_type='milestone',
                    description=description
                ).first()
                
                if not existing:
                    achievements.append({
                        'type': 'milestone',
                        'title': title,
                        'description': description,
                        'criteria_met': True
                    })
        
        # Check for excellence achievements
        excellence_count = badge_counts.get('excellence', 0)
        if excellence_count >= 5:
            existing = Badge.query.filter_by(
                user_id=user_id,
                badge_type='excellence_streak',
                description='Earned 5 excellence badges'
            ).first()
            
            if not existing:
                achievements.append({
                    'type': 'excellence_streak',
                    'title': 'Excellence Streak',
                    'description': 'Earned 5 excellence badges',
                    'criteria_met': True
                })
        
        # Check for perfect score achievements
        perfect_scores = QuizAttemptV2.query.filter_by(
            user_id=user_id,
            score=100,
            status='completed'
        ).count()
        
        if perfect_scores >= 3:
            existing = Badge.query.filter_by(
                user_id=user_id,
                badge_type='perfectionist',
                description='Achieved 3 perfect quiz scores'
            ).first()
            
            if not existing:
                achievements.append({
                    'type': 'perfectionist',
                    'title': 'Perfectionist',
                    'description': 'Achieved 3 perfect quiz scores',
                    'criteria_met': True
                })
        
        return achievements
    
    @staticmethod
    def award_special_achievement(user_id: int, achievement: Dict) -> Tuple[bool, str]:
        """Award a special achievement badge
        
        Args:
            user_id: User ID
            achievement: Achievement dictionary
            
        Returns:
            Tuple of (success, message)
        """
        # Check if badge already exists
        existing = Badge.query.filter_by(
            user_id=user_id,
            badge_type=achievement['type'],
            description=achievement['description']
        ).first()
        
        if existing:
            return False, "Achievement already awarded."
        
        # Create badge
        badge = Badge(
            user_id=user_id,
            module_id=None,  # Special achievements are not tied to specific modules
            badge_type=achievement['type'],
            earned_at=datetime.utcnow(),
            description=achievement['description']
        )
        
        db.session.add(badge)
        db.session.commit()
        
        return True, f"Achievement '{achievement['title']}' awarded successfully."
    
    @staticmethod
    def get_leaderboard(limit: int = 10) -> List[Dict]:
        """Get badge leaderboard
        
        Args:
            limit: Number of top users to return
            
        Returns:
            List of leaderboard entries
        """
        # Calculate badge scores for all users
        badge_weights = {
            'completion': 1,
            'proficiency': 2,
            'excellence': 3,
            'first_try': 2,
            'efficiency': 2,
            'mastery': 5,
            'milestone': 10,
            'excellence_streak': 15,
            'perfectionist': 20
        }
        
        # Get user badge counts and calculate scores
        user_scores = db.session.query(
            Badge.user_id,
            Badge.badge_type,
            func.count(Badge.id)
        ).group_by(Badge.user_id, Badge.badge_type).all()
        
        # Calculate total scores per user
        user_totals = {}
        user_badge_counts = {}
        
        for user_id, badge_type, count in user_scores:
            if user_id not in user_totals:
                user_totals[user_id] = 0
                user_badge_counts[user_id] = {}
            
            weight = badge_weights.get(badge_type, 1)
            user_totals[user_id] += count * weight
            user_badge_counts[user_id][badge_type] = count
        
        # Sort by score and get top users
        sorted_users = sorted(user_totals.items(), key=lambda x: x[1], reverse=True)[:limit]
        
        leaderboard = []
        for rank, (user_id, score) in enumerate(sorted_users, 1):
            user = User.query.get(user_id)
            if user:
                total_badges = sum(user_badge_counts[user_id].values())
                
                leaderboard.append({
                    'rank': rank,
                    'user_id': user_id,
                    'username': user.username,
                    'total_score': score,
                    'total_badges': total_badges,
                    'badge_counts': user_badge_counts[user_id]
                })
        
        return leaderboard
    
    @staticmethod
    def get_badge_progress(user_id: int) -> Dict:
        """Get user's progress towards next badges
        
        Args:
            user_id: User ID
            
        Returns:
            Badge progress dictionary
        """
        # Get current statistics
        completed_modules = ModuleProgressV2.query.filter_by(
            user_id=user_id,
            status='completed'
        ).count()
        
        user_badges = Badge.query.filter_by(user_id=user_id).all()
        badge_counts = {}
        for badge in user_badges:
            badge_counts[badge.badge_type] = badge_counts.get(badge.badge_type, 0) + 1
        
        perfect_scores = QuizAttemptV2.query.filter_by(
            user_id=user_id,
            score=100,
            status='completed'
        ).count()
        
        # Calculate progress towards next milestones
        progress = {
            'next_milestones': [],
            'next_achievements': []
        }
        
        # Module completion milestones
        milestones = [5, 10, 25, 50, 100]
        for milestone in milestones:
            if completed_modules < milestone:
                progress['next_milestones'].append({
                    'type': 'module_completion',
                    'target': milestone,
                    'current': completed_modules,
                    'remaining': milestone - completed_modules,
                    'percentage': (completed_modules / milestone) * 100
                })
                break
        
        # Excellence streak
        excellence_count = badge_counts.get('excellence', 0)
        if excellence_count < 5:
            progress['next_achievements'].append({
                'type': 'excellence_streak',
                'target': 5,
                'current': excellence_count,
                'remaining': 5 - excellence_count,
                'percentage': (excellence_count / 5) * 100
            })
        
        # Perfectionist
        if perfect_scores < 3:
            progress['next_achievements'].append({
                'type': 'perfectionist',
                'target': 3,
                'current': perfect_scores,
                'remaining': 3 - perfect_scores,
                'percentage': (perfect_scores / 3) * 100
            })
        
        return progress
    
    @staticmethod
    def revoke_badge(badge_id: int) -> Tuple[bool, str]:
        """Revoke a badge (admin function)
        
        Args:
            badge_id: Badge ID to revoke
            
        Returns:
            Tuple of (success, message)
        """
        badge = Badge.query.get(badge_id)
        if not badge:
            return False, "Badge not found."
        
        db.session.delete(badge)
        db.session.commit()
        
        return True, "Badge revoked successfully."
    
    @staticmethod
    def get_badge_analytics() -> Dict:
        """Get overall badge analytics
        
        Returns:
            Badge analytics dictionary
        """
        # Total badges awarded
        total_badges = Badge.query.count()
        
        # Badges by type
        badge_type_counts = db.session.query(
            Badge.badge_type,
            func.count(Badge.id)
        ).group_by(Badge.badge_type).all()
        
        # Recent badge activity (last 30 days)
        recent_date = datetime.utcnow().replace(day=1)
        recent_badges = Badge.query.filter(Badge.earned_at >= recent_date).count()
        
        # Most active users (by badge count)
        top_users = db.session.query(
            Badge.user_id,
            func.count(Badge.id)
        ).group_by(Badge.user_id).order_by(func.count(Badge.id).desc()).limit(5).all()
        
        return {
            'total_badges': total_badges,
            'badge_type_distribution': dict(badge_type_counts),
            'recent_badges': recent_badges,
            'top_users': [{'user_id': user_id, 'badge_count': count} for user_id, count in top_users]
        }