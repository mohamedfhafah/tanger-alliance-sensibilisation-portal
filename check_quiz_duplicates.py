#!/usr/bin/env python3
"""
Script to check for duplicate quizzes in the Vulnerability Management module
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models import Quiz, Module

def check_quiz_duplicates():
    app = create_app()
    
    with app.app_context():
        # Find the Vulnerability Management module
        vuln_module = Module.query.filter_by(name='Gestion des vulnérabilités').first()
        
        if not vuln_module:
            print("❌ Vulnerability Management module not found")
            print("Available modules:")
            modules = Module.query.all()
            for module in modules:
                print(f"  - {module.name} (ID: {module.id})")
            return
        
        print(f"✅ Found Vulnerability Management module:")
        print(f"   ID: {vuln_module.id}")
        print(f"   Name: {vuln_module.name}")
        print(f"   Description: {vuln_module.description}")
        print()
        
        # Check for quizzes in this module
        quizzes = Quiz.query.filter_by(module_id=vuln_module.id).all()
        
        print(f"📊 Found {len(quizzes)} quiz(zes) in Vulnerability Management module:")
        
        if not quizzes:
            print("   No quizzes found")
        else:
            for i, quiz in enumerate(quizzes, 1):
                print(f"   Quiz {i}:")
                print(f"     ID: {quiz.id}")
                print(f"     Title: {quiz.title}")
                print(f"     Questions count: {len(quiz.questions)}")
                print(f"     Created: {quiz.created_at}")
                print()
        
        # Check if there are duplicates (more than 1 quiz)
        if len(quizzes) > 1:
            print("⚠️  WARNING: Multiple quizzes found in the same module!")
            print("   This could cause the duplication issue you're experiencing.")
            print()
            
            # Show questions for each quiz to identify duplicates
            for i, quiz in enumerate(quizzes, 1):
                print(f"Quiz {i} questions:")
                for j, question in enumerate(quiz.questions, 1):
                    print(f"  Q{j}: {question.question_text}")
                print()
        else:
            print("✅ No duplicate quizzes detected")

if __name__ == "__main__":
    check_quiz_duplicates()
