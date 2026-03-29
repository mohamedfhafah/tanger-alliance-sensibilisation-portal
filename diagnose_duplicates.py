#!/usr/bin/env python3
"""
Diagnostic script to check for duplicate quizzes in the Vulnerability Management module
"""

import os
import sys
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import your models
from app.models import Quiz, Module, Question, Choice, User, UserProgress, QuizProgress

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///security_portal.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Initialize extensions
    db = SQLAlchemy()
    db.init_app(app)
    
    return app, db

def diagnose_duplicates():
    app, db = create_app()
    
    with app.app_context():
        print("=== DUPLICATE QUIZ DIAGNOSTIC ===\n")
        
        # Check for Vulnerability Management module
        vuln_module = Module.query.filter_by(name='Vulnerability Management').first()
        if not vuln_module:
            print("ERROR: Vulnerability Management module not found!")
            return
        
        print(f"Found Vulnerability Management module (ID: {vuln_module.id})")
        
        # Get all quizzes for this module
        quizzes = Quiz.query.filter_by(module_id=vuln_module.id).all()
        print(f"\nTotal quizzes in Vulnerability Management module: {len(quizzes)}")
        
        # Check for duplicates by title
        quiz_titles = {}
        duplicates_found = False
        
        for quiz in quizzes:
            title = quiz.title.strip()
            if title in quiz_titles:
                duplicates_found = True
                print(f"\n🔴 DUPLICATE FOUND:")
                print(f"   Title: '{title}'")
                print(f"   Quiz 1: ID={quiz_titles[title]['id']}, Created={quiz_titles[title]['created_at']}")
                print(f"   Quiz 2: ID={quiz.id}, Created={quiz.created_at}")
                
                # Compare question counts
                q1_count = Question.query.filter_by(quiz_id=quiz_titles[title]['id']).count()
                q2_count = Question.query.filter_by(quiz_id=quiz.id).count()
                print(f"   Question counts: Quiz 1={q1_count}, Quiz 2={q2_count}")
                
                quiz_titles[title]['duplicates'].append({
                    'id': quiz.id,
                    'created_at': quiz.created_at,
                    'question_count': q2_count
                })
            else:
                quiz_titles[title] = {
                    'id': quiz.id,
                    'created_at': quiz.created_at,
                    'question_count': Question.query.filter_by(quiz_id=quiz.id).count(),
                    'duplicates': []
                }
        
        if not duplicates_found:
            print("\n✅ No duplicate quiz titles found in Vulnerability Management module")
        
        # Show all quizzes with details
        print(f"\n=== ALL QUIZZES IN VULNERABILITY MANAGEMENT ===")
        for quiz in quizzes:
            question_count = Question.query.filter_by(quiz_id=quiz.id).count()
            print(f"ID: {quiz.id} | Title: '{quiz.title}' | Questions: {question_count} | Created: {quiz.created_at}")
        
        # Check user progress for this module
        print(f"\n=== USER PROGRESS ANALYSIS ===")
        user_progresses = UserProgress.query.filter_by(module_id=vuln_module.id).all()
        print(f"Total user progress records for Vulnerability Management: {len(user_progresses)}")
        
        for progress in user_progresses:
            user = User.query.get(progress.user_id)
            print(f"User: {user.email if user else 'Unknown'} | Completed: {progress.completed} | Score: {progress.score}")
        
        # Check quiz-specific progress
        print(f"\n=== QUIZ PROGRESS ANALYSIS ===")
        quiz_progresses = QuizProgress.query.join(Quiz).filter(Quiz.module_id == vuln_module.id).all()
        print(f"Total quiz progress records for Vulnerability Management: {len(quiz_progresses)}")
        
        for qp in quiz_progresses:
            user = User.query.get(qp.user_id)
            quiz = Quiz.query.get(qp.quiz_id)
            print(f"User: {user.email if user else 'Unknown'} | Quiz: '{quiz.title if quiz else 'Unknown'}' | Completed: {qp.completed} | Score: {qp.score}")

if __name__ == '__main__':
    diagnose_duplicates()
