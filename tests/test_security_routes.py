#!/usr/bin/env python
"""
Tests pour les pages et endpoints sécurité réellement exposés par l'application.
"""

from app.models.simulation_rating import SimulationRating


class TestSecurityPages:
    """Tests des pages de sécurité visibles pour les utilisateurs."""

    def test_security_alerts_access_authenticated(self, authenticated_client):
        response = authenticated_client.get('/security/security-alerts')
        assert response.status_code == 200
        assert b'Alertes de s' in response.data or b'Alertes de s\xc3\xa9curit\xc3\xa9' in response.data

    def test_security_alerts_access_unauthenticated(self, client):
        response = client.get('/security/security-alerts')
        assert response.status_code == 302
        assert '/auth/login' in response.location

    def test_security_resources_display(self, authenticated_client):
        response = authenticated_client.get('/security/security-resources')
        assert response.status_code == 200
        assert b'Ressources de s' in response.data or b'Ressources de s\xc3\xa9curit\xc3\xa9' in response.data

    def test_security_policy_display(self, authenticated_client):
        response = authenticated_client.get('/security/security-policy')
        assert response.status_code == 200
        assert b'Politique de s' in response.data or b'Politique de s\xc3\xa9curit\xc3\xa9' in response.data

    def test_contact_security_display(self, authenticated_client):
        response = authenticated_client.get('/security/contact-security')
        assert response.status_code == 200
        assert b'Contact' in response.data


class TestSimulationPages:
    """Tests des simulations de sensibilisation."""

    def test_simulation_list_page(self, authenticated_client):
        response = authenticated_client.get('/simulations')
        assert response.status_code == 200
        assert b'Simulations' in response.data

    def test_simulation_detail_page(self, authenticated_client):
        response = authenticated_client.get('/simulations/phishing_email')
        assert response.status_code == 200
        assert b'phishing' in response.data.lower()


class TestSimulationRatings:
    """Tests de l'API de notation des simulations."""

    def test_create_simulation_rating(self, authenticated_client, test_user, db_session):
        response = authenticated_client.post(
            '/api/simulations/phishing_email/rate',
            data={'rating': 4}
        )

        assert response.status_code == 200

        rating = SimulationRating.query.filter_by(
            user_id=test_user.id,
            simulation_slug='phishing_email'
        ).first()
        assert rating is not None
        assert rating.rating == 4

    def test_get_simulation_rating_stats(self, authenticated_client, test_user, db_session):
        db_session.query(SimulationRating).delete()
        rating = SimulationRating(
            user_id=test_user.id,
            simulation_slug='phishing_email',
            rating=5
        )
        db_session.add(rating)
        db_session.commit()

        response = authenticated_client.get('/api/simulations/phishing_email/rating')
        assert response.status_code == 200

        payload = response.get_json()
        assert payload['count'] >= 1
        assert payload['average'] >= 1
        assert payload['user_rating'] == 5


class TestSecurityLearning:
    """Tests du contenu sécurité présenté dans les parcours et profils."""

    def test_security_modules_access(self, authenticated_client):
        response = authenticated_client.get('/modules/')
        assert response.status_code == 200
        assert b'Modules' in response.data or b'Parcours' in response.data

    def test_security_badges_display(self, authenticated_client):
        response = authenticated_client.get('/profile')
        assert response.status_code == 200
        assert b'Badges' in response.data
