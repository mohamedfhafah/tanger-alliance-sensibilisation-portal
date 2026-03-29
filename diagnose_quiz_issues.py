#!/usr/bin/env python3
"""
Diagnostic script to identify quiz-related issues in the security portal application.
This script will help identify:
1. Duplicate quizzes in modules
2. Orphaned quiz progress records
3. Users with multiple quiz attempts on the same quiz
4. Session-related issues that might cause redirect loops
"""

import os
import sys
from collections import defaultdict, Counter

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models import Module, Quiz, Question, Choice, User, UserProgress, QuizProgress

def analyze_duplicate_quizzes():
    """Find duplicate quizzes within modules."""
    print("\n=== ANALYZING DUPLICATE QUIZZES ===")
    
    modules = Module.query.all()
    total_duplicates = 0
    
    for module in modules:
        quizzes = Quiz.query.filter_by(module_id=module.id).all()
        quiz_titles = [quiz.title for quiz in quizzes]
        title_counts = Counter(quiz_titles)
        
        duplicates = {title: count for title, count in title_counts.items() if count > 1}
        
        if duplicates:
            print(f"\nModule: {module.title} (ID: {module.id})")
            for title, count in duplicates.items():
                print(f"  - Quiz '{title}': {count} instances")
                # Show detailed info about duplicate quizzes
                duplicate_quizzes = Quiz.query.filter_by(module_id=module.id, title=title).all()
                for quiz in duplicate_quizzes:
                    question_count = Question.query.filter_by(quiz_id=quiz.id).count()
                    print(f"    * Quiz ID {quiz.id}: {question_count} questions, Created: {quiz.created_at}")
                total_duplicates += count - 1
    
    print(f"\nTotal duplicate quizzes found: {total_duplicates}")
    return total_duplicates

def analyze_quiz_progress():
    """Analyze quiz progress and user attempts."""
    print("\n=== ANALYZING QUIZ PROGRESS ===")
    
    # Count quiz progress records per user per quiz
    progress_records = QuizProgress.query.all()
    user_quiz_attempts = defaultdict(lambda: defaultdict(list))
    
    for progress in progress_records:
        user_quiz_attempts[progress.user_id][progress.quiz_id].append(progress)
    
    multiple_attempts = 0
    for user_id, quizzes in user_quiz_attempts.items():
        user = User.query.get(user_id)
        for quiz_id, attempts in quizzes.items():
            if len(attempts) > 1:
                quiz = Quiz.query.get(quiz_id)
                print(f"\nUser {user.username} (ID: {user_id}) has {len(attempts)} attempts on quiz '{quiz.title}' (ID: {quiz_id})")
                for i, attempt in enumerate(attempts, 1):
                    print(f"  Attempt {i}: Score {attempt.score}, Completed: {attempt.completed}, Date: {attempt.completed_at}")
                multiple_attempts += 1
    
    print(f"\nUsers with multiple attempts on same quiz: {multiple_attempts}")
    
    # Check for orphaned quiz progress (quiz or user doesn't exist)
    orphaned_progress = []
    for progress in progress_records:
        if not User.query.get(progress.user_id) or not Quiz.query.get(progress.quiz_id):
            orphaned_progress.append(progress)
    
    if orphaned_progress:
        print(f"\nOrphaned quiz progress records: {len(orphaned_progress)}")
        for progress in orphaned_progress:
            print(f"  Progress ID {progress.id}: User {progress.user_id}, Quiz {progress.quiz_id}")

def analyze_user_progress():
    """Analyze user progress records."""
    print("\n=== ANALYZING USER PROGRESS ===")
    
    # Check for multiple UserProgress records per user per module
    progress_records = UserProgress.query.all()
    user_module_progress = defaultdict(lambda: defaultdict(list))
    
    for progress in progress_records:
        user_module_progress[progress.user_id][progress.module_id].append(progress)
    
    multiple_module_progress = 0
    for user_id, modules in user_module_progress.items():
        user = User.query.get(user_id)
        for module_id, progress_list in modules.items():
            if len(progress_list) > 1:
                module = Module.query.get(module_id)
                print(f"\nUser {user.username} (ID: {user_id}) has {len(progress_list)} progress records for module '{module.title}' (ID: {module_id})")
                for i, progress in enumerate(progress_list, 1):
                    print(f"  Record {i}: Progress {progress.progress}%, Completed: {progress.completed}, Updated: {progress.updated_at}")
                multiple_module_progress += 1
    
    print(f"\nUsers with multiple progress records per module: {multiple_module_progress}")

def show_vulnerability_management_details():
    """Show detailed information about the vulnerability management module."""
    print("\n=== VULNERABILITY MANAGEMENT MODULE DETAILS ===")
    
    vuln_module = Module.query.filter_by(title='Gestion des Vulnérabilités').first()
    if not vuln_module:
        print("Vulnerability Management module not found!")
        return
    
    print(f"Module: {vuln_module.title} (ID: {vuln_module.id})")
    print(f"Description: {vuln_module.description[:100]}...")
    
    quizzes = Quiz.query.filter_by(module_id=vuln_module.id).all()
    print(f"\nQuizzes in this module: {len(quizzes)}")
    
    for quiz in quizzes:
        question_count = Question.query.filter_by(quiz_id=quiz.id).count()
        progress_count = QuizProgress.query.filter_by(quiz_id=quiz.id).count()
        print(f"\nQuiz: {quiz.title} (ID: {quiz.id})")
        print(f"  Questions: {question_count}")
        print(f"  User attempts: {progress_count}")
        print(f"  Created: {quiz.created_at}")
        
        # Show recent quiz progress for this quiz
        recent_progress = QuizProgress.query.filter_by(quiz_id=quiz.id).order_by(QuizProgress.completed_at.desc()).limit(5).all()
        if recent_progress:
            print(f"  Recent attempts:")
            for progress in recent_progress:
                user = User.query.get(progress.user_id)
                print(f"    - {user.username}: Score {progress.score}, Completed: {progress.completed}, Date: {progress.completed_at}")

def main():
    """Main diagnostic function."""
    print("Starting Quiz Issues Diagnostic...")
    print("=" * 50)
    
    app = create_app()
    with app.app_context():
        # Run all diagnostic functions
        analyze_duplicate_quizzes()
        analyze_quiz_progress()
        analyze_user_progress()
        show_vulnerability_management_details()
        
    print("\n" + "=" * 50)
    print("Diagnostic completed!")

if __name__ == '__main__':
    main()
