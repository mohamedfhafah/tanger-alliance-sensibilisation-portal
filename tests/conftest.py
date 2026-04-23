#!/usr/bin/env python
"""
Configuration et fixtures pytest pour le portail de sécurité Tanger Alliance.

Ce module fournit les fixtures et configurations communes pour tous les tests.
"""

import pytest
import os
import tempfile
from datetime import datetime
from app import create_app, db
from app.models.user import User
from app.models.module import Module, UserProgress, Quiz, Question, Choice
from app.models.simulation import SimulationAttempt
from app.models.simulation_rating import SimulationRating
from app.models.badge import Badge, user_badge_association
from app.models.campaign import Campaign, PhishingSimulation

TEST_SECRET_KEY = 'test-secret-key-for-ci'
TEST_USER_PASSWORD = 'TestPassword2026!'
TEST_REGISTRATION_PASSWORD = 'SecureSignup2026!'
TEST_UPDATED_PASSWORD = 'UpdatedPassword2026!'


@pytest.fixture(scope='session')
def app():
    """Créer l'application Flask pour les tests."""
    # Configuration de test en mémoire
    db_fd, db_path = tempfile.mkstemp()
    
    app = create_app('testing')
    app.config.update({
        'TESTING': True,
        'LOGIN_DISABLED': False,
        'WTF_CSRF_ENABLED': False,
        'SQLALCHEMY_DATABASE_URI': f'sqlite:///{db_path}',
        'SECRET_KEY': TEST_SECRET_KEY,
        'MAIL_SUPPRESS_SEND': True,
        'SERVER_NAME': 'localhost.localdomain'
    })
    
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()
    
    os.close(db_fd)
    os.unlink(db_path)


@pytest.fixture(scope='function')
def client(app):
    """Client de test Flask."""
    return app.test_client()


@pytest.fixture(scope='function')
def app_context(app):
    """Contexte d'application Flask."""
    with app.app_context():
        yield app


@pytest.fixture(scope='function')
def db_session(app_context):
    """Session de base de données pour les tests."""
    # Clean up any existing data
    db.session.remove()
    db.drop_all()
    db.create_all()
    
    yield db.session
    
    # Clean up after test
    db.session.rollback()
    db.session.remove()


@pytest.fixture
def test_user(db_session):
    """Utilisateur de test standard."""
    user = User(
        email='test@example.com',
        firstname='Test',
        lastname='User',
        role='user',
        department='IT',
        created_at=datetime.now()
    )
    user.set_password(TEST_USER_PASSWORD)
    db_session.add(user)
    db_session.commit()
    return user


@pytest.fixture
def admin_user(db_session):
    """Utilisateur administrateur de test."""
    admin = User(
        email='admin@example.com',
        firstname='Admin',
        lastname='User',
        role='admin',
        department='Security',
        created_at=datetime.now()
    )
    admin.set_password(TEST_USER_PASSWORD)
    db_session.add(admin)
    db_session.commit()
    return admin


@pytest.fixture
def test_module(db_session):
    """Module d'apprentissage de test."""
    module = Module(
        title='Test Module',
        description='Description du module de test',
        content='Contenu du module de test pour l\'apprentissage cybersécurité',
        order=1,
        image='test_module.jpg',
        is_active=True,
        created_at=datetime.now()
    )
    db_session.add(module)
    db_session.commit()
    return module


@pytest.fixture
def test_quiz(db_session, test_module):
    """Quiz de test associé à un module."""
    quiz = Quiz(
        module_id=test_module.id,
        title='Quiz de test',
        description='Description du quiz de test',
        passing_score=70
    )
    db_session.add(quiz)
    db_session.commit()
    return quiz


@pytest.fixture
def test_questions(db_session, test_quiz):
    """Questions de test pour un quiz."""
    questions = []
    for i in range(3):
        question = Question(
            quiz_id=test_quiz.id,
            content=f'Question {i+1} du quiz de test ?',
            explanation=f'Explication pour la question {i+1}'
        )
        db_session.add(question)
        questions.append(question)
    
    db_session.commit()

    for question in questions:
        db_session.add_all([
            Choice(question_id=question.id, content='Option A', is_correct=True),
            Choice(question_id=question.id, content='Option B', is_correct=False),
            Choice(question_id=question.id, content='Option C', is_correct=False),
        ])

    db_session.commit()
    return questions


@pytest.fixture
def test_campaign(db_session):
    """Campagne de test."""
    campaign = Campaign(
        name='Test Campaign',
        type='Phishing Email',
        description='Campagne de test pour simulation de phishing',
        start_date=datetime.now(),
        status='active'
    )
    db_session.add(campaign)
    db_session.commit()
    return campaign


@pytest.fixture
def test_simulation(db_session, test_campaign):
    """Simulation de phishing de test."""
    simulation = PhishingSimulation(
        campaign_id=test_campaign.id,
        title='Test Phishing Simulation',
        template='phishing_template_1',
        description='Simulation de test pour détecter les tentatives de phishing',
        created_at=datetime.now()
    )
    db_session.add(simulation)
    db_session.commit()
    return simulation


@pytest.fixture
def test_badge(db_session, test_module):
    """Badge de test."""
    badge = Badge(
        name='Test Badge',
        description='Badge de test pour les achievements',
        image_filename='test-badge.png',
        module_id=test_module.id
    )
    db_session.add(badge)
    db_session.commit()
    return badge


@pytest.fixture
def authenticated_client(client, test_user):
    """Client authentifié avec un utilisateur de test."""
    with client.session_transaction() as sess:
        sess['_user_id'] = str(test_user.id)
        sess['_fresh'] = True
    return client


@pytest.fixture
def admin_client(client, admin_user):
    """Client authentifié avec un utilisateur administrateur."""
    with client.session_transaction() as sess:
        sess['_user_id'] = str(admin_user.id)
        sess['_fresh'] = True
    return client


class TestDataFactory:
    """Factory pour créer des données de test."""
    _counter = 0
    
    @staticmethod
    def create_user(email=None, role='user', **kwargs):
        """Créer un utilisateur de test."""
        if email is None:
            TestDataFactory._counter += 1
            email = f'test{TestDataFactory._counter}@example.com'
        
        defaults = {
            'firstname': 'Test',
            'lastname': 'User',
            'department': 'it',
            'created_at': datetime.now()
        }
        defaults.update(kwargs)

        user = User(email=email, role=role, **defaults)
        user.set_password(TEST_USER_PASSWORD)
        return user
    
    @staticmethod
    def create_module(title='Test Module', order=1, **kwargs):
        """Créer un module de test."""
        defaults = {
            'description': 'Description du module de test',
            'content': 'Contenu du module de test',
            'image': 'test_module.jpg',
            'is_active': True,
            'created_at': datetime.now()
        }
        defaults.update(kwargs)

        return Module(title=title, order=order, **defaults)
    
    @staticmethod
    def create_progress(user_id, module_id, completed=False, **kwargs):
        """Créer une progression utilisateur."""
        defaults = {
            'started_at': datetime.now(),
            'score': None
        }
        defaults.update(kwargs)
        
        return UserProgress(
            user_id=user_id,
            module_id=module_id,
            completed=completed,
            **defaults
        )
    
    @staticmethod
    def create_campaign(name='Test Campaign', campaign_type='Phishing Email', **kwargs):
        """Créer une campagne de test."""
        defaults = {
            'description': 'Campagne de test pour simulation de phishing',
            'start_date': datetime.now(),
            'status': 'active'
        }
        defaults.update(kwargs)
        
        return Campaign(name=name, type=campaign_type, **defaults)


# Utilitaires de test
class TestUtils:
    """Utilitaires pour les tests."""
    
    @staticmethod
    def login_user(client, email='test@example.com', password=TEST_USER_PASSWORD):
        """Connecter un utilisateur via le client de test."""
        return client.post('/auth/login', data={
            'email': email,
            'password': password
        }, follow_redirects=True)
    
    @staticmethod
    def logout_user(client):
        """Déconnecter l'utilisateur."""
        return client.get('/auth/logout', follow_redirects=True)
    
    @staticmethod
    def assert_flash_message(response, message_text, category='success'):
        """Vérifier qu'un message flash est présent."""
        assert message_text.encode() in response.data
    
    @staticmethod
    def assert_redirects_to(response, endpoint):
        """Vérifier qu'une réponse redirige vers un endpoint."""
        assert response.status_code in [301, 302]
        assert endpoint in response.location
