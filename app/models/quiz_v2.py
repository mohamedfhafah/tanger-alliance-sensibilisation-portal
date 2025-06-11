"""Redesigned Quiz Models - Version 2

This file contains the new simplified quiz system models that address
the issues identified in the current implementation.

Key improvements:
- Simplified quiz structure
- Better question management
- Improved answer tracking
- Optimized for performance
- Clear separation from module logic
"""

from datetime import datetime
from app import db
from sqlalchemy import Index
import json


class QuizV2(db.Model):
    """Simplified Quiz model"""
    __tablename__ = 'quizzes_v2'
    
    id = db.Column(db.Integer, primary_key=True)
    module_id = db.Column(db.Integer, db.ForeignKey('modules_v2.id'), nullable=False)
    
    # Quiz settings
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    instructions = db.Column(db.Text)
    
    # Quiz configuration
    time_limit = db.Column(db.Integer)  # in minutes, null = no limit
    max_attempts = db.Column(db.Integer, default=3)
    passing_score = db.Column(db.Integer, default=70)  # 0-100
    randomize_questions = db.Column(db.Boolean, default=False)
    show_correct_answers = db.Column(db.Boolean, default=True)
    
    # Quiz state
    is_active = db.Column(db.Boolean, default=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    questions = db.relationship(
        'QuestionV2',
        backref='quiz',
        cascade='all, delete-orphan',
        order_by='QuestionV2.order'
    )
    
    attempts = db.relationship(
        'QuizAttemptV2',
        backref='quiz',
        cascade='all, delete-orphan'
    )
    
    # Indexes
    __table_args__ = (
        Index('idx_quiz_module', 'module_id'),
        Index('idx_quiz_active', 'is_active'),
    )
    
    def __repr__(self):
        return f'<QuizV2 {self.id}: {self.title}>'
    
    def to_dict(self, include_questions=False):
        """Convert quiz to dictionary"""
        data = {
            'id': self.id,
            'module_id': self.module_id,
            'title': self.title,
            'description': self.description,
            'instructions': self.instructions,
            'time_limit': self.time_limit,
            'max_attempts': self.max_attempts,
            'passing_score': self.passing_score,
            'randomize_questions': self.randomize_questions,
            'show_correct_answers': self.show_correct_answers,
            'is_active': self.is_active,
            'question_count': len(self.questions),
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
        
        if include_questions:
            data['questions'] = [q.to_dict(include_choices=True) for q in self.questions]
        
        return data
    
    def get_questions_for_attempt(self):
        """Get questions for a quiz attempt (randomized if configured)"""
        questions = self.questions
        
        if self.randomize_questions:
            import random
            questions = list(questions)
            random.shuffle(questions)
        
        return questions
    
    def calculate_score(self, answers):
        """Calculate score based on answers
        
        Args:
            answers: dict with question_id as key and choice_id as value
        
        Returns:
            tuple: (score_percentage, correct_count, total_count)
        """
        total_questions = len(self.questions)
        correct_answers = 0
        
        for question in self.questions:
            user_choice_id = answers.get(str(question.id))
            if user_choice_id:
                correct_choice = question.get_correct_choice()
                if correct_choice and str(correct_choice.id) == str(user_choice_id):
                    correct_answers += 1
        
        score_percentage = (correct_answers / total_questions * 100) if total_questions > 0 else 0
        return score_percentage, correct_answers, total_questions
    
    @classmethod
    def get_by_module(cls, module_id):
        """Get quiz for a specific module"""
        return cls.query.filter_by(module_id=module_id, is_active=True).first()


class QuestionV2(db.Model):
    """Quiz question model"""
    __tablename__ = 'questions_v2'
    
    id = db.Column(db.Integer, primary_key=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quizzes_v2.id'), nullable=False)
    
    # Question content
    content = db.Column(db.Text, nullable=False)
    explanation = db.Column(db.Text)  # Explanation for the correct answer
    order = db.Column(db.Integer, nullable=False)
    
    # Question settings
    question_type = db.Column(db.String(20), default='multiple_choice')  # multiple_choice, true_false
    points = db.Column(db.Integer, default=1)
    
    # Metadata
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    choices = db.relationship(
        'ChoiceV2',
        backref='question',
        cascade='all, delete-orphan',
        order_by='ChoiceV2.order'
    )
    
    # Indexes
    __table_args__ = (
        Index('idx_question_quiz_order', 'quiz_id', 'order'),
        Index('idx_question_active', 'is_active'),
    )
    
    def __repr__(self):
        return f'<QuestionV2 {self.id}: {self.content[:50]}...>'
    
    def to_dict(self, include_choices=False, include_correct_answer=False):
        """Convert question to dictionary"""
        data = {
            'id': self.id,
            'quiz_id': self.quiz_id,
            'content': self.content,
            'explanation': self.explanation,
            'order': self.order,
            'question_type': self.question_type,
            'points': self.points,
            'is_active': self.is_active
        }
        
        if include_choices:
            data['choices'] = [c.to_dict(include_correct=include_correct_answer) for c in self.choices]
        
        return data
    
    def get_correct_choice(self):
        """Get the correct choice for this question"""
        return next((choice for choice in self.choices if choice.is_correct), None)
    
    def get_choices_for_display(self):
        """Get choices for display (randomized if needed)"""
        choices = list(self.choices)
        # Could add randomization logic here if needed
        return choices


class ChoiceV2(db.Model):
    """Answer choice model"""
    __tablename__ = 'choices_v2'
    
    id = db.Column(db.Integer, primary_key=True)
    question_id = db.Column(db.Integer, db.ForeignKey('questions_v2.id'), nullable=False)
    
    # Choice content
    content = db.Column(db.Text, nullable=False)
    order = db.Column(db.Integer, nullable=False)
    
    # Choice properties
    is_correct = db.Column(db.Boolean, default=False)
    
    # Metadata
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Indexes
    __table_args__ = (
        Index('idx_choice_question_order', 'question_id', 'order'),
        Index('idx_choice_correct', 'question_id', 'is_correct'),
    )
    
    def __repr__(self):
        return f'<ChoiceV2 {self.id}: {self.content[:30]}...>'
    
    def to_dict(self, include_correct=False):
        """Convert choice to dictionary"""
        data = {
            'id': self.id,
            'question_id': self.question_id,
            'content': self.content,
            'order': self.order,
            'is_active': self.is_active
        }
        
        if include_correct:
            data['is_correct'] = self.is_correct
        
        return data


class QuizAttemptV2(db.Model):
    """Quiz attempt tracking"""
    __tablename__ = 'quiz_attempts_v2'
    
    id = db.Column(db.Integer, primary_key=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quizzes_v2.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # Attempt data
    attempt_number = db.Column(db.Integer, nullable=False)
    answers = db.Column(db.JSON)  # Store user answers as JSON
    
    # Results
    score = db.Column(db.Integer)  # 0-100
    correct_answers = db.Column(db.Integer)
    total_questions = db.Column(db.Integer)
    passed = db.Column(db.Boolean, default=False)
    
    # Timing
    started_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)
    time_taken = db.Column(db.Integer)  # in seconds
    
    # Status
    status = db.Column(db.String(20), default='in_progress')  # in_progress, completed, abandoned
    
    # Relationships
    user = db.relationship('User', backref='quiz_attempts_v2')
    
    # Constraints
    __table_args__ = (
        Index('idx_attempt_user_quiz', 'user_id', 'quiz_id', 'attempt_number'),
        Index('idx_attempt_status', 'status'),
        db.CheckConstraint('score >= 0 AND score <= 100', name='valid_score'),
    )
    
    def __repr__(self):
        return f'<QuizAttemptV2 User:{self.user_id} Quiz:{self.quiz_id} Attempt:{self.attempt_number}>'
    
    def to_dict(self):
        """Convert attempt to dictionary"""
        return {
            'id': self.id,
            'quiz_id': self.quiz_id,
            'user_id': self.user_id,
            'attempt_number': self.attempt_number,
            'score': self.score,
            'correct_answers': self.correct_answers,
            'total_questions': self.total_questions,
            'passed': self.passed,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'time_taken': self.time_taken,
            'status': self.status
        }
    
    def complete_attempt(self, answers):
        """Complete the quiz attempt"""
        self.answers = answers
        self.completed_at = datetime.utcnow()
        self.status = 'completed'
        
        # Calculate time taken
        if self.started_at:
            time_diff = self.completed_at - self.started_at
            self.time_taken = int(time_diff.total_seconds())
        
        # Calculate score
        if self.quiz:
            score, correct, total = self.quiz.calculate_score(answers)
            self.score = int(score)
            self.correct_answers = correct
            self.total_questions = total
            self.passed = score >= self.quiz.passing_score
    
    def abandon_attempt(self):
        """Mark attempt as abandoned"""
        self.status = 'abandoned'
        self.completed_at = datetime.utcnow()
    
    @classmethod
    def get_user_attempts(cls, user_id, quiz_id):
        """Get all attempts for a user and quiz"""
        return cls.query.filter_by(
            user_id=user_id,
            quiz_id=quiz_id
        ).order_by(cls.attempt_number).all()
    
    @classmethod
    def get_latest_attempt(cls, user_id, quiz_id):
        """Get the latest attempt for a user and quiz"""
        return cls.query.filter_by(
            user_id=user_id,
            quiz_id=quiz_id
        ).order_by(cls.attempt_number.desc()).first()
    
    @classmethod
    def get_best_attempt(cls, user_id, quiz_id):
        """Get the best scoring attempt for a user and quiz"""
        return cls.query.filter_by(
            user_id=user_id,
            quiz_id=quiz_id,
            status='completed'
        ).order_by(cls.score.desc()).first()
    
    @classmethod
    def create_new_attempt(cls, user_id, quiz_id):
        """Create a new quiz attempt"""
        # Get the next attempt number
        last_attempt = cls.query.filter_by(
            user_id=user_id,
            quiz_id=quiz_id
        ).order_by(cls.attempt_number.desc()).first()
        
        attempt_number = (last_attempt.attempt_number + 1) if last_attempt else 1
        
        # Create new attempt
        attempt = cls(
            user_id=user_id,
            quiz_id=quiz_id,
            attempt_number=attempt_number
        )
        
        db.session.add(attempt)
        return attempt


class QuizAnalyticsV2(db.Model):
    """Quiz analytics and statistics"""
    __tablename__ = 'quiz_analytics_v2'
    
    id = db.Column(db.Integer, primary_key=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quizzes_v2.id'), nullable=False)
    
    # Analytics data
    total_attempts = db.Column(db.Integer, default=0)
    total_completions = db.Column(db.Integer, default=0)
    total_passes = db.Column(db.Integer, default=0)
    
    # Score statistics
    average_score = db.Column(db.Float)
    highest_score = db.Column(db.Integer)
    lowest_score = db.Column(db.Integer)
    
    # Time statistics
    average_time = db.Column(db.Integer)  # in seconds
    
    # Question analytics (stored as JSON)
    question_stats = db.Column(db.JSON)  # Per-question statistics
    
    # Last updated
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    quiz = db.relationship('QuizV2', backref='analytics')
    
    def __repr__(self):
        return f'<QuizAnalyticsV2 Quiz:{self.quiz_id}>'
    
    def to_dict(self):
        """Convert analytics to dictionary"""
        return {
            'quiz_id': self.quiz_id,
            'total_attempts': self.total_attempts,
            'total_completions': self.total_completions,
            'total_passes': self.total_passes,
            'completion_rate': (self.total_completions / self.total_attempts * 100) if self.total_attempts > 0 else 0,
            'pass_rate': (self.total_passes / self.total_completions * 100) if self.total_completions > 0 else 0,
            'average_score': self.average_score,
            'highest_score': self.highest_score,
            'lowest_score': self.lowest_score,
            'average_time': self.average_time,
            'question_stats': self.question_stats,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    @classmethod
    def update_quiz_analytics(cls, quiz_id):
        """Update analytics for a quiz"""
        # Get or create analytics record
        analytics = cls.query.filter_by(quiz_id=quiz_id).first()
        if not analytics:
            analytics = cls(quiz_id=quiz_id)
            db.session.add(analytics)
        
        # Get all completed attempts for this quiz
        completed_attempts = QuizAttemptV2.query.filter_by(
            quiz_id=quiz_id,
            status='completed'
        ).all()
        
        if completed_attempts:
            # Calculate basic statistics
            analytics.total_attempts = len(completed_attempts)
            analytics.total_completions = len(completed_attempts)
            analytics.total_passes = len([a for a in completed_attempts if a.passed])
            
            # Score statistics
            scores = [a.score for a in completed_attempts if a.score is not None]
            if scores:
                analytics.average_score = sum(scores) / len(scores)
                analytics.highest_score = max(scores)
                analytics.lowest_score = min(scores)
            
            # Time statistics
            times = [a.time_taken for a in completed_attempts if a.time_taken is not None]
            if times:
                analytics.average_time = sum(times) / len(times)
            
            # Question-level analytics
            analytics.question_stats = cls._calculate_question_stats(completed_attempts)
        
        analytics.updated_at = datetime.utcnow()
        return analytics
    
    @staticmethod
    def _calculate_question_stats(attempts):
        """Calculate per-question statistics"""
        question_stats = {}
        
        for attempt in attempts:
            if attempt.answers:
                for question_id, choice_id in attempt.answers.items():
                    if question_id not in question_stats:
                        question_stats[question_id] = {
                            'total_answers': 0,
                            'correct_answers': 0,
                            'choice_distribution': {}
                        }
                    
                    stats = question_stats[question_id]
                    stats['total_answers'] += 1
                    
                    # Track choice distribution
                    if choice_id not in stats['choice_distribution']:
                        stats['choice_distribution'][choice_id] = 0
                    stats['choice_distribution'][choice_id] += 1
                    
                    # Check if answer was correct
                    # This would need to be implemented based on the question/choice data
                    # For now, we'll leave this as a placeholder
        
        # Calculate percentages
        for question_id, stats in question_stats.items():
            if stats['total_answers'] > 0:
                stats['correct_percentage'] = (stats['correct_answers'] / stats['total_answers']) * 100
        
        return question_stats