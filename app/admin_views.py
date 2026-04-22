"""
Flask-Admin views for the security portal administration.
Provides CRUD interfaces for managing users, modules, campaigns, and other entities.
"""

import os
from flask_admin import BaseView, expose, AdminIndexView
from flask_admin.contrib.sqla import ModelView
from flask_admin.actions import action
from flask_login import current_user
from flask import redirect, url_for, flash, request, current_app, make_response
from sqlalchemy import func, and_, or_, case
from datetime import datetime, timedelta
from app.models.user import User
from app.models.module import Module, Quiz, Question, Choice, UserProgress
from app.models.campaign import Campaign, PhishingSimulation, PhishingTarget, Certificate
from app.models.settings import Setting
from app.models.badge import Badge
from app import db


def get_redirect_target():
    """Get redirect target from request args."""
    return request.args.get('url') or request.referrer


class AdminAuthMixin:
    """Mixin to restrict access to admin users only."""
    
    def is_accessible(self):
        return current_user.is_authenticated and current_user.is_admin()
    
    def inaccessible_callback(self, name, **kwargs):
        flash('Accès refusé. Vous devez être administrateur.', 'error')
        return redirect(url_for('main.dashboard'))


class CustomAdminIndexView(AdminAuthMixin, AdminIndexView):
    """Custom admin index view with dashboard."""
    
    @expose('/')
    def index(self):
        # Basic statistics
        total_users = User.query.count()
        total_modules = Module.query.count()
        total_campaigns = Campaign.query.count()
        active_users = User.query.filter(User.last_login.isnot(None)).count()
        
        # Advanced KPIs
        # Department participation rates
        dept_stats = db.session.query(
            User.department,
            func.count(User.id).label('total_users'),
            func.count(UserProgress.id).label('completions')
        ).outerjoin(UserProgress, User.id == UserProgress.user_id)\
         .group_by(User.department).all()
        
        # Module completion rates
        module_stats = db.session.query(
            Module.title,
            Module.id,
            func.count(UserProgress.id).label('completions'),
            func.avg(UserProgress.score).label('avg_score')
        ).outerjoin(UserProgress, Module.id == UserProgress.module_id)\
         .group_by(Module.id, Module.title).all()
        
        # Recent activity (last 30 days)
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        recent_completions = UserProgress.query.filter(
            UserProgress.completed_at >= thirty_days_ago
        ).count()
        
        # Weekly progress trend
        weekly_stats = []
        for i in range(7):
            week_start = datetime.utcnow() - timedelta(days=(i+1)*7)
            week_end = datetime.utcnow() - timedelta(days=i*7)
            week_completions = UserProgress.query.filter(
                and_(
                    UserProgress.completed_at >= week_start,
                    UserProgress.completed_at < week_end
                )
            ).count()
            weekly_stats.append({
                'week': f"Semaine {7-i}",
                'completions': week_completions
            })
        
        # Quiz performance analytics
        quiz_stats = db.session.query(
            Quiz.title,
            func.count(UserProgress.id).label('attempts'),
            func.avg(UserProgress.score).label('avg_score'),
            func.max(UserProgress.score).label('max_score'),
            func.min(UserProgress.score).label('min_score')
        ).join(UserProgress, Quiz.module_id == UserProgress.module_id)\
         .group_by(Quiz.id, Quiz.title).all()
        
        # Users at risk (low scores or no recent activity)
        at_risk_users = User.query.outerjoin(UserProgress)\
            .filter(
                or_(
                    User.last_login < thirty_days_ago,
                    and_(
                        UserProgress.score < 60,
                        UserProgress.completed_at >= thirty_days_ago
                    )
                )
            ).limit(10).all()
        
        # Recent activity
        recent_users = User.query.order_by(User.created_at.desc()).limit(5).all()
        recent_progress = UserProgress.query.filter(UserProgress.completed_at.isnot(None))\
            .order_by(UserProgress.completed_at.desc()).limit(10).all()
        
        # Calculate overall completion rate
        total_possible_completions = total_users * total_modules
        total_actual_completions = UserProgress.query.filter(UserProgress.completed == True).count()
        overall_completion_rate = (total_actual_completions / total_possible_completions * 100) if total_possible_completions > 0 else 0
        
        return self.render('admin/custom_index.html',
                         total_users=total_users,
                         total_modules=total_modules,
                         total_campaigns=total_campaigns,
                         active_users=active_users,
                         recent_users=recent_users,
                         recent_progress=recent_progress,
                         dept_stats=dept_stats,
                         module_stats=module_stats,
                         recent_completions=recent_completions,
                         weekly_stats=weekly_stats,
                         quiz_stats=quiz_stats,
                         at_risk_users=at_risk_users,
                         overall_completion_rate=round(overall_completion_rate, 1))


class UserAdminView(AdminAuthMixin, ModelView):
    """Admin view for managing users with enhanced functionality."""
    
    column_list = ['id', 'email', 'firstname', 'lastname', 'role', 'department', 'is_active', 'created_at', 'last_login']
    column_searchable_list = ['email', 'firstname', 'lastname', 'department']
    column_filters = ['role', 'department', 'is_active', 'created_at', 'last_login']
    column_default_sort = ('created_at', True)
    column_editable_list = ['is_active', 'role', 'department']
    
    form_columns = ['email', 'firstname', 'lastname', 'role', 'department', 'is_active']
    
    column_labels = {
        'email': 'Email',
        'firstname': 'Prénom',
        'lastname': 'Nom',
        'role': 'Rôle',
        'department': 'Département',
        'is_active': 'Actif',
        'created_at': 'Créé le',
        'last_login': 'Dernière connexion'
    }
    
    form_choices = {
        'role': [
            ('user', 'Utilisateur'),
            ('admin', 'Administrateur')
        ],
        'department': [
            ('IT', 'Informatique'),
            ('HR', 'Ressources Humaines'),
            ('Operations', 'Opérations'),
            ('Security', 'Sécurité'),
            ('Logistics', 'Logistique'),
            ('Finance', 'Finance'),
            ('Management', 'Direction'),
            ('Commercial', 'Commercial')
        ]
    }
    
    can_export = True
    export_max_rows = 1000
    page_size = 25
    
    # Bulk actions
    action_disallowed_list = ['delete']  # Prevent accidental deletions
    
    @expose('/details/')
    def details_view(self):
        """Enhanced user details view with progress tracking."""
        return_url = get_redirect_target() or url_for('.index_view')
        id = request.args.get('id')
        if id is None:
            return redirect(return_url)

        model = self.get_one(id)
        if model is None:
            flash(f'Record does not exist.', 'error')
            return redirect(return_url)

        # Get user progress
        user_progress = UserProgress.query.filter_by(user_id=id).all()
        total_modules = Module.query.filter_by(is_active=True).count()
        completed_modules = len([p for p in user_progress if p.completed])
        completion_rate = (completed_modules / total_modules * 100) if total_modules > 0 else 0
        
        # Get recent activity
        recent_activity = UserProgress.query.filter_by(user_id=id)\
            .order_by(UserProgress.completed_at.desc()).limit(5).all()

        return self.render('admin/user_details.html',
                         model=model,
                         user_progress=user_progress,
                         completed_modules=completed_modules,
                         total_modules=total_modules,
                         completion_rate=completion_rate,
                         recent_activity=recent_activity,
                         return_url=return_url)
    
    @action('activate', 'Activer', 'Êtes-vous sûr de vouloir activer les utilisateurs sélectionnés?')
    def action_activate(self, ids):
        """Bulk activate users."""
        try:
            query = User.query.filter(User.id.in_(ids))
            count = query.update({User.is_active: True}, synchronize_session=False)
            db.session.commit()
            flash(f'{count} utilisateur(s) activé(s) avec succès.', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Erreur lors de l\'activation: {str(e)}', 'error')

    @action('deactivate', 'Désactiver', 'Êtes-vous sûr de vouloir désactiver les utilisateurs sélectionnés?')
    def action_deactivate(self, ids):
        """Bulk deactivate users."""
        try:
            query = User.query.filter(User.id.in_(ids))
            count = query.update({User.is_active: False}, synchronize_session=False)
            db.session.commit()
            flash(f'{count} utilisateur(s) désactivé(s) avec succès.', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Erreur lors de la désactivation: {str(e)}', 'error')

    @action('reset_password', 'Réinitialiser mot de passe', 'Générer un nouveau mot de passe temporaire?')
    def action_reset_password(self, ids):
        """Bulk password reset."""
        try:
            from app import bcrypt
            import secrets
            import string
            
            reset_info = []
            for user_id in ids:
                user = db.session.get(User, user_id)
                if user:
                    # Generate secure temporary password
                    temp_password = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(12))
                    user.password = bcrypt.generate_password_hash(temp_password).decode('utf-8')
                    reset_info.append(f"{user.email}: {temp_password}")
            
            db.session.commit()
            
            # Display passwords (in production, these should be sent via email)
            flash('Mots de passe temporaires générés. Notez-les bien:', 'info')
            for info in reset_info:
                flash(info, 'warning')
                
        except Exception as e:
            db.session.rollback()
            flash(f'Erreur lors de la réinitialisation: {str(e)}', 'error')
    
    def on_model_change(self, form, model, is_created):
        """Handle password hashing for new users."""
        if is_created:
            # Generate temporary password for new users
            import secrets
            import string
            from app import bcrypt
            
            temp_password = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(12))
            model.password = bcrypt.generate_password_hash(temp_password).decode('utf-8')
            flash(f'Mot de passe temporaire pour {model.email}: {temp_password}', 'info')
    
    def create_model(self, form):
        """Override to handle user creation with password."""
        try:
            return super().create_model(form)
        except Exception as e:
            flash(f'Erreur lors de la création: {str(e)}', 'error')
            return False


class ModuleAdminView(AdminAuthMixin, ModelView):
    """Admin view for managing training modules with enhanced functionality."""
    
    column_list = ['id', 'title', 'order', 'is_active', 'completion_count', 'avg_score', 'created_at']
    column_searchable_list = ['title', 'description']
    column_filters = ['is_active', 'created_at']
    column_default_sort = ('order', False)
    column_editable_list = ['is_active', 'order']
    
    form_columns = ['title', 'description', 'content', 'order', 'image', 'is_active']
    
    column_labels = {
        'title': 'Titre',
        'description': 'Description',
        'order': 'Ordre',
        'content': 'Contenu',
        'image': 'Image',
        'is_active': 'Actif',
        'completion_count': 'Complétions',
        'avg_score': 'Score Moyen',
        'created_at': 'Créé le'
    }
    
    can_export = True
    page_size = 20
    
    def get_query(self):
        """Enhanced query with completion statistics."""
        return self.session.query(self.model).outerjoin(UserProgress)
    
    def get_count_query(self):
        """Count query for pagination."""
        return self.session.query(func.count('*')).select_from(self.model)
    
    @expose('/details/')
    def details_view(self):
        """Enhanced module details view with progress analytics."""
        return_url = get_redirect_target() or url_for('.index_view')
        id = request.args.get('id')
        if id is None:
            return redirect(return_url)

        model = self.get_one(id)
        if model is None:
            flash(f'Record does not exist.', 'error')
            return redirect(return_url)

        # Get module statistics
        total_users = User.query.filter_by(is_active=True).count()
        completions = UserProgress.query.filter_by(module_id=id, completed=True).count()
        avg_score = db.session.query(func.avg(UserProgress.score))\
            .filter_by(module_id=id, completed=True).scalar() or 0
        
        # Get completion trend (last 30 days)
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        recent_completions = UserProgress.query.filter(
            UserProgress.module_id == id,
            UserProgress.completed_at >= thirty_days_ago
        ).count()
        
        # Get quiz statistics if available
        quiz_stats = None
        quiz = Quiz.query.filter_by(module_id=id).first()
        if quiz:
            quiz_attempts = UserProgress.query.filter_by(module_id=id).count()
            quiz_stats = {
                'attempts': quiz_attempts,
                'completions': completions,
                'success_rate': (completions / quiz_attempts * 100) if quiz_attempts > 0 else 0
            }

        return self.render('admin/module_details.html',
                         model=model,
                         total_users=total_users,
                         completions=completions,
                         completion_rate=(completions / total_users * 100) if total_users > 0 else 0,
                         avg_score=round(avg_score, 1),
                         recent_completions=recent_completions,
                         quiz_stats=quiz_stats,
                         return_url=return_url)
    
    @action('activate', 'Activer', 'Activer les modules sélectionnés?')
    def action_activate(self, ids):
        """Bulk activate modules."""
        try:
            query = Module.query.filter(Module.id.in_(ids))
            count = query.update({Module.is_active: True}, synchronize_session=False)
            db.session.commit()
            flash(f'{count} module(s) activé(s) avec succès.', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Erreur lors de l\'activation: {str(e)}', 'error')

    @action('deactivate', 'Désactiver', 'Désactiver les modules sélectionnés?')
    def action_deactivate(self, ids):
        """Bulk deactivate modules."""
        try:
            query = Module.query.filter(Module.id.in_(ids))
            count = query.update({Module.is_active: False}, synchronize_session=False)
            db.session.commit()
            flash(f'{count} module(s) désactivé(s) avec succès.', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Erreur lors de la désactivation: {str(e)}', 'error')

    @action('reset_progress', 'Réinitialiser progrès', 'Réinitialiser le progrès de tous les utilisateurs?')
    def action_reset_progress(self, ids):
        """Reset user progress for selected modules."""
        try:
            count = 0
            for module_id in ids:
                progress_count = UserProgress.query.filter_by(module_id=module_id).count()
                UserProgress.query.filter_by(module_id=module_id).delete()
                count += progress_count
            
            db.session.commit()
            flash(f'Progrès réinitialisé pour {count} entrée(s).', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Erreur lors de la réinitialisation: {str(e)}', 'error')
    
    def on_model_change(self, form, model, is_created):
        """Handle module changes."""
        if is_created:
            # Set default order if not provided
            if not model.order:
                max_order = db.session.query(func.max(Module.order)).scalar() or 0
                model.order = max_order + 1
    
    form_widget_args = {
        'content': {
            'rows': 10,
            'class': 'form-control'
        },
        'description': {
            'rows': 3,
            'class': 'form-control'
        }
    }


class CampaignAdminView(AdminAuthMixin, ModelView):
    """Admin view for managing phishing campaigns."""
    
    column_list = ['id', 'name', 'type', 'status', 'created_at', 'targets_count']
    column_searchable_list = ['name', 'description']
    column_filters = ['type', 'status', 'created_at']
    
    form_columns = ['name', 'description', 'type', 'status']
    
    column_labels = {
        'name': 'Nom',
        'description': 'Description',
        'type': 'Type',
        'status': 'Statut',
        'created_at': 'Créé le',
        'targets_count': 'Nb. cibles'
    }
    
    def targets_count(view, context, model, name):
        """Custom column to show target count."""
        return PhishingTarget.query.filter_by(campaign_id=model.id).count()
    
    column_formatters = {
        'targets_count': targets_count
    }


class SettingsAdminView(AdminAuthMixin, ModelView):
    """Admin view for managing application settings."""
    
    column_list = ['key', 'value', 'description']
    column_searchable_list = ['key', 'description']
    
    form_columns = ['key', 'value', 'description']
    
    column_labels = {
        'key': 'Clé',
        'value': 'Valeur',
        'description': 'Description'
    }
    
    form_widget_args = {
        'description': {
            'rows': 2,
            'class': 'form-control'
        }
    }


class UserProgressAdminView(AdminAuthMixin, ModelView):
    """Admin view for monitoring user progress."""
    
    column_list = ['id', 'user_id', 'module_id', 'score', 'completed_at', 'completed']
    column_searchable_list = []  # Remove search on relationship fields
    column_filters = ['score', 'completed_at', 'completed']
    column_default_sort = ('completed_at', True)
    
    can_create = False  # Progress is created automatically
    can_edit = False    # Progress should not be manually edited
    can_delete = True   # Allow deletion for cleanup
    
    column_labels = {
        'user_id': 'ID Utilisateur',
        'module_id': 'ID Module',
        'score': 'Score',
        'completed_at': 'Complété le',
        'completed': 'Terminé'
    }


class ReportsView(AdminAuthMixin, BaseView):
    """Custom view for generating reports."""
    
    @expose('/')
    def index(self):
        return self.render('admin/reports.html')
    
    @expose('/users')
    def users_report(self):
        """Generate user statistics report."""
        users_by_dept = db.session.query(
            User.department,
            db.func.count(User.id).label('count')
        ).group_by(User.department).all()
        
        users_by_role = db.session.query(
            User.role,
            db.func.count(User.id).label('count')
        ).group_by(User.role).all()
        
        return self.render('admin/users_report.html',
                         users_by_dept=users_by_dept,
                         users_by_role=users_by_role)
    
    @expose('/progress')
    def progress_report(self):
        """Generate progress statistics report."""
        module_completion = db.session.query(
            Module.title,
            db.func.count(UserProgress.id).label('completions'),
            db.func.avg(UserProgress.score).label('avg_score')
        ).join(UserProgress).group_by(Module.id).all()
        
        return self.render('admin/progress_report.html',
                         module_completion=module_completion)


class ReportingView(AdminAuthMixin, BaseView):
    """Advanced reporting and analytics view."""
    
    @expose('/')
    def index(self):
        """Main reporting dashboard."""
        # Department Performance Analysis
        dept_performance = db.session.query(
            User.department,
            func.count(User.id).label('total_users'),
            func.count(UserProgress.id).label('total_completions'),
            func.avg(UserProgress.score).label('avg_score'),
            func.count(case([(UserProgress.completed == True, 1)])).label('completed_modules')
        ).outerjoin(UserProgress, User.id == UserProgress.user_id)\
         .group_by(User.department).all()
        
        # Module Performance Analysis
        module_performance = db.session.query(
            Module.title,
            Module.id,
            func.count(UserProgress.id).label('attempts'),
            func.count(case([(UserProgress.completed == True, 1)])).label('completions'),
            func.avg(UserProgress.score).label('avg_score'),
            func.min(UserProgress.score).label('min_score'),
            func.max(UserProgress.score).label('max_score')
        ).outerjoin(UserProgress, Module.id == UserProgress.module_id)\
         .filter(Module.is_active == True)\
         .group_by(Module.id, Module.title).all()
        
        # Time-based analytics (last 6 months)
        monthly_stats = []
        for i in range(6):
            month_start = datetime.utcnow().replace(day=1) - timedelta(days=i*30)
            month_end = month_start + timedelta(days=30)
            
            completions = UserProgress.query.filter(
                and_(
                    UserProgress.completed_at >= month_start,
                    UserProgress.completed_at < month_end,
                    UserProgress.completed == True
                )
            ).count()
            
            monthly_stats.append({
                'month': month_start.strftime('%B %Y'),
                'completions': completions
            })
        
        monthly_stats.reverse()  # Show oldest to newest
        
        # User engagement metrics
        engagement_stats = {
            'active_users_week': User.query.filter(
                User.last_login >= datetime.utcnow() - timedelta(days=7)
            ).count(),
            'active_users_month': User.query.filter(
                User.last_login >= datetime.utcnow() - timedelta(days=30)
            ).count(),
            'never_logged': User.query.filter(User.last_login.is_(None)).count(),
            'high_performers': UserProgress.query.filter(
                UserProgress.score >= 90, UserProgress.completed == True
            ).count(),
            'low_performers': UserProgress.query.filter(
                UserProgress.score < 60, UserProgress.completed == True
            ).count()
        }
        
        # Risk analysis
        at_risk_departments = []
        for dept in dept_performance:
            if dept.total_users > 0:
                completion_rate = (dept.completed_modules / (dept.total_users * Module.query.filter_by(is_active=True).count()) * 100) if Module.query.filter_by(is_active=True).count() > 0 else 0
                avg_score = dept.avg_score or 0
                
                if completion_rate < 50 or avg_score < 60:
                    at_risk_departments.append({
                        'department': dept.department or 'Non spécifié',
                        'completion_rate': completion_rate,
                        'avg_score': avg_score,
                        'total_users': dept.total_users
                    })
        
        return self.render('admin/reporting.html',
                         dept_performance=dept_performance,
                         module_performance=module_performance,
                         monthly_stats=monthly_stats,
                         engagement_stats=engagement_stats,
                         at_risk_departments=at_risk_departments)
    
    @expose('/export/')
    def export_data(self):
        """Export comprehensive report data."""
        import csv
        from io import StringIO
        
        output = StringIO()
        writer = csv.writer(output)
        
        # Export user progress data
        writer.writerow(['Email', 'Prénom', 'Nom', 'Département', 'Module', 'Score', 'Complété', 'Date Completion'])
        
        progress_data = db.session.query(
            User.email, User.firstname, User.lastname, User.department,
            Module.title, UserProgress.score, UserProgress.completed, UserProgress.completed_at
        ).join(UserProgress, User.id == UserProgress.user_id)\
         .join(Module, UserProgress.module_id == Module.id).all()
        
        for row in progress_data:
            writer.writerow([
                row.email,
                row.firstname or '',
                row.lastname or '',
                row.department or '',
                row.title,
                row.score or '',
                'Oui' if row.completed else 'Non',
                row.completed_at.strftime('%d/%m/%Y %H:%M') if row.completed_at else ''
            ])
        
        output.seek(0)
        response = make_response(output.getvalue())
        response.headers['Content-Type'] = 'text/csv'
        response.headers['Content-Disposition'] = f'attachment; filename=rapport_formation_{datetime.utcnow().strftime("%Y%m%d")}.csv'
        
        return response


class SystemConfigView(AdminAuthMixin, BaseView):
    """System configuration and settings view."""
    
    @expose('/')
    def index(self):
        """System configuration dashboard."""
        # Get system settings
        settings = Setting.query.all()
        settings_dict = {s.key: s.value for s in settings}
        
        # System statistics
        system_stats = {
            'total_users': User.query.count(),
            'total_modules': Module.query.count(),
            'total_progress': UserProgress.query.count(),
            'database_size': self._get_database_size(),
            'last_backup': settings_dict.get('last_backup_date', 'Jamais'),
            'system_version': '1.0.0'
        }
        
        return self.render('admin/system_config.html',
                         settings=settings,
                         system_stats=system_stats)
    
    def _get_database_size(self):
        """Get database size estimation."""
        try:
            import os
            db_path = current_app.config.get('DATABASE_PATH', 'instance/database.db')
            if os.path.exists(db_path):
                size_bytes = os.path.getsize(db_path)
                if size_bytes < 1024:
                    return f"{size_bytes} B"
                elif size_bytes < 1024**2:
                    return f"{size_bytes/1024:.1f} KB"
                elif size_bytes < 1024**3:
                    return f"{size_bytes/(1024**2):.1f} MB"
                else:
                    return f"{size_bytes/(1024**3):.1f} GB"
            return "Non disponible"
        except:
            return "Erreur de calcul"
    
    @expose('/backup/', methods=['POST'])
    def create_backup(self):
        """Create system backup."""
        try:
            import shutil
            from datetime import datetime
            
            backup_dir = 'backups'
            if not os.path.exists(backup_dir):
                os.makedirs(backup_dir)
            
            timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
            backup_path = f"{backup_dir}/backup_{timestamp}.db"
            
            db_path = current_app.config.get('DATABASE_PATH', 'instance/database.db')
            shutil.copy2(db_path, backup_path)
            
            # Update last backup setting
            backup_setting = Setting.query.filter_by(key='last_backup_date').first()
            if not backup_setting:
                backup_setting = Setting(key='last_backup_date', value='', description='Date de la dernière sauvegarde')
                db.session.add(backup_setting)
            
            backup_setting.value = datetime.utcnow().strftime('%d/%m/%Y %H:%M')
            db.session.commit()
            
            flash(f'Sauvegarde créée avec succès: {backup_path}', 'success')
        except Exception as e:
            flash(f'Erreur lors de la sauvegarde: {str(e)}', 'error')
        
        return redirect(url_for('.index'))


class PhishingSimulationAdminView(AdminAuthMixin, ModelView):
    """Admin view for managing phishing simulations."""
    
    column_list = ['id', 'title', 'template', 'campaign_id', 'description', 'created_at', 'sent_at']
    column_searchable_list = ['title', 'template', 'description']
    column_filters = ['template', 'created_at', 'sent_at', 'campaign_id']
    column_default_sort = ('created_at', True)
    
    form_columns = ['campaign_id', 'title', 'template', 'description']
    
    column_labels = {
        'campaign_id': 'Campagne',
        'title': 'Titre',
        'template': 'Template',
        'description': 'Description',
        'created_at': 'Créé le',
        'sent_at': 'Envoyé le'
    }
    
    form_choices = {
        'template': [
            ('phishing_generic', 'Phishing générique'),
            ('spear_phishing', 'Spear phishing'),
            ('business_email', 'Email professionnel'),
            ('social_media', 'Réseaux sociaux'),
            ('urgent_request', 'Demande urgente'),
            ('invoice', 'Facture'),
            ('security_alert', 'Alerte sécurité')
        ]
    }
    
    can_export = True
    page_size = 20
    
    def scaffold_form(self):
        """Customize the form to include campaign selection."""
        form_class = super(PhishingSimulationAdminView, self).scaffold_form()
        # Add custom form logic if needed
        return form_class


class CertificateAdminView(AdminAuthMixin, ModelView):
    """Admin view for managing certificates."""
    
    column_list = ['id', 'title', 'user_id', 'module_id', 'certificate_id', 'issued_at', 'expiry_date']
    column_searchable_list = ['title', 'certificate_id', 'description']
    column_filters = ['issued_at', 'expiry_date', 'user_id', 'module_id']
    column_default_sort = ('issued_at', True)
    
    form_columns = ['user_id', 'module_id', 'title', 'description', 'expiry_date', 'certificate_id']
    
    column_labels = {
        'user_id': 'Utilisateur',
        'module_id': 'Module',
        'title': 'Titre',
        'description': 'Description',
        'issued_at': 'Date d\'émission',
        'expiry_date': 'Date d\'expiration',
        'certificate_id': 'ID Certificat'
    }
    
    can_export = True
    page_size = 25
    
    def scaffold_form(self):
        """Customize the form to include user and module selection."""
        form_class = super(CertificateAdminView, self).scaffold_form()
        # Add custom form logic if needed
        return form_class
