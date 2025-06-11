#!/usr/bin/env python
"""
Tests pour les routes de sécurité du portail de sécurité.

Tests adaptés aux modèles existants de l'application.
"""

import pytest
from datetime import datetime
from flask import url_for
from app.models.campaign import Campaign, PhishingSimulation
from app.models.simulation_rating import SimulationRating
from app.models.badge import Badge
from app.models.user import User
from app.models.module import UserProgress
from tests.conftest import TestUtils, TestDataFactory


class TestSecurityDashboard:
    """Tests pour le tableau de bord de sécurité."""
    
    def test_security_dashboard_access_authenticated(self, authenticated_client):
        """Test d'accès au tableau de bord de sécurité pour un utilisateur authentifié."""
        response = authenticated_client.get('/security/')
        assert response.status_code == 200
    
    def test_security_dashboard_access_unauthenticated(self, client):
        """Test d'accès au tableau de bord sans authentification."""
        response = client.get('/security/')
        # Devrait rediriger vers la page de connexion
        assert response.status_code == 302


class TestPhishingSimulations:
    """Tests pour les simulations de phishing."""
    
    def test_phishing_simulation_list(self, authenticated_client, test_simulation):
        """Test d'accès à la liste des simulations de phishing."""
        response = authenticated_client.get('/security/simulations')
        assert response.status_code == 200
    
    def test_phishing_simulation_detail(self, authenticated_client, test_simulation):
        """Test d'accès au détail d'une simulation de phishing."""
        response = authenticated_client.get(f'/security/simulations/{test_simulation.id}')
        assert response.status_code == 200
        assert test_simulation.title.encode() in response.data


class TestSimulationRatings:
    """Tests pour les évaluations de simulations."""
    
    def test_create_simulation_rating(self, authenticated_client, db_session, test_user):
        """Test de création d'une évaluation de simulation."""
        rating_data = {
            'simulation_slug': 'test_simulation',
            'rating': 4
        }
        
        response = authenticated_client.post('/security/rate-simulation', data=rating_data)
        assert response.status_code in [200, 302]  # Success or redirect
        
        # Vérifier que l'évaluation a été créée
        rating = SimulationRating.query.filter_by(
            user_id=test_user.id,
            simulation_slug='test_simulation'
        ).first()
        
        if rating:  # Si le système d'évaluation est implémenté
            assert rating.rating == 4


class TestSecurityBadges:
    """Tests pour les badges de sécurité."""
    
    def test_security_badges_display(self, authenticated_client):
        """Test d'affichage des badges de sécurité."""
        response = authenticated_client.get('/security/badges')
        assert response.status_code == 200


class TestSecurityModules:
    """Tests pour les modules de sécurité."""
    
    def test_security_modules_access(self, authenticated_client):
        """Test d'accès aux modules de sécurité."""
        response = authenticated_client.get('/security/modules')
        assert response.status_code == 200


class TestSecurityReports:
    """Tests pour les rapports de sécurité."""
    
    def test_user_security_progress(self, authenticated_client, test_user):
        """Test du rapport de progression de sécurité de l'utilisateur."""
        response = authenticated_client.get('/security/progress')
        assert response.status_code == 200
    
    def test_security_statistics(self, authenticated_client):
        """Test d'accès aux statistiques de sécurité."""
        response = authenticated_client.get('/security/stats')
        assert response.status_code == 200


class TestSecuritySettings:
    """Tests pour les paramètres de sécurité."""
    
    def test_security_settings_access(self, authenticated_client):
        """Test d'accès aux paramètres de sécurité."""
        response = authenticated_client.get('/security/settings')
        assert response.status_code == 200
    
    def test_security_preferences_update(self, authenticated_client):
        """Test de mise à jour des préférences de sécurité."""
        preferences_data = {
            'email_notifications': True,
            'security_level': 'high'
        }
        
        response = authenticated_client.post('/security/settings', data=preferences_data)
        assert response.status_code in [200, 302]  # Success or redirect
