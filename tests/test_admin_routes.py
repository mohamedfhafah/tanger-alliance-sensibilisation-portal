#!/usr/bin/env python
"""
Tests pour les routes d'administration du portail de sécurité.

Tests couverts:
- Interface d'administration
- Gestion des utilisateurs
- Gestion des modules
- Gestion des quiz et questions
- Contrôle d'accès administrateur
- Statistiques et rapports
"""

import pytest
from datetime import datetime, timedelta
from flask import url_for
from app.models.user import User
from app.models.module import Module, Quiz, Question, UserProgress
from app.models.badge import Badge
from tests.conftest import TestUtils, TestDataFactory


class TestAdminAccess:
    """Tests pour le contrôle d'accès administrateur."""
    
    def test_admin_login_required(self, client):
        """Test que l'accès admin nécessite une connexion."""
        response = client.get('/admin/')
        # Devrait rediriger vers la page de connexion
        assert response.status_code == 302
        assert '/auth/login' in response.location
    
    def test_admin_role_required(self, authenticated_client):
        """Test que l'accès admin nécessite le rôle administrateur."""
        response = authenticated_client.get('/admin/')
        # Utilisateur normal ne devrait pas avoir accès
        assert response.status_code in [302, 403]
    
    def test_admin_access_granted(self, admin_client):
        """Test d'accès accordé pour un administrateur."""
        response = admin_client.get('/admin/')
        # Administrateur devrait avoir accès
        assert response.status_code in [200, 302]  # 302 si redirection vers dashboard
    
    def test_admin_dashboard(self, admin_client):
        """Test du tableau de bord administrateur."""
        response = admin_client.get('/admin/dashboard')
        assert response.status_code == 200
        assert 'Administration'.encode() in response.data or 'Admin'.encode() in response.data


class TestUserManagement:
    """Tests pour la gestion des utilisateurs."""
    
    def test_admin_users_list(self, admin_client, db_session):
        """Test de la liste des utilisateurs en admin."""
        # Créer quelques utilisateurs test
        users = []
        for i in range(3):
            user = TestDataFactory.create_user(
                email=f'user{i+1}@example.com',
                firstname=f'User{i+1}',
                lastname='Test'
            )
            users.append(user)
            db_session.add(user)
        
        db_session.commit()
        
        response = admin_client.get('/admin/users')
        assert response.status_code == 200
        
        # Vérifier que tous les utilisateurs apparaissent
        for user in users:
            assert user.email.encode() in response.data
    
    def test_admin_user_detail(self, admin_client, test_user):
        """Test de la page de détail d'un utilisateur."""
        response = admin_client.get(f'/admin/users/{test_user.id}')
        assert response.status_code == 200
        assert test_user.email.encode() in response.data
        assert test_user.firstname.encode() in response.data
    
    def test_admin_user_edit(self, admin_client, test_user, db_session):
        """Test de modification d'un utilisateur par l'admin."""
        response = admin_client.post(f'/admin/users/{test_user.id}/edit', data={
            'email': test_user.email,
            'firstname': 'Modified',
            'lastname': 'User',
            'role': 'admin',
            'department': 'Security'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        
        # Vérifier les modifications
        db_session.refresh(test_user)
        assert test_user.firstname == 'Modified'
        assert test_user.role == 'admin'
        assert test_user.department == 'Security'
    
    def test_admin_user_delete(self, admin_client, db_session):
        """Test de suppression d'un utilisateur."""
        # Créer un utilisateur à supprimer
        user_to_delete = TestDataFactory.create_user(email='delete@example.com')
        db_session.add(user_to_delete)
        db_session.commit()
        user_id = user_to_delete.id
        
        response = admin_client.post(f'/admin/users/{user_id}/delete', follow_redirects=True)
        assert response.status_code == 200
        
        # Vérifier que l'utilisateur a été supprimé
        deleted_user = db_session.get(User, user_id)
        assert deleted_user is None
    
    def test_admin_user_role_change(self, admin_client, test_user, db_session):
        """Test de changement de rôle utilisateur."""
        assert test_user.role == 'user'
        
        response = admin_client.post(f'/admin/users/{test_user.id}/role', data={
            'role': 'admin'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        
        db_session.refresh(test_user)
        assert test_user.role == 'admin'
        assert test_user.is_admin()
    
    def test_admin_users_search(self, admin_client, db_session):
        """Test de recherche d'utilisateurs."""
        # Créer des utilisateurs avec différents emails/noms
        users_data = [
            ('alice@example.com', 'Alice', 'Smith'),
            ('bob@example.com', 'Bob', 'Johnson'),
            ('charlie@example.com', 'Charlie', 'Brown')
        ]
        
        for email, firstname, lastname in users_data:
            user = TestDataFactory.create_user(
                email=email,
                firstname=firstname,
                lastname=lastname
            )
            db_session.add(user)
        
        db_session.commit()
        
        # Rechercher "alice"
        response = admin_client.get('/admin/users?search=alice')
        assert response.status_code == 200
        assert 'alice@example.com'.encode() in response.data
        assert 'bob@example.com'.encode() not in response.data


class TestModuleManagement:
    """Tests pour la gestion des modules."""
    
    def test_admin_modules_list(self, admin_client, db_session):
        """Test de la liste des modules en admin."""
        # Créer des modules test
        modules = []
        for i in range(3):
            module = TestDataFactory.create_module(
                title=f'Module Admin {i+1}',
                order=i+1
            )
            modules.append(module)
            db_session.add(module)
        
        db_session.commit()
        
        response = admin_client.get('/admin/modules')
        assert response.status_code == 200
        
        # Vérifier que tous les modules apparaissent
        for module in modules:
            assert module.title.encode() in response.data
    
    def test_admin_module_create(self, admin_client, db_session):
        """Test de création d'un nouveau module."""
        response = admin_client.post('/admin/modules/create', data={
            'title': 'Nouveau Module Admin',
            'description': 'Description du nouveau module',
            'content': 'Contenu détaillé du nouveau module',
            'order': 10,
            'is_active': True
        }, follow_redirects=True)
        
        assert response.status_code == 200
        
        # Vérifier que le module a été créé
        new_module = Module.query.filter_by(title='Nouveau Module Admin').first()
        assert new_module is not None
        assert new_module.description == 'Description du nouveau module'
        assert new_module.order == 10
        assert new_module.is_active is True
    
    def test_admin_module_edit(self, admin_client, test_module, db_session):
        """Test de modification d'un module."""
        response = admin_client.post(f'/admin/modules/{test_module.id}/edit', data={
            'title': 'Module Modifié',
            'description': 'Description modifiée',
            'content': test_module.content,
            'order': 5
            # is_active is not included, which means it should be False (unchecked checkbox)
        }, follow_redirects=True)
        
        assert response.status_code == 200
        
        # Vérifier les modifications
        db_session.refresh(test_module)
        assert test_module.title == 'Module Modifié'
        assert test_module.description == 'Description modifiée'
        assert test_module.order == 5
        assert test_module.is_active is False
    
    def test_admin_module_delete(self, admin_client, db_session):
        """Test de suppression d'un module."""
        # Créer un module à supprimer
        module_to_delete = TestDataFactory.create_module(title='Module à supprimer')
        db_session.add(module_to_delete)
        db_session.commit()
        module_id = module_to_delete.id
        
        response = admin_client.post(f'/admin/modules/{module_id}/delete', follow_redirects=True)
        assert response.status_code == 200
        
        # Vérifier que le module a été supprimé
        deleted_module = db_session.get(Module, module_id)
        assert deleted_module is None
    
    def test_admin_module_reorder(self, admin_client, db_session):
        """Test de réorganisation des modules."""
        # Créer plusieurs modules
        modules = []
        for i in range(3):
            module = TestDataFactory.create_module(
                title=f'Module {i+1}',
                order=i+1
            )
            modules.append(module)
            db_session.add(module)
        
        db_session.commit()
        
        # Réorganiser les modules
        new_order = {
            modules[0].id: 3,
            modules[1].id: 1,
            modules[2].id: 2
        }
        
        response = admin_client.post('/admin/modules/reorder', 
                                   json=new_order,
                                   content_type='application/json')
        assert response.status_code == 200
        
        # Vérifier le nouvel ordre
        for module in modules:
            db_session.refresh(module)
        
        assert modules[0].order == 3
        assert modules[1].order == 1
        assert modules[2].order == 2


class TestQuizManagement:
    """Tests pour la gestion des quiz."""
    
    def test_admin_quiz_create(self, admin_client, test_module, db_session):
        """Test de création d'un quiz."""
        response = admin_client.post('/admin/quiz/create', data={
            'module_id': test_module.id,
            'title': 'Quiz Admin Test',
            'description': 'Description du quiz admin',
            'passing_score': 80
        }, follow_redirects=True)
        
        assert response.status_code == 200
        
        # Vérifier que le quiz a été créé
        new_quiz = Quiz.query.filter_by(title='Quiz Admin Test').first()
        assert new_quiz is not None
        assert new_quiz.module_id == test_module.id
        assert new_quiz.passing_score == 80
    
    def test_admin_question_create(self, admin_client, test_quiz, db_session):
        """Test de création d'une question."""
        response = admin_client.post('/admin/questions/create', data={
            'quiz_id': test_quiz.id,
            'content': 'Question créée par admin ?',
            'explanation': 'Explication de la question admin'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        
        # Vérifier que la question a été créée
        new_question = Question.query.filter_by(content='Question créée par admin ?').first()
        assert new_question is not None
        assert new_question.quiz_id == test_quiz.id
    
    def test_admin_quiz_delete_cascade(self, admin_client, db_session, test_module):
        """Test de suppression en cascade quiz -> questions."""
        # Créer un quiz avec des questions
        quiz = Quiz(
            module_id=test_module.id,
            title='Quiz à supprimer'
        )
        db_session.add(quiz)
        db_session.commit()
        
        # Ajouter des questions
        questions = []
        for i in range(3):
            question = Question(
                quiz_id=quiz.id,
                content=f'Question {i+1} à supprimer ?',
                explanation=f'Explication {i+1}'
            )
            questions.append(question)
            db_session.add(question)
        
        db_session.commit()
        quiz_id = quiz.id
        
        # Supprimer le quiz
        response = admin_client.post(f'/admin/quiz/{quiz_id}/delete', follow_redirects=True)
        assert response.status_code == 200
        
        # Vérifier que le quiz et ses questions ont été supprimés
        deleted_quiz = db_session.get(Quiz, quiz_id)
        assert deleted_quiz is None
        
        remaining_questions = Question.query.filter_by(quiz_id=quiz_id).all()
        assert len(remaining_questions) == 0


class TestAdminStatistics:
    """Tests pour les statistiques administrateur."""
    
    def test_admin_dashboard_statistics(self, admin_client, db_session):
        """Test des statistiques sur le tableau de bord admin."""
        # Créer des données test
        users = []
        modules = []
        
        # Créer des utilisateurs
        for i in range(5):
            user = TestDataFactory.create_user(email=f'stats{i+1}@example.com')
            users.append(user)
            db_session.add(user)
        
        # Créer des modules
        for i in range(3):
            module = TestDataFactory.create_module(title=f'Stats Module {i+1}')
            modules.append(module)
            db_session.add(module)
        
        db_session.commit()
        
        # Créer des progressions
        for i, user in enumerate(users[:3]):
            for j, module in enumerate(modules[:2]):
                progress = TestDataFactory.create_progress(
                    user_id=user.id,
                    module_id=module.id,
                    completed=(i + j) % 2 == 0  # Alterner complété/non complété
                )
                db_session.add(progress)
        
        db_session.commit()
        
        response = admin_client.get('/admin/dashboard')
        assert response.status_code == 200
        
        # Vérifier que les statistiques apparaissent
        assert '5'.encode() in response.data  # Nombre d'utilisateurs
        assert '3'.encode() in response.data  # Nombre de modules
    
    def test_admin_user_progress_report(self, admin_client, db_session):
        """Test du rapport de progression des utilisateurs."""
        # Créer des données de progression
        user = TestDataFactory.create_user(email='progress@example.com')
        modules = []
        
        for i in range(3):
            module = TestDataFactory.create_module(title=f'Progress Module {i+1}')
            modules.append(module)
            db_session.add(module)
        
        db_session.add(user)
        db_session.commit()
        
        # Créer des progressions
        for i, module in enumerate(modules):
            progress = TestDataFactory.create_progress(
                user_id=user.id,
                module_id=module.id,
                completed=i < 2,  # 2 modules complétés sur 3
                score=80 + i * 5 if i < 2 else None
            )
            db_session.add(progress)
        
        db_session.commit()
        
        response = admin_client.get('/admin/reports/progress')
        assert response.status_code == 200
        
        # Vérifier le contenu du rapport
        assert user.email.encode() in response.data
        assert '66.7%'.encode() in response.data or '2/3'.encode() in response.data


class TestAdminSecurity:
    """Tests de sécurité pour l'administration."""
    
    def test_admin_csrf_protection(self, admin_client):
        """Test de protection CSRF sur les actions admin."""
        # Essayer de créer un module sans token CSRF
        response = admin_client.post('/admin/modules/create', data={
            'title': 'Module CSRF Test',
            'description': 'Test sans CSRF',
            'content': 'Contenu test',
            'order': 1
        })
        
        # Devrait être rejeté ou redirecté
        assert response.status_code in [400, 403, 302]
    
    def test_admin_sql_injection_protection(self, admin_client, db_session):
        """Test de protection contre l'injection SQL."""
        # Essayer une injection SQL dans la recherche
        response = admin_client.get("/admin/users?search='; DROP TABLE user; --")
        assert response.status_code == 200
        
        # Vérifier que les tables existent toujours
        users = User.query.all()
        # Ce test réussit si aucune exception n'est levée
    
    def test_admin_xss_protection(self, admin_client, db_session):
        """Test de protection contre XSS."""
        # Essayer d'injecter du JavaScript
        response = admin_client.post('/admin/modules/create', data={
            'title': '<script>alert("XSS")</script>',
            'description': 'Description normale',
            'content': 'Contenu normal',
            'order': 1
        }, follow_redirects=True)
        
        # Le script malveillant ne devrait pas apparaître non échappé
        # Vérifier que le script XSS spécifique est échappé
        assert b'<script>alert("XSS")</script>' not in response.data
        # S'assurer que le contenu est échappé (soit avec &lt; soit complètement absent)
        response_text = response.data.decode('utf-8')
        if 'alert("XSS")' in response_text:
            # Si le contenu est présent, il doit être échappé
            assert '&lt;script&gt;alert("XSS")&lt;/script&gt;' in response_text
    
    def test_admin_unauthorized_access_prevention(self, authenticated_client):
        """Test de prévention d'accès non autorisé."""
        # Utilisateur normal essayant d'accéder aux fonctions admin
        admin_urls = [
            '/admin/',
            '/admin/users',
            '/admin/modules',
            '/admin/modules/create'
        ]
        
        for url in admin_urls:
            response = authenticated_client.get(url)
            # Devrait être redirigé ou refusé
            assert response.status_code in [302, 403]


class TestAdminBulkOperations:
    """Tests pour les opérations en lot."""
    
    def test_admin_bulk_user_actions(self, admin_client, db_session):
        """Test d'actions en lot sur les utilisateurs."""
        # Créer plusieurs utilisateurs
        users = []
        for i in range(5):
            user = TestDataFactory.create_user(email=f'bulk{i+1}@example.com')
            users.append(user)
            db_session.add(user)
        
        db_session.commit()
        user_ids = [user.id for user in users[:3]]
        
        # Action en lot : changer le département
        response = admin_client.post('/admin/users/bulk_action', data={
            'action': 'change_department',
            'user_ids': user_ids,
            'department': 'Security'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        
        # Vérifier que les changements ont été appliqués
        for user in users[:3]:
            db_session.refresh(user)
            assert user.department == 'Security'
    
    def test_admin_bulk_module_status(self, admin_client, db_session):
        """Test de changement de statut en lot pour les modules."""
        # Créer plusieurs modules
        modules = []
        for i in range(4):
            module = TestDataFactory.create_module(
                title=f'Bulk Module {i+1}',
                is_active=True
            )
            modules.append(module)
            db_session.add(module)
        
        db_session.commit()
        module_ids = [module.id for module in modules[:2]]
        
        # Désactiver en lot
        response = admin_client.post('/admin/modules/bulk_action', data={
            'action': 'deactivate',
            'module_ids': module_ids
        }, follow_redirects=True)
        
        assert response.status_code == 200
        
        # Vérifier les changements
        for module in modules[:2]:
            db_session.refresh(module)
            assert module.is_active is False
        
        # Les autres modules restent actifs
        for module in modules[2:]:
            db_session.refresh(module)
            assert module.is_active is True
