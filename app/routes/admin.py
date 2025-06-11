from flask import Blueprint, flash, redirect, url_for
from flask_login import login_required, current_user
from app import db
from app.models.module import Module, Quiz, Question, Choice

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/activate-vulnerability-quiz')
@login_required
def activate_vulnerability_quiz():
    """Active le quiz pour le module Gestion des vulnérabilités en le créant s'il n'existe pas déjà."""
    # Vérifier si l'utilisateur est admin
    if not current_user.is_admin():
        flash('Accès non autorisé.', 'danger')
        return redirect(url_for('main.dashboard'))
    
    # Trouver le module de gestion des vulnérabilités
    vulnerability_module = None
    for module in Module.query.all():
        if 'vulnérabilité' in module.title.lower() or 'vulnerability' in module.title.lower():
            vulnerability_module = module
            break
    
    if not vulnerability_module:
        flash('Module de gestion des vulnérabilités non trouvé.', 'danger')
        return redirect(url_for('modules.index'))
    
    # Vérifier si un quiz existe déjà
    existing_quiz = Quiz.query.filter_by(module_id=vulnerability_module.id).first()
    
    if existing_quiz:
        flash(f'Un quiz existe déjà pour le module "{vulnerability_module.title}".', 'info')
    else:
        # Créer un nouveau quiz
        new_quiz = Quiz(
            module_id=vulnerability_module.id,
            title="Quiz sur la gestion des vulnérabilités",
            description="Testez vos connaissances sur la gestion des vulnérabilités et la sécurité des systèmes.",
            passing_score=70
        )
        db.session.add(new_quiz)
        db.session.flush()  # Pour obtenir l'ID du quiz
        
        # Créer des questions et choix de base
        questions = [
            {
                "content": "Qu'est-ce qu'une vulnérabilité de type 'zero-day' ?",
                "choices": [
                    {"content": "Une vulnérabilité qui existe depuis plus de 30 jours", "is_correct": False},
                    {"content": "Une vulnérabilité inconnue des développeurs et pour laquelle aucun correctif n'existe", "is_correct": True},
                    {"content": "Une vulnérabilité qui n'affecte que les systèmes Windows", "is_correct": False},
                    {"content": "Une vulnérabilité qui ne peut jamais être exploitée", "is_correct": False}
                ]
            },
            {
                "content": "Quelle est la meilleure pratique pour gérer les vulnérabilités logicielles ?",
                "choices": [
                    {"content": "Ignorer les mises à jour pour éviter d'introduire des problèmes", "is_correct": False},
                    {"content": "Mettre en place un programme régulier de mises à jour et de correctifs", "is_correct": True},
                    {"content": "Attendre que des attaques se produisent avant d'agir", "is_correct": False},
                    {"content": "Réinstaller le système d'exploitation chaque mois", "is_correct": False}
                ]
            },
            {
                "content": "Qu'est-ce que le 'CVE' dans le contexte de la sécurité informatique ?",
                "choices": [
                    {"content": "Computer Virus Encyclopedia", "is_correct": False},
                    {"content": "Common Vulnerability and Exposures - une liste de vulnérabilités connues", "is_correct": True},
                    {"content": "Critical Vulnerability Examination", "is_correct": False},
                    {"content": "Cyber Vulnerability Eradication", "is_correct": False}
                ]
            },
            {
                "content": "Quelle méthode est recommandée pour prioriser les correctifs de vulnérabilités ?",
                "choices": [
                    {"content": "Corriger toutes les vulnérabilités en même temps", "is_correct": False},
                    {"content": "Corriger d'abord les vulnérabilités des systèmes non critiques", "is_correct": False},
                    {"content": "Évaluer les risques et prioriser selon la criticité et l'exploitabilité", "is_correct": True},
                    {"content": "Corriger uniquement les vulnérabilités récentes", "is_correct": False}
                ]
            },
            {
                "content": "Quel est l'objectif principal d'un scan de vulnérabilités ?",
                "choices": [
                    {"content": "Exploiter les failles de sécurité pour tester la défense", "is_correct": False},
                    {"content": "Identifier les faiblesses et les vulnérabilités potentielles dans les systèmes", "is_correct": True},
                    {"content": "Ralentir le réseau pour détecter les goulots d'étranglement", "is_correct": False},
                    {"content": "Bloquer automatiquement toutes les connexions suspectes", "is_correct": False}
                ]
            }
        ]
        
        for q_data in questions:
            question = Question(
                quiz_id=new_quiz.id,
                content=q_data["content"]
            )
            db.session.add(question)
            db.session.flush()  # Pour obtenir l'ID de la question
            
            for c_data in q_data["choices"]:
                choice = Choice(
                    question_id=question.id,
                    content=c_data["content"],
                    is_correct=c_data["is_correct"]
                )
                db.session.add(choice)
        
        db.session.commit()
        flash(f'Quiz créé avec succès pour le module "{vulnerability_module.title}".', 'success')
    
    return redirect(url_for('modules.view', module_id=vulnerability_module.id))
