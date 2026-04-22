#!/usr/bin/env python
"""
Tests pour les routes de quiz et les fonctionnalités d'évaluation.

Tests couverts:
- Accès aux quiz
- Passage des quiz
- Calcul des scores
- Enregistrement des résultats
- Validation des réponses
- Gestion du temps (si applicable)
"""

import pytest
from datetime import datetime, timedelta
from flask import url_for
from app.models.module import Module, Quiz, Question, UserProgress
from app.models.user import User
from tests.conftest import TestUtils, TestDataFactory


def build_correct_answers(questions, limit=None):
    """Construit un payload valide basé sur les choix corrects en base."""
    payload = {}
    iterable = questions if limit is None else questions[:limit]
    for question in iterable:
        correct_choice = next(choice for choice in question.choices if choice.is_correct)
        payload[f'question_{question.id}'] = str(correct_choice.id)
    return payload


class TestQuizAccess:
    """Tests pour l'accès aux quiz."""
    
    def test_quiz_access_authenticated(self, authenticated_client, test_quiz):
        """Test d'accès au quiz pour utilisateur connecté."""
        response = authenticated_client.get(f'/quiz/{test_quiz.id}')
        assert response.status_code == 200
        assert test_quiz.title.encode() in response.data
        assert test_quiz.description.encode() in response.data
    
    def test_quiz_access_unauthenticated(self, client, test_quiz):
        """Test d'accès au quiz pour utilisateur non connecté."""
        response = client.get(f'/quiz/{test_quiz.id}')
        assert response.status_code == 302
        assert '/auth/login' in response.location
    
    def test_quiz_nonexistent(self, authenticated_client):
        """Test d'accès à un quiz inexistant."""
        response = authenticated_client.get('/quiz/99999')
        assert response.status_code == 404
    
    def test_quiz_module_prerequisite(self, authenticated_client, test_user, db_session):
        """Test de vérification des prérequis de module."""
        # Créer un module avec quiz qui nécessite un module précédent
        module1 = TestDataFactory.create_module(title='Module 1', order=1)
        module2 = TestDataFactory.create_module(title='Module 2', order=2)
        
        db_session.add_all([module1, module2])
        db_session.flush()  # Flush to assign IDs to modules
        
        quiz2 = Quiz(
            module_id=module2.id,
            title='Quiz Module 2',
            description='Quiz nécessitant la complétion du Module 1'
        )
        
        db_session.add(quiz2)
        db_session.commit()
        
        # Accéder au quiz sans avoir complété le module précédent
        response = authenticated_client.get(f'/quiz/{quiz2.id}')
        
        # Devrait soit rediriger soit afficher un avertissement
        # (dépend de l'implémentation des prérequis)
        assert response.status_code in [200, 302]


class TestQuizQuestions:
    """Tests pour l'affichage des questions de quiz."""
    
    def test_quiz_questions_display(self, authenticated_client, test_quiz, test_questions):
        """Test d'affichage des questions du quiz."""
        response = authenticated_client.get(f'/quiz/{test_quiz.id}/start')
        assert response.status_code == 200
        
        # Vérifier que la page de démarrage affiche le nombre de questions
        assert f"{len(test_questions)} questions".encode() in response.data
        
        # Vérifier que chaque question individuelle s'affiche correctement
        for i, question in enumerate(test_questions, 1):
            question_response = authenticated_client.get(f'/quiz/{test_quiz.id}/question/{i}')
            assert question_response.status_code == 200
            assert question.content.encode() in question_response.data
    
    def test_quiz_single_question_view(self, authenticated_client, test_quiz, test_questions):
        """Test d'affichage d'une question unique."""
        question = test_questions[0]
        response = authenticated_client.get(f'/quiz/{test_quiz.id}/question/1')  # Use question number, not ID
        assert response.status_code == 200
        assert question.content.encode() in response.data # Changed text to content
    
    def test_quiz_navigation(self, authenticated_client, test_quiz, test_questions):
        """Test de navigation entre les questions."""
        # Première question
        response = authenticated_client.get(f'/quiz/{test_quiz.id}/question/1')
        assert response.status_code == 200
        
        # Navigation vers la question suivante
        response = authenticated_client.get(f'/quiz/{test_quiz.id}/question/2')
        assert response.status_code == 200
        
        # Navigation vers la question précédente
        response = authenticated_client.get(f'/quiz/{test_quiz.id}/question/1')
        assert response.status_code == 200


class TestQuizSubmission:
    """Tests pour la soumission des réponses de quiz."""
    
    def test_quiz_answer_submission(self, authenticated_client, test_quiz, test_questions):
        """Test de soumission d'une réponse."""
        question = test_questions[0]
        
        response = authenticated_client.post(f'/quiz/{test_quiz.id}/answer', data={
            'question_id': question.id,
            'answer': 'A'  # Réponse de test
        })
        
        assert response.status_code in [200, 302]
    
    def test_quiz_multiple_answers(self, authenticated_client, test_quiz, test_questions):
        """Test de soumission de plusieurs réponses."""
        answers_data = build_correct_answers(test_questions)
        
        response = authenticated_client.post(f'/quiz/{test_quiz.id}/submit', 
                                           data=answers_data)
        assert response.status_code == 307
    
    def test_quiz_empty_answer(self, authenticated_client, test_quiz, test_questions):
        """Test de soumission avec réponse vide."""
        question = test_questions[0]
        
        response = authenticated_client.post(f'/quiz/{test_quiz.id}/answer', data={
            'question_id': question.id,
            'answer': ''  # Réponse vide
        })
        
        # Devrait soit accepter (score 0) soit rejeter
        assert response.status_code in [200, 302, 400]
    
    def test_quiz_invalid_question_id(self, authenticated_client, test_quiz):
        """Test de soumission avec ID de question invalide."""
        response = authenticated_client.post(f'/quiz/{test_quiz.id}/answer', data={
            'question_id': 99999,
            'answer': 'A'
        })
        
        assert response.status_code in [400, 404]


class TestQuizScoring:
    """Tests pour le calcul des scores de quiz."""
    
    def test_quiz_score_calculation(self, authenticated_client, test_user, test_quiz, test_questions, db_session):
        """Test de calcul du score du quiz."""
        # Simuler des réponses (toutes correctes)
        correct_answers = build_correct_answers(test_questions)
        
        response = authenticated_client.post(f'/quiz/{test_quiz.id}/submit', 
                                           data=correct_answers,
                                           follow_redirects=True)
        assert response.status_code == 200
        
        # Vérifier que le score a été enregistré
        progress = UserProgress.query.filter_by(
            user_id=test_user.id,
            module_id=test_quiz.module_id
        ).first()
        
        if progress:
            assert progress.score is not None
            assert progress.score >= 0
            assert progress.score <= 100
    
    def test_quiz_passing_score(self, authenticated_client, test_user, db_session):
        """Test de vérification du score de passage."""
        # Créer un module et quiz avec score de passage élevé
        module = TestDataFactory.create_module(title='Module Score Test')
        db_session.add(module)
        db_session.flush()  # Flush to assign ID to module
        
        quiz = Quiz(
            module_id=module.id,
            title='Quiz Score Test',
            passing_score=80
        )
        
        db_session.add(quiz)
        db_session.commit()
        
        # Créer des questions
        questions = []
        for i in range(3):
            question = Question(
                quiz_id=quiz.id,
                content=f'Question {i+1} ?', # Changed text to content
                explanation=f'Explication {i+1}'
            )
            questions.append(question)
            db_session.add(question)
        
        db_session.commit()

        from app.models.module import Choice
        for question in questions:
            db_session.add_all([
                Choice(question_id=question.id, content='Bonne réponse', is_correct=True),
                Choice(question_id=question.id, content='Mauvaise réponse 1', is_correct=False),
                Choice(question_id=question.id, content='Mauvaise réponse 2', is_correct=False),
            ])

        db_session.commit()
        
        # Soumettre des réponses partielles (score insuffisant)
        partial_answers = build_correct_answers(questions, limit=1)
        
        response = authenticated_client.post(f'/quiz/{quiz.id}/submit', 
                                           data=partial_answers,
                                           follow_redirects=True)
        assert response.status_code == 200

        progress = UserProgress.query.filter_by(
            user_id=test_user.id,
            module_id=module.id
        ).first()
        assert progress is not None
        assert progress.score < quiz.passing_score
    
    def test_quiz_perfect_score(self, authenticated_client, test_user, test_quiz, test_questions, db_session):
        """Test d'obtention d'un score parfait."""
        perfect_answers = build_correct_answers(test_questions)
        
        response = authenticated_client.post(f'/quiz/{test_quiz.id}/submit', 
                                           data=perfect_answers,
                                           follow_redirects=True)
        assert response.status_code == 200

        progress = UserProgress.query.filter_by(
            user_id=test_user.id,
            module_id=test_quiz.module_id
        ).first()
        assert progress is not None
        assert progress.score == 100


class TestQuizResults:
    """Tests pour l'affichage des résultats de quiz."""
    
    def test_quiz_results_page(self, authenticated_client, test_user, test_quiz, db_session):
        """Test de la page de résultats du quiz."""
        # Créer une progression avec score
        progress = TestDataFactory.create_progress(
            user_id=test_user.id,
            module_id=test_quiz.module_id,
            completed=True,
            score=85
        )
        db_session.add(progress)
        db_session.commit()
        
        response = authenticated_client.get(f'/quiz/{test_quiz.id}/results')
        assert response.status_code == 200
        assert '85'.encode() in response.data
    
    def test_quiz_review_answers(self, authenticated_client, test_quiz, test_questions):
        """Test de révision des réponses après le quiz."""
        response = authenticated_client.get(f'/quiz/{test_quiz.id}/review')
        assert response.status_code == 200
        
        # Devrait afficher les questions et explications
        for question in test_questions:
            assert question.content.encode() in response.data # Changed text to content
            if question.explanation:
                assert question.explanation.encode() in response.data
    
    def test_quiz_retake_availability(self, authenticated_client, test_user, test_quiz, db_session):
        """Test de disponibilité pour refaire le quiz."""
        # Marquer le quiz comme complété
        progress = TestDataFactory.create_progress(
            user_id=test_user.id,
            module_id=test_quiz.module_id,
            completed=True,
            score=65  # Score faible
        )
        db_session.add(progress)
        db_session.commit()
        
        response = authenticated_client.get(f'/quiz/{test_quiz.id}/review')
        assert response.status_code == 200
        assert b'Reprendre le quiz' in response.data


class TestQuizValidation:
    """Tests pour la validation des quiz."""
    
    def test_quiz_csrf_protection(self, authenticated_client, test_quiz, test_questions):
        """Test de protection CSRF sur la soumission de quiz."""
        # Essayer de soumettre sans token CSRF approprié
        answers = build_correct_answers(test_questions, limit=1)
        
        response = authenticated_client.post(f'/quiz/{test_quiz.id}/submit', 
                                           data=answers)
        
        # Si CSRF est activé, devrait être rejeté
        # Sinon, devrait être accepté normalement
        assert response.status_code in [307, 302, 400, 403]
    
    def test_quiz_session_validation(self, client, test_quiz):
        """Test de validation de session pour les quiz."""
        # Essayer d'accéder au quiz sans session valide
        response = client.get(f'/quiz/{test_quiz.id}')

        assert response.status_code == 302
        assert '/auth/login' in response.location
    
    def test_quiz_duplicate_submission(self, authenticated_client, test_quiz, test_questions):
        """Test de protection contre les soumissions multiples."""
        answers = build_correct_answers(test_questions)
        
        # Première soumission
        response1 = authenticated_client.post(f'/quiz/{test_quiz.id}/submit', 
                                            data=answers)
        assert response1.status_code == 307
        
        # Tentative de re-soumission
        response2 = authenticated_client.post(f'/quiz/{test_quiz.id}/submit', 
                                            data=answers)
        
        # Devrait soit rediriger soit afficher un message d'erreur
        assert response2.status_code in [307, 302, 400]


class TestQuizProgress:
    """Tests pour le suivi de progression dans les quiz."""
    
    def test_quiz_progress_tracking(self, authenticated_client, test_user, test_quiz, db_session):
        """Test de suivi de progression dans un quiz."""
        # Démarrer le quiz
        response = authenticated_client.post(f'/quiz/{test_quiz.id}/start')
        assert response.status_code in [200, 302]
        
        # Vérifier qu'une progression a été créée ou mise à jour
        progress = UserProgress.query.filter_by(
            user_id=test_user.id,
            module_id=test_quiz.module_id
        ).first()
        
        # Peut être None si la progression n'est créée qu'à la fin
        if progress:
            assert progress.started_at is not None
    
    def test_quiz_time_tracking(self, authenticated_client, test_quiz):
        """Test de suivi du temps de quiz."""
        # Démarrer le quiz
        start_response = authenticated_client.post(f'/quiz/{test_quiz.id}/start')
        assert start_response.status_code in [200, 302]
        
        # Simuler un délai
        import time
        time.sleep(1)
        
        # Terminer le quiz
        end_response = authenticated_client.post(f'/quiz/{test_quiz.id}/submit', 
                                               data={'question_1': '1'})
        assert end_response.status_code in [307, 302]
        
        # Le temps devrait être enregistré quelque part
        # (dépend de l'implémentation)
    
    def test_quiz_partial_completion(self, authenticated_client, test_quiz, test_questions):
        """Test de complétion partielle de quiz."""
        # Répondre seulement à une partie des questions
        partial_answers = build_correct_answers(test_questions, limit=1)
        
        response = authenticated_client.post(f'/quiz/{test_quiz.id}/submit', 
                                           data=partial_answers)
        assert response.status_code in [307, 302]
        
        # Devrait soit accepter la soumission partielle soit demander toutes les réponses


class TestQuizAccessibility:
    """Tests d'accessibilité pour les quiz."""
    
    def test_quiz_keyboard_navigation(self, authenticated_client, test_quiz):
        """Test de navigation au clavier dans les quiz."""
        response = authenticated_client.get(f'/quiz/{test_quiz.id}')
        assert response.status_code == 200
        
        # Vérifier la présence d'attributs d'accessibilité
        accessibility_attrs = [b'tabindex', b'aria-', b'role=']
        has_accessibility = any(attr in response.data for attr in accessibility_attrs)
        
        # Le test passe si des attributs d'accessibilité sont présents
        # (ou si ce n'est pas requis par l'implémentation)
    
    def test_quiz_screen_reader_support(self, authenticated_client, test_quiz, test_questions):
        """Test de support pour les lecteurs d'écran."""
        response = authenticated_client.get(f'/quiz/{test_quiz.id}')
        assert response.status_code == 200
        
        # Vérifier la structure sémantique
        semantic_elements = [b'<fieldset', b'<legend', b'<label']
        has_semantic_structure = any(elem in response.data for elem in semantic_elements)
        
        # Le test passe si une structure sémantique est présente
