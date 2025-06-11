"""Redesigned Module Models - Version 2

This file contains the new simplified module system models that address
the issues identified in the current implementation.

Key improvements:
- Simplified relationships
- Better data integrity
- Clearer separation of concerns
- Optimized for performance
"""

from datetime import datetime
from app import db
from sqlalchemy import Index


class ModuleV2(db.Model):
    """Simplified Module model with better structure"""
    __tablename__ = 'modules_v2'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    content_type = db.Column(db.String(50), default='standard')  # standard, interactive, quiz
    order = db.Column(db.Integer, nullable=False)
    
    # Content management
    content_file = db.Column(db.String(255))  # Path to content JSON file
    template_name = db.Column(db.String(100), default='module_base.html')
    
    # Module settings
    is_active = db.Column(db.Boolean, default=True)
    requires_completion = db.Column(db.Boolean, default=True)
    passing_score = db.Column(db.Integer, default=70)  # For modules with quizzes
    
    # Metadata
    estimated_duration = db.Column(db.Integer)  # in minutes
    difficulty_level = db.Column(db.String(20), default='beginner')  # beginner, intermediate, advanced
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    prerequisites = db.relationship(
        'ModulePrerequisite',
        foreign_keys='ModulePrerequisite.module_id',
        backref='module',
        cascade='all, delete-orphan'
    )
    
    progress_records = db.relationship(
        'ModuleProgressV2',
        backref='module',
        cascade='all, delete-orphan'
    )
    
    quiz = db.relationship(
        'QuizV2',
        backref='module',
        uselist=False,
        cascade='all, delete-orphan'
    )
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_module_order', 'order'),
        Index('idx_module_active', 'is_active'),
    )
    
    def __repr__(self):
        return f'<ModuleV2 {self.id}: {self.title}>'
    
    def to_dict(self):
        """Convert module to dictionary for API responses"""
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'content_type': self.content_type,
            'order': self.order,
            'is_active': self.is_active,
            'estimated_duration': self.estimated_duration,
            'difficulty_level': self.difficulty_level,
            'passing_score': self.passing_score,
            'has_quiz': self.quiz is not None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def get_prerequisites(self):
        """Get list of prerequisite module IDs"""
        return [prereq.prerequisite_id for prereq in self.prerequisites]
    
    def has_prerequisite(self, module_id):
        """Check if a module is a prerequisite"""
        return module_id in self.get_prerequisites()
    
    @classmethod
    def get_active_modules(cls):
        """Get all active modules ordered by order"""
        return cls.query.filter_by(is_active=True).order_by(cls.order).all()
    
    @classmethod
    def get_by_order(cls, order):
        """Get module by order number"""
        return cls.query.filter_by(order=order, is_active=True).first()


class ModulePrerequisite(db.Model):
    """Module prerequisite relationships"""
    __tablename__ = 'module_prerequisites_v2'
    
    id = db.Column(db.Integer, primary_key=True)
    module_id = db.Column(db.Integer, db.ForeignKey('modules_v2.id'), nullable=False)
    prerequisite_id = db.Column(db.Integer, db.ForeignKey('modules_v2.id'), nullable=False)
    
    # Ensure a module can't be its own prerequisite
    __table_args__ = (
        db.CheckConstraint('module_id != prerequisite_id', name='no_self_prerequisite'),
        db.UniqueConstraint('module_id', 'prerequisite_id', name='unique_prerequisite'),
        Index('idx_module_prereq', 'module_id', 'prerequisite_id'),
    )
    
    def __repr__(self):
        return f'<ModulePrerequisite {self.module_id} requires {self.prerequisite_id}>'


class ModuleProgressV2(db.Model):
    """Simplified progress tracking"""
    __tablename__ = 'module_progress_v2'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    module_id = db.Column(db.Integer, db.ForeignKey('modules_v2.id'), nullable=False)
    
    # Progress tracking
    status = db.Column(db.String(20), default='not_started')  # not_started, in_progress, completed
    progress_percentage = db.Column(db.Integer, default=0)  # 0-100
    
    # Quiz results (if module has quiz)
    quiz_score = db.Column(db.Integer)  # 0-100
    quiz_attempts = db.Column(db.Integer, default=0)
    quiz_passed = db.Column(db.Boolean, default=False)
    
    # Timestamps
    started_at = db.Column(db.DateTime)
    completed_at = db.Column(db.DateTime)
    last_accessed = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref='module_progress_v2')
    
    # Constraints
    __table_args__ = (
        db.UniqueConstraint('user_id', 'module_id', name='unique_user_module_progress'),
        Index('idx_user_progress', 'user_id', 'module_id'),
        Index('idx_module_progress_status', 'module_id', 'status'),
        db.CheckConstraint('progress_percentage >= 0 AND progress_percentage <= 100', name='valid_progress'),
        db.CheckConstraint('quiz_score IS NULL OR (quiz_score >= 0 AND quiz_score <= 100)', name='valid_quiz_score'),
    )
    
    def __repr__(self):
        return f'<ModuleProgressV2 User:{self.user_id} Module:{self.module_id} {self.status}>'
    
    def to_dict(self):
        """Convert progress to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'module_id': self.module_id,
            'status': self.status,
            'progress_percentage': self.progress_percentage,
            'quiz_score': self.quiz_score,
            'quiz_attempts': self.quiz_attempts,
            'quiz_passed': self.quiz_passed,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'last_accessed': self.last_accessed.isoformat() if self.last_accessed else None
        }
    
    def start_module(self):
        """Mark module as started"""
        if self.status == 'not_started':
            self.status = 'in_progress'
            self.started_at = datetime.utcnow()
            self.last_accessed = datetime.utcnow()
    
    def update_progress(self, percentage):
        """Update progress percentage"""
        self.progress_percentage = max(0, min(100, percentage))
        self.last_accessed = datetime.utcnow()
        
        if self.status == 'not_started':
            self.start_module()
    
    def complete_module(self, quiz_score=None):
        """Mark module as completed"""
        self.status = 'completed'
        self.progress_percentage = 100
        self.completed_at = datetime.utcnow()
        self.last_accessed = datetime.utcnow()
        
        if quiz_score is not None:
            self.quiz_score = quiz_score
            # Check if quiz passed based on module's passing score
            if self.module and self.module.passing_score:
                self.quiz_passed = quiz_score >= self.module.passing_score
    
    def record_quiz_attempt(self, score):
        """Record a quiz attempt"""
        self.quiz_attempts += 1
        self.quiz_score = score
        self.last_accessed = datetime.utcnow()
        
        # Check if quiz passed
        if self.module and self.module.passing_score:
            self.quiz_passed = score >= self.module.passing_score
            
            # If quiz passed and module requires completion, mark as completed
            if self.quiz_passed and self.module.requires_completion:
                self.complete_module(score)
    
    @classmethod
    def get_user_progress(cls, user_id, module_id):
        """Get or create progress record for user and module"""
        progress = cls.query.filter_by(user_id=user_id, module_id=module_id).first()
        if not progress:
            progress = cls(user_id=user_id, module_id=module_id)
            db.session.add(progress)
        return progress
    
    @classmethod
    def get_user_module_stats(cls, user_id):
        """Get user's overall module statistics"""
        progress_records = cls.query.filter_by(user_id=user_id).all()
        
        total_modules = len(progress_records)
        completed_modules = len([p for p in progress_records if p.status == 'completed'])
        in_progress_modules = len([p for p in progress_records if p.status == 'in_progress'])
        
        return {
            'total_modules': total_modules,
            'completed_modules': completed_modules,
            'in_progress_modules': in_progress_modules,
            'completion_rate': (completed_modules / total_modules * 100) if total_modules > 0 else 0
        }


class ModuleContentV2(db.Model):
    """Module content sections for dynamic content management"""
    __tablename__ = 'module_content_v2'
    
    id = db.Column(db.Integer, primary_key=True)
    module_id = db.Column(db.Integer, db.ForeignKey('modules_v2.id'), nullable=False)
    
    # Content structure
    section_type = db.Column(db.String(50), nullable=False)  # text, image, video, interactive, quiz
    section_order = db.Column(db.Integer, nullable=False)
    title = db.Column(db.String(200))
    content = db.Column(db.Text)
    
    # Additional properties (stored as JSON)
    properties = db.Column(db.JSON)  # For storing section-specific data
    
    # Metadata
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    module = db.relationship('ModuleV2', backref='content_sections')
    
    # Constraints
    __table_args__ = (
        Index('idx_module_content_order', 'module_id', 'section_order'),
        Index('idx_module_content_type', 'module_id', 'section_type'),
    )
    
    def __repr__(self):
        return f'<ModuleContentV2 {self.module_id}.{self.section_order}: {self.section_type}>'
    
    def to_dict(self):
        """Convert content section to dictionary"""
        return {
            'id': self.id,
            'section_type': self.section_type,
            'section_order': self.section_order,
            'title': self.title,
            'content': self.content,
            'properties': self.properties,
            'is_active': self.is_active
        }
    
    @classmethod
    def get_module_content(cls, module_id):
        """Get all active content sections for a module"""
        return cls.query.filter_by(
            module_id=module_id,
            is_active=True
        ).order_by(cls.section_order).all()