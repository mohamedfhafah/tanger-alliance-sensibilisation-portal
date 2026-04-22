#!/usr/bin/env python
"""
Tests pour les routes d'authentification du portail de sécurité.

Tests couverts:
- Inscription (register)
- Connexion (login)
- Déconnexion (logout)
- Réinitialisation de mot de passe
- Validation des formulaires
- Sécurité et protection CSRF
"""

import pytest
from datetime import datetime, timedelta
from flask import url_for
from app.models.user import User
from tests.conftest import TestUtils, TestDataFactory


class TestUserRegistration:
    """Tests pour l'inscription des utilisateurs."""
    
    def test_register_page_loads(self, client):
        """Test que la page d'inscription se charge correctement."""
        response = client.get('/auth/register')
        assert response.status_code == 200
        assert 'Inscription'.encode() in response.data
        assert 'email'.encode() in response.data
        assert 'password'.encode() in response.data
    
    def test_successful_registration(self, client, db_session):
        """Test d'inscription réussie avec des données valides."""
        response = client.post('/auth/register', data={
            'email': 'newuser@example.com',
            'firstname': 'Nouveau',
            'lastname': 'Utilisateur',
            'password': 'securepassword123',
            'confirm_password': 'securepassword123',
            'department': 'it'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        
        # Vérifier que l'utilisateur a été créé
        user = User.query.filter_by(email='newuser@example.com').first()
        assert user is not None
        assert user.firstname == 'Nouveau'
        assert user.lastname == 'Utilisateur'
        assert user.department == 'it'
        assert user.role == 'user'  # Rôle par défaut


class TestUserLogin:
    """Tests pour la connexion des utilisateurs."""
    
    def test_login_page_loads(self, client):
        """Test que la page de connexion se charge correctement."""
        response = client.get('/auth/login')
        assert response.status_code == 200
        assert 'Connexion'.encode() in response.data or 'Login'.encode() in response.data
        assert 'email'.encode() in response.data
        assert 'password'.encode() in response.data
    
    def test_successful_login(self, client, test_user):
        """Test de connexion réussie avec des identifiants valides."""
        response = client.post('/auth/login', data={
            'email': test_user.email,
            'password': 'password123'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        # Vérifier la redirection vers le tableau de bord
        assert b'Operational Dashboard' in response.data or b'Bienvenue' in response.data
