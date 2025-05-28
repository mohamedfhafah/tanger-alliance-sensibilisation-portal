from app import db
from datetime import datetime

class Module(db.Model):
    """Modèle pour les modules d'apprentissage"""
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    content = db.Column(db.Text, nullable=False)
    order = db.Column(db.Integer, nullable=False)
    image = db.Column(db.String(100), nullable=True, default='default_module.jpg')
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
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
    started_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime, nullable=True)
    score = db.Column(db.Integer, nullable=True)
    
    def __repr__(self):
        return f"UserProgress(user_id={self.user_id}, module_id={self.module_id}, completed={self.completed})"


class Quiz(db.Model):
    """Modèle pour les quiz associés aux modules"""
    id = db.Column(db.Integer, primary_key=True)
    module_id = db.Column(db.Integer, db.ForeignKey('module.id'), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    passing_score = db.Column(db.Integer, default=70)  # Percentage required to pass
    
    # Relationships
    questions = db.relationship('Question', backref='quiz', lazy=True, cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"Quiz('{self.title}', module_id={self.module_id})"


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
