#!/usr/bin/env python
"""
Tests pour les routes principales du portail de sécurité.

Tests couverts:
- Page d'accueil
- Tableau de bord utilisateur
- Navigation entre modules
- Profil utilisateur
- Recherche et filtrage
- Responsive design et accessibilité
"""

import pytest
from flask import url_for
from app.models.user import User
from app.models.module import Module, UserProgress
from tests.conftest import TestUtils, TestDataFactory, TEST_UPDATED_PASSWORD, TEST_USER_PASSWORD


class TestMainRoutes:
    """Tests pour les routes principales."""
    
    def test_home_page_unauthenticated(self, client):
        """Test de la page d'accueil pour utilisateur non connecté."""
        response = client.get('/')
        assert response.status_code == 200
        assert b'Mission Active: Tanger Alliance' in response.data
        assert 'Se connecter'.encode() in response.data
    
    def test_home_page_authenticated(self, authenticated_client, test_user):
        """Test de la page d'accueil pour utilisateur connecté."""
        response = authenticated_client.get('/')
        assert response.status_code == 200
        assert b'Acc\xc3\xa9der au tableau de bord' in response.data
        assert b'Explorer les modules' in response.data
    
    def test_dashboard_access_authenticated(self, authenticated_client):
        """Test d'accès au tableau de bord pour utilisateur connecté."""
        response = authenticated_client.get('/dashboard')
        assert response.status_code == 200
        assert b'Operational Dashboard' in response.data or b'Tableau de Bord' in response.data
    
    def test_dashboard_access_unauthenticated(self, client):
        """Test d'accès au tableau de bord pour utilisateur non connecté."""
        response = client.get('/dashboard')
        # Devrait rediriger vers la page de connexion
        assert response.status_code == 302
        assert '/auth/login' in response.location


class TestModuleNavigation:
    """Tests pour la navigation des modules."""
    
    def test_modules_list_page(self, authenticated_client, db_session):
        """Test de la page listant tous les modules."""
        # Créer quelques modules de test
        modules = []
        for i in range(3):
            module = TestDataFactory.create_module(
                title=f'Module de test {i+1}',
                order=i+1,
                is_active=True
            )
            modules.append(module)
            db_session.add(module)
        
        db_session.commit()
        
        response = authenticated_client.get('/modules/')
        assert response.status_code == 200
        
        # Vérifier que tous les modules actifs apparaissent
        for module in modules:
            assert module.title.encode() in response.data
    
    def test_module_detail_page(self, authenticated_client, test_module):
        """Test de la page de détail d'un module."""
        response = authenticated_client.get(f'/modules/view/{test_module.id}')
        assert response.status_code == 200
        assert test_module.title.encode() in response.data
        assert test_module.description.encode() in response.data
        assert test_module.content.encode() in response.data
    
    def test_module_detail_nonexistent(self, authenticated_client):
        """Test d'accès à un module inexistant."""
        response = authenticated_client.get('/modules/view/99999')
        assert response.status_code == 404
    
    def test_module_access_inactive(self, authenticated_client, db_session):
        """Test d'accès à un module inactif."""
        inactive_module = TestDataFactory.create_module(
            title='Module inactif',
            is_active=False
        )
        db_session.add(inactive_module)
        db_session.commit()
        
        response = authenticated_client.get(f'/modules/view/{inactive_module.id}')
        # Devrait soit rediriger soit retourner 404
        assert response.status_code in [302, 404]
    
    def test_module_completion_tracking(self, authenticated_client, test_user, test_module, db_session):
        """Test du suivi de complétion des modules."""
        # Marquer le module comme commencé
        response = authenticated_client.post(f'/modules/{test_module.id}/start')
        assert response.status_code in [200, 302]
        
        # Vérifier que la progression a été créée
        progress = UserProgress.query.filter_by(
            user_id=test_user.id,
            module_id=test_module.id
        ).first()
        assert progress is not None
        assert progress.completed is False
        
        # Marquer comme complété
        response = authenticated_client.post(f'/modules/{test_module.id}/complete')
        assert response.status_code in [200, 302]
        
        # Vérifier la complétion
        db_session.refresh(progress)
        assert progress.completed is True
        assert progress.completed_at is not None


class TestUserProfile:
    """Tests pour le profil utilisateur."""
    
    def test_profile_page_access(self, authenticated_client, test_user):
        """Test d'accès à la page de profil."""
        response = authenticated_client.get('/profile')
        assert response.status_code == 200
        assert test_user.email.encode() in response.data
        assert test_user.firstname.encode() in response.data
        assert test_user.lastname.encode() in response.data
    
    def test_profile_update(self, authenticated_client, test_user, db_session):
        """Test de mise à jour du profil."""
        response = authenticated_client.post('/profile', data={
            'firstname': 'Nouveau',
            'lastname': 'Nom',
            'department': 'Security',
            'email': test_user.email  # Email ne change pas
        }, follow_redirects=True)
        
        assert response.status_code == 200
        
        # Vérifier les changements
        db_session.refresh(test_user)
        assert test_user.firstname == 'Nouveau'
        assert test_user.lastname == 'Nom'
        assert test_user.department == 'security'  # Department is converted to lowercase in the route
    
    def test_profile_password_change(self, authenticated_client, test_user, db_session):
        """Test de changement de mot de passe."""
        response = authenticated_client.post('/profile/change_password', data={
            'current_password': TEST_USER_PASSWORD,
            'new_password': TEST_UPDATED_PASSWORD,
            'confirm_password': TEST_UPDATED_PASSWORD
        }, follow_redirects=True)
        
        assert response.status_code == 200
        
        # Vérifier le changement
        db_session.refresh(test_user)
        assert test_user.check_password(TEST_UPDATED_PASSWORD)
        assert not test_user.check_password(TEST_USER_PASSWORD)
    
    def test_profile_password_change_wrong_current(self, authenticated_client, test_user):
        """Test de changement de mot de passe avec mauvais mot de passe actuel."""
        response = authenticated_client.post('/profile/change_password', data={
            'current_password': 'wrongpassword',
            'new_password': TEST_UPDATED_PASSWORD,
            'confirm_password': TEST_UPDATED_PASSWORD
        }, follow_redirects=True)
        
        assert response.status_code == 200
        assert test_user.check_password(TEST_USER_PASSWORD)
        assert b'Profil' in response.data or b'Informations personnelles' in response.data
    
    def test_profile_picture_upload(self, authenticated_client, test_user):
        """Test d'upload de photo de profil."""
        # Simuler un upload de fichier
        from io import BytesIO
        from pathlib import Path

        pictures_dir = Path('app/static/profile_pics')
        before_upload = {path.name for path in pictures_dir.iterdir() if path.is_file()}
        
        data = {
            'profile_picture': (BytesIO(b'fake image data'), 'test.jpg')
        }
        
        response = authenticated_client.post('/profile/upload_picture', 
                                           data=data, 
                                           content_type='multipart/form-data')
        
        # Devrait soit accepter soit rejeter proprement
        assert response.status_code in [200, 302, 400]

        after_upload = {path.name for path in pictures_dir.iterdir() if path.is_file()}
        generated_files = after_upload - before_upload
        for filename in generated_files:
            (pictures_dir / filename).unlink(missing_ok=True)


class TestSearchAndFiltering:
    """Tests pour la recherche et le filtrage."""
    
    def test_module_search(self, authenticated_client, db_session):
        """Test de recherche dans les modules."""
        # Créer des modules avec différents termes
        modules_data = [
            ('Sécurité des mots de passe', 'Apprenez à créer des mots de passe sécurisés'),
            ('Phishing et ingénierie sociale', 'Détectez les tentatives de phishing'),
            ('Sécurité réseau', 'Protégez votre infrastructure réseau')
        ]
        
        for title, description in modules_data:
            module = TestDataFactory.create_module(
                title=title,
                description=description,
                is_active=True
            )
            db_session.add(module)
        
        db_session.commit()
        
        # Rechercher "sécurité"
        response = authenticated_client.get('/modules/?search=sécurité')
        assert response.status_code == 200
        assert 'Sécurité des mots de passe'.encode() in response.data
        assert 'Sécurité réseau'.encode() in response.data
        assert 'Phishing'.encode() not in response.data
        
        # Rechercher "phishing"
        response = authenticated_client.get('/modules/?search=phishing')
        assert response.status_code == 200
        assert 'Phishing et ingénierie sociale'.encode() in response.data
        assert 'mots de passe'.encode() not in response.data
    
    def test_module_filtering_by_completion(self, authenticated_client, test_user, db_session):
        """Test de filtrage des modules par statut de complétion."""
        # Créer des modules
        completed_module = TestDataFactory.create_module(title='Module complété')
        in_progress_module = TestDataFactory.create_module(title='Module en cours')
        not_started_module = TestDataFactory.create_module(title='Module non commencé')
        
        db_session.add_all([completed_module, in_progress_module, not_started_module])
        db_session.commit()
        
        # Créer des progressions
        completed_progress = TestDataFactory.create_progress(
            user_id=test_user.id,
            module_id=completed_module.id,
            completed=True
        )
        in_progress_progress = TestDataFactory.create_progress(
            user_id=test_user.id,
            module_id=in_progress_module.id,
            completed=False
        )
        
        db_session.add_all([completed_progress, in_progress_progress])
        db_session.commit()
        
        # Filtrer les modules complétés
        response = authenticated_client.get('/modules/?filter=completed')
        assert response.status_code == 200
        assert 'Module complété'.encode() in response.data
        assert 'Module en cours'.encode() not in response.data
        
        # Filtrer les modules en cours
        response = authenticated_client.get('/modules/?filter=in_progress')
        assert response.status_code == 200
        assert 'Module en cours'.encode() in response.data
        assert 'Module complété'.encode() not in response.data


class TestProgressTracking:
    """Tests pour le suivi de progression."""
    
    def test_progress_dashboard(self, authenticated_client, test_user, db_session):
        """Test du tableau de bord de progression."""
        # Créer des modules et progressions
        modules = []
        for i in range(5):
            module = TestDataFactory.create_module(
                title=f'Module {i+1}',
                order=i+1
            )
            modules.append(module)
            db_session.add(module)
        
        db_session.commit()
        
        # Compléter quelques modules
        for i in range(3):
            progress = TestDataFactory.create_progress(
                user_id=test_user.id,
                module_id=modules[i].id,
                completed=True,
                score=80 + i * 5
            )
            db_session.add(progress)
        
        db_session.commit()
        
        response = authenticated_client.get('/dashboard')
        assert response.status_code == 200
        
        # Vérifier que le tableau de bord et les modules créés sont bien affichés
        assert b'Operational Dashboard' in response.data or b'Tableau de Bord' in response.data
        assert modules[0].title.encode() in response.data
    
    def test_progress_statistics(self, authenticated_client, test_user, db_session):
        """Test des statistiques de progression."""
        # Créer des progressions avec scores
        module = TestDataFactory.create_module(title='Module avec score')
        db_session.add(module)
        db_session.commit()
        
        progress = TestDataFactory.create_progress(
            user_id=test_user.id,
            module_id=module.id,
            completed=True,
            score=95
        )
        db_session.add(progress)
        db_session.commit()
        
        response = authenticated_client.get('/dashboard')
        assert response.status_code == 200
        
        # Devrait afficher le score
        assert '95'.encode() in response.data


class TestResponsiveDesign:
    """Tests pour le design responsive."""
    
    def test_mobile_viewport(self, authenticated_client):
        """Test de la balise viewport pour mobile."""
        response = authenticated_client.get('/')
        assert response.status_code == 200
        assert 'viewport'.encode() in response.data
        assert 'width=device-width'.encode() in response.data
    
    def test_css_responsive_classes(self, authenticated_client):
        """Test de la présence de classes CSS responsive."""
        response = authenticated_client.get('/modules/')
        assert response.status_code == 200
        
        # Vérifier la présence de classes Bootstrap ou CSS responsive
        responsive_classes = [b'col-', b'row', b'container', b'responsive']
        has_responsive_class = any(cls in response.data for cls in responsive_classes)
        assert has_responsive_class


class TestAccessibility:
    """Tests pour l'accessibilité."""
    
    def test_semantic_html(self, authenticated_client):
        """Test de l'utilisation d'HTML sémantique."""
        response = authenticated_client.get('/')
        assert response.status_code == 200
        
        # Vérifier la présence d'éléments sémantiques
        semantic_elements = [b'<header', b'<nav', b'<main', b'<footer', b'<section', b'<article']
        has_semantic_elements = any(elem in response.data for elem in semantic_elements)
        assert has_semantic_elements
    
    def test_alt_attributes(self, authenticated_client):
        """Test de la présence d'attributs alt sur les images."""
        response = authenticated_client.get('/modules', follow_redirects=True)
        assert response.status_code == 200
        
        # Si des images sont présentes, elles devraient avoir des attributs alt
        if b'<img' in response.data:
            assert b'alt=' in response.data
    
    def test_form_labels(self, authenticated_client):
        """Test de la présence de labels sur les formulaires."""
        response = authenticated_client.get('/profile')
        assert response.status_code == 200
        
        # Les champs de formulaire devraient avoir des labels
        if b'<input' in response.data:
            assert b'<label' in response.data or b'aria-label' in response.data


class TestErrorHandling:
    """Tests pour la gestion d'erreurs."""
    
    def test_404_page(self, authenticated_client):
        """Test de la page 404."""
        response = authenticated_client.get('/page-inexistante')
        assert response.status_code == 404
    
    def test_500_error_handling(self, authenticated_client):
        """Test de gestion des erreurs 500."""
        # Déclencher une erreur en accédant à un module avec ID invalide
        response = authenticated_client.get('/modules/invalid_id')
        # Devrait soit retourner 404 soit gérer l'erreur proprement
        assert response.status_code in [404, 500]
    
    def test_csrf_protection(self, client, test_user):
        """Test de protection CSRF sur les formulaires."""
        # Se connecter
        TestUtils.login_user(client, test_user.email, TEST_USER_PASSWORD)
        
        # Essayer de poster sans token CSRF
        response = client.post('/profile', data={
            'firstname': 'Test',
            'lastname': 'CSRF'
        })
        
        # Devrait être rejeté (400 ou redirection)
        assert response.status_code in [400, 403, 302]
