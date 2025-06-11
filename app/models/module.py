from app import db
from datetime import datetime, timezone

class Module(db.Model):
    """Modèle pour les modules d'apprentissage"""
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    content = db.Column(db.Text, nullable=False)
    order = db.Column(db.Integer, nullable=False)
    image = db.Column(db.String(100), nullable=True, default='default_module.jpg')
    created_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    is_active = db.Column(db.Boolean, default=True)
    
    # Relationships
    quizzes = db.relationship('Quiz', backref='module', lazy=True)
    
    def __repr__(self):
        return f"Module('{self.title}', order={self.order})"


class UserProgress(db.Model):
    """Modèle pour suivre la progression des utilisateurs"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    module_id = db.Column(db.Integer, db.ForeignKey('module.id'), nullable=False)
    completed = db.Column(db.Boolean, default=False)
    started_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    completed_at = db.Column(db.DateTime, nullable=True)
    score = db.Column(db.Integer, nullable=True)
    
    def __repr__(self):
        return f"UserProgress(user_id={self.user_id}, module_id={self.module_id}, completed={self.completed})"


class QuizProgress(db.Model):
    """Modèle pour suivre la progression des utilisateurs sur les quiz individuels"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id'), nullable=False)
    completed = db.Column(db.Boolean, default=False)
    started_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    completed_at = db.Column(db.DateTime, nullable=True)
    score = db.Column(db.Integer, nullable=True)
    attempts = db.Column(db.Integer, default=0)
    
    # Unique constraint to prevent duplicate records
    __table_args__ = (db.UniqueConstraint('user_id', 'quiz_id'),)
    
    def __repr__(self):
        return f"QuizProgress(user_id={self.user_id}, quiz_id={self.quiz_id}, completed={self.completed}, score={self.score})"


class Quiz(db.Model):
    """Modèle pour les quiz associés aux modules"""
    id = db.Column(db.Integer, primary_key=True)
    module_id = db.Column(db.Integer, db.ForeignKey('module.id'), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    passing_score = db.Column(db.Integer, default=70)  # Percentage required to pass
    difficulty_level = db.Column(db.String(20), default='beginner')  # beginner, intermediate, advanced
    order = db.Column(db.Integer, default=1)  # Order within the module
    prerequisite_quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id'), nullable=True)  # Required quiz to complete first
    is_active = db.Column(db.Boolean, default=True)
    
    # Relationships
    questions = db.relationship('Question', backref='quiz', lazy=True, cascade="all, delete-orphan")
    prerequisite_quiz = db.relationship('Quiz', remote_side=[id], backref='dependent_quizzes')
    
    def __repr__(self):
        return f"Quiz('{self.title}', module_id={self.module_id}, difficulty='{self.difficulty_level}')"
    
    def is_unlocked_for_user(self, user_id):
        """Check if this quiz is unlocked for a specific user"""
        if not self.prerequisite_quiz_id:
            return True  # No prerequisite, always unlocked
        
        # Check if prerequisite quiz is completed with passing score
        quiz_progress = QuizProgress.query.filter_by(
            user_id=user_id,
            quiz_id=self.prerequisite_quiz_id
        ).first()
        
        return (quiz_progress and 
                quiz_progress.completed and 
                quiz_progress.score is not None and
                quiz_progress.score >= self.prerequisite_quiz.passing_score)


class Question(db.Model):
    """Modèle pour les questions de quiz"""
    id = db.Column(db.Integer, primary_key=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    explanation = db.Column(db.Text, nullable=True)
    type = db.Column(db.String(20), default='multiple_choice')  # multiple_choice, true_false, open_ended
    
    # Relationships
    choices = db.relationship('Choice', backref='question', lazy=True, cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"Question(id={self.id}, quiz_id={self.quiz_id})"


class Choice(db.Model):
    """Modèle pour les choix de réponses aux questions"""
    id = db.Column(db.Integer, primary_key=True)
    question_id = db.Column(db.Integer, db.ForeignKey('question.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    is_correct = db.Column(db.Boolean, default=False)
    
    def __repr__(self):
        return f"Choice(id={self.id}, question_id={self.question_id}, is_correct={self.is_correct})"
