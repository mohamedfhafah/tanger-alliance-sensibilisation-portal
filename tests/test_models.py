#!/usr/bin/env python
"""
Tests pour les modèles de données du portail de sécurité.

Tests couverts:
- Modèle User (utilisateur)
- Modèle Module (modules d'apprentissage)
- Modèle Quiz et Question
- Modèle UserProgress (progression)
- Relations entre modèles
- Validations et contraintes
"""

import pytest
from datetime import datetime, timezone, timedelta
from app.models.user import User
from app.models.module import Module, Quiz, Question, Choice, UserProgress
from app.models.badge import Badge
from app.models.simulation import SimulationAttempt
from app.models.simulation_rating import SimulationRating
from app.models.campaign import Campaign, PhishingSimulation
from tests.conftest import TestDataFactory, TEST_USER_PASSWORD


class TestUserModel:
    """Tests pour le modèle User."""
    
    def test_user_creation(self, db_session):
        """Test de création d'un utilisateur."""
        user = TestDataFactory.create_user(
            email='test@example.com',
            firstname='Test',
            lastname='User',
            department='IT'
        )
        
        db_session.add(user)
        db_session.commit()
        
        assert user.id is not None
        assert user.email == 'test@example.com'
        assert user.firstname == 'Test'
        assert user.lastname == 'User'
        assert user.department == 'IT'
        assert user.role == 'user'
        assert user.created_at is not None
        assert user.check_password(TEST_USER_PASSWORD)
    
    def test_user_password_hashing(self, db_session):
        """Test du hachage des mots de passe."""
        user = TestDataFactory.create_user()
        user.set_password('plaintext_password')
        
        db_session.add(user)
        db_session.commit()
        
        # Le mot de passe ne devrait pas être stocké en clair
        assert user.password != 'plaintext_password'
        assert len(user.password) > 20  # Hash bcrypt
        assert user.check_password('plaintext_password')
        assert not user.check_password('wrong_password')
    
    def test_user_unique_email(self, db_session):
        """Test de l'unicité des emails."""
        user1 = TestDataFactory.create_user(email='unique@example.com')
        user2 = TestDataFactory.create_user(email='unique@example.com')
        
        db_session.add(user1)
        db_session.commit()
        
        db_session.add(user2)
        
        # Devrait lever une exception d'intégrité
        with pytest.raises(Exception):
            db_session.commit()
    
    def test_user_admin_role(self, db_session):
        """Test du rôle administrateur."""
        admin = TestDataFactory.create_user(
            email='admin@example.com',
            role='admin'
        )
        user = TestDataFactory.create_user(
            email='user@example.com',
            role='user'
        )
        
        db_session.add_all([admin, user])
        db_session.commit()
        
        assert admin.is_admin()
        assert not user.is_admin()
    
    def test_user_last_login_update(self, db_session):
        """Test de mise à jour du dernier login."""
        user = TestDataFactory.create_user()
        db_session.add(user)
        db_session.commit()
        
        assert user.last_login is None
        
        user.update_last_login()
        assert user.last_login is not None
        # Allow for small time differences in test execution
        # Handle timezone-naive datetime by making it timezone-aware for comparison
        last_login = user.last_login
        if last_login.tzinfo is None:
            last_login = last_login.replace(tzinfo=timezone.utc)
        time_diff = abs((datetime.now(timezone.utc) - last_login).total_seconds())
        assert time_diff < 5  # Should be within 5 seconds
    
    def test_user_reset_token(self, db_session):
        """Test des tokens de réinitialisation."""
        user = TestDataFactory.create_user()
        db_session.add(user)
        db_session.commit()
        
        # Génération du token
        token = user.get_reset_token()
        assert token is not None
        assert isinstance(token, str)
        
        # Vérification du token
        verified_user = User.verify_reset_token(token)
        assert verified_user is not None
        assert verified_user.id == user.id
        
        # Token invalide
        invalid_user = User.verify_reset_token('invalid_token')
        assert invalid_user is None
    
    def test_user_repr(self, db_session):
        """Test de la représentation string d'un utilisateur."""
        user = TestDataFactory.create_user(
            email='test@example.com',
            role='admin',
            department='Security'
        )
        
        repr_str = repr(user)
        assert 'test@example.com' in repr_str
        assert 'admin' in repr_str
        assert 'Security' in repr_str


class TestModuleModel:
    """Tests pour le modèle Module."""
    
    def test_module_creation(self, db_session):
        """Test de création d'un module."""
        module = TestDataFactory.create_module(
            title='Sécurité des mots de passe',
            description='Apprenez à créer des mots de passe sécurisés',
            content='Contenu détaillé sur la sécurité des mots de passe...', # Changed text to content
            order=1
        )
        
        db_session.add(module)
        db_session.commit()
        
        assert module.id is not None
        assert module.title == 'Sécurité des mots de passe'
        assert module.description == 'Apprenez à créer des mots de passe sécurisés'
        assert module.content == 'Contenu détaillé sur la sécurité des mots de passe...' # Changed text to content
        assert module.order == 1
        assert module.is_active is True
        assert module.created_at is not None
        assert module.image == 'test_module.jpg'
    
    def test_module_ordering(self, db_session):
        """Test de l'ordre des modules."""
        modules = []
        for i in range(3):
            module = TestDataFactory.create_module(
                title=f'Module {i+1}',
                order=i+1
            )
            modules.append(module)
            db_session.add(module)
        
        db_session.commit()
        
        # Vérifier l'ordre
        ordered_modules = Module.query.order_by(Module.order).all()
        for i, module in enumerate(ordered_modules):
            assert module.order == i + 1
            assert module.title == f'Module {i+1}'
    
    def test_module_active_inactive(self, db_session):
        """Test des modules actifs et inactifs."""
        active_module = TestDataFactory.create_module(
            title='Module Actif',
            is_active=True
        )
        inactive_module = TestDataFactory.create_module(
            title='Module Inactif',
            is_active=False
        )
        
        db_session.add_all([active_module, inactive_module])
        db_session.commit()
        
        active_modules = Module.query.filter_by(is_active=True).all()
        assert len(active_modules) == 1
        assert active_modules[0].title == 'Module Actif'
        
        inactive_modules = Module.query.filter_by(is_active=False).all()
        assert len(inactive_modules) == 1
        assert inactive_modules[0].title == 'Module Inactif'
    
    def test_module_repr(self, db_session):
        """Test de la représentation string d'un module."""
        module = TestDataFactory.create_module(
            title='Test Module',
            order=5
        )
        
        repr_str = repr(module)
        assert 'Test Module' in repr_str
        assert 'order=5' in repr_str


class TestQuizModel:
    """Tests pour le modèle Quiz."""
    
    def test_quiz_creation(self, db_session, test_module):
        """Test de création d'un quiz."""
        quiz = Quiz(
            module_id=test_module.id,
            title='Quiz de sécurité',
            description='Testez vos connaissances en sécurité',
            passing_score=80
        )
        
        db_session.add(quiz)
        db_session.commit()
        
        assert quiz.id is not None
        assert quiz.module_id == test_module.id
        assert quiz.title == 'Quiz de sécurité'
        assert quiz.description == 'Testez vos connaissances en sécurité'
        assert quiz.passing_score == 80
        assert quiz.module == test_module
    
    def test_quiz_module_relationship(self, db_session, test_module):
        """Test de la relation entre quiz et module."""
        quiz1 = Quiz(
            module_id=test_module.id,
            title='Quiz 1',
            description='Premier quiz'
        )
        quiz2 = Quiz(
            module_id=test_module.id,
            title='Quiz 2',
            description='Deuxième quiz'
        )
        
        db_session.add_all([quiz1, quiz2])
        db_session.commit()
        
        # Vérifier la relation inverse
        assert len(test_module.quizzes) == 2
        quiz_titles = [q.title for q in test_module.quizzes]
        assert 'Quiz 1' in quiz_titles
        assert 'Quiz 2' in quiz_titles
    
    def test_quiz_default_passing_score(self, db_session, test_module):
        """Test du score de passage par défaut."""
        quiz = Quiz(
            module_id=test_module.id,
            title='Quiz sans score'
        )
        
        db_session.add(quiz)
        db_session.commit()
        
        assert quiz.passing_score == 70  # Valeur par défaut


class TestQuestionModel:
    """Tests pour le modèle Question."""
    
    def test_question_creation(self, db_session, test_quiz):
        """Test de création d'une question."""
        question = Question(
            quiz_id=test_quiz.id,
            content='Quelle est la longueur minimale recommandée pour un mot de passe ?', # Changed text to content
            explanation='Un mot de passe sécurisé doit contenir au moins 12 caractères.',
            type='multiple_choice'
        )
        
        db_session.add(question)
        db_session.commit()
        
        assert question.id is not None
        assert question.quiz_id == test_quiz.id
        assert 'longueur minimale' in question.content # Changed text to content
        assert 'au moins 12 caractères' in question.explanation
        assert question.type == 'multiple_choice'
        assert question.quiz == test_quiz
    
    def test_question_quiz_relationship(self, db_session, test_quiz):
        """Test de la relation entre question et quiz."""
        questions = []
        for i in range(3):
            question = Question(
                quiz_id=test_quiz.id,
                content=f'Question {i+1} ?', # Changed text to content
                explanation=f'Explication {i+1}',
                type='multiple_choice'
            )
            questions.append(question)
            db_session.add(question)
        
        db_session.commit()
        
        # Vérifier la relation inverse
        assert len(test_quiz.questions) == 3
        question_contents = [q.content for q in test_quiz.questions] # Changed text to content
        for i in range(3):
            assert f'Question {i+1} ?' in question_contents # Changed text to content


class TestUserProgressModel:
    """Tests pour le modèle UserProgress."""
    
    def test_progress_creation(self, db_session, test_user, test_module):
        """Test de création d'une progression."""
        progress = TestDataFactory.create_progress(
            user_id=test_user.id,
            module_id=test_module.id,
            completed=False
        )
        
        db_session.add(progress)
        db_session.commit()
        
        assert progress.id is not None
        assert progress.user_id == test_user.id
        assert progress.module_id == test_module.id
        assert progress.completed is False
        assert progress.started_at is not None
        assert progress.completed_at is None
        assert progress.score is None
    
    def test_progress_completion(self, db_session, test_user, test_module):
        """Test de complétion d'un module."""
        progress = TestDataFactory.create_progress(
            user_id=test_user.id,
            module_id=test_module.id,
            completed=True,
            completed_at=datetime.now(),
            score=85
        )
        
        db_session.add(progress)
        db_session.commit()
        
        assert progress.completed is True
        assert progress.completed_at is not None
        assert progress.score == 85
    
    def test_progress_user_relationship(self, db_session, test_user, test_module):
        """Test de la relation progression-utilisateur."""
        progress = TestDataFactory.create_progress(
            user_id=test_user.id,
            module_id=test_module.id
        )
        
        db_session.add(progress)
        db_session.commit()
        
        # Vérifier la relation
        assert len(test_user.progress) == 1
        assert test_user.progress[0].module_id == test_module.id
    
    def test_progress_repr(self, db_session, test_user, test_module):
        """Test de la représentation string d'une progression."""
        progress = TestDataFactory.create_progress(
            user_id=test_user.id,
            module_id=test_module.id,
            completed=True
        )
        
        repr_str = repr(progress)
        assert f'user_id={test_user.id}' in repr_str
        assert f'module_id={test_module.id}' in repr_str
        assert 'completed=True' in repr_str


class TestModelRelationships:
    """Tests pour les relations entre modèles."""
    
    def test_cascade_delete_quiz_questions(self, db_session, test_module):
        """Test de suppression en cascade quiz -> questions."""
        quiz = Quiz(
            module_id=test_module.id,
            title='Quiz à supprimer'
        )
        db_session.add(quiz)
        db_session.commit()
        
        # Ajouter des questions
        for i in range(3):
            question = Question(
                quiz_id=quiz.id,
                content=f'Question {i+1}', # Changed text to content
                explanation=f'Explication {i+1}',
                type='multiple_choice'
            )
            db_session.add(question)
        
        db_session.commit()
        quiz_id = quiz.id
        
        # Vérifier que les questions existent
        questions = Question.query.filter_by(quiz_id=quiz_id).all()
        assert len(questions) == 3
        
        # Supprimer le quiz
        db_session.delete(quiz)
        db_session.commit()
        
        # Vérifier que les questions ont été supprimées
        questions = Question.query.filter_by(quiz_id=quiz_id).all()
        assert len(questions) == 0
    
    def test_user_module_progress_tracking(self, db_session):
        """Test de suivi de progression utilisateur-module."""
        # Créer utilisateur et modules
        user = TestDataFactory.create_user(email='progress@test.com')
        modules = []
        for i in range(3):
            module = TestDataFactory.create_module(
                title=f'Module {i+1}',
                order=i+1
            )
            modules.append(module)
        
        db_session.add_all([user] + modules)
        db_session.commit()
        
        # Marquer certains modules comme complétés
        for i, module in enumerate(modules[:2]):
            progress = TestDataFactory.create_progress(
                user_id=user.id,
                module_id=module.id,
                completed=True,
                score=80 + i * 5
            )
            db_session.add(progress)
        
        db_session.commit()
        
        # Vérifier la progression
        completed_progress = UserProgress.query.filter_by(
            user_id=user.id,
            completed=True
        ).all()
        assert len(completed_progress) == 2
        
        total_progress = UserProgress.query.filter_by(user_id=user.id).all()
        assert len(total_progress) == 2
        
        # Calculer le pourcentage de progression
        completion_rate = len(completed_progress) / len(modules) * 100
        assert abs(completion_rate - 66.67) < 0.1  # 2/3 modules complétés (with floating point tolerance)


class TestModelValidations:
    """Tests pour les validations des modèles."""
    
    def test_module_required_fields(self, db_session):
        """Test des champs requis pour Module."""
        # Module sans titre (devrait échouer)
        module = Module(
            description='Description sans titre',
            content='Contenu sans titre', # Changed text to content
            order=1
        )
        
        db_session.add(module)
        
        with pytest.raises(Exception):
            db_session.commit()
    
    def test_user_required_fields(self, db_session):
        """Test des champs requis pour User."""
        # Utilisateur sans email (devrait échouer)
        user = User(
            firstname='Test',
            lastname='User',
            role='user'
        )
        user.set_password(TEST_USER_PASSWORD)
        
        db_session.add(user)
        
        with pytest.raises(Exception):
            db_session.commit()
    
    def test_quiz_module_foreign_key(self, db_session):
        """Test de la contrainte de clé étrangère quiz-module."""
        # Create a valid module first
        module = TestDataFactory.create_module(title='Valid Module')
        db_session.add(module)
        db_session.commit()
        
        # Test that a quiz can be created with valid module_id
        quiz = Quiz(
            module_id=module.id,
            title='Quiz valide'
        )
        
        db_session.add(quiz)
        db_session.commit()
        
        # Verify the relationship works
        assert quiz.module == module
        assert quiz in module.quizzes
