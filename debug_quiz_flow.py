#!/usr/bin/env python3
"""
Debugging script to analyze quiz submission flow and session handling
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models import User, Module, Quiz, Progress, QuizProgress
from datetime import datetime

def debug_user_progress(user_id=None, email=None):
    """Debug a specific user's progress with the vulnerability management module"""
    app = create_app()
    
    with app.app_context():
        # Find user
        if user_id:
            user = User.query.get(user_id)
        elif email:
            user = User.query.filter_by(email=email).first()
        else:
            print("❌ Please provide either user_id or email")
            return
            
        if not user:
            print("❌ User not found")
            return
            
        print(f"👤 User: {user.username} ({user.email})")
        print(f"   ID: {user.id}")
        print()
        
        # Find the Vulnerability Management module
        vuln_module = Module.query.filter_by(name='Gestion des vulnérabilités').first()
        
        if not vuln_module:
            print("❌ Vulnerability Management module not found")
            return
            
        print(f"📚 Module: {vuln_module.name}")
        print(f"   ID: {vuln_module.id}")
        print()
        
        # Check user's progress on this module
        progress = Progress.query.filter_by(
            user_id=user.id, 
            module_id=vuln_module.id
        ).first()
        
        if progress:
            print("📈 Module Progress:")
            print(f"   Completed: {progress.completed}")
            print(f"   Score: {progress.score}")
            print(f"   Started: {progress.started_at}")
            print(f"   Completed at: {progress.completion_date}")
            print()
        else:
            print("❌ No module progress found for this user")
            print()
        
        # Check quiz progress
        quizzes = Quiz.query.filter_by(module_id=vuln_module.id).all()
        
        for quiz in quizzes:
            print(f"🧩 Quiz: {quiz.title} (ID: {quiz.id})")
            
            quiz_progress = QuizProgress.query.filter_by(
                user_id=user.id,
                quiz_id=quiz.id
            ).first()
            
            if quiz_progress:
                print(f"   Progress exists:")
                print(f"     Completed: {quiz_progress.completed}")
                print(f"     Score: {quiz_progress.score}")
                print(f"     Attempts: {quiz_progress.attempts}")
                print(f"     Started: {quiz_progress.started_at}")
                print(f"     Completed at: {quiz_progress.completion_date}")
                
                # Check individual answers
                print(f"     Answers ({len(quiz_progress.answers)}):")
                for answer in quiz_progress.answers:
                    print(f"       Q{answer.question_id}: {answer.selected_option} ({'✅' if answer.is_correct else '❌'})")
            else:
                print("   No quiz progress found")
            
            print()

def analyze_session_handling():
    """Analyze the session handling logic in the code"""
    print("🔍 Session Handling Analysis")
    print("=" * 50)
    
    # Read the modules.py file to analyze session handling
    try:
        with open('/Users/mohamedfhafah/Documents/Analyse_Cecurité/Projet_Portail_Securite/app/routes/modules.py', 'r') as f:
            content = f.read()
            
        print("📄 Analyzing modules.py for session handling...")
        
        # Look for session variable usage
        session_vars = ['retaking_quiz', 'previous_completion']
        
        for var in session_vars:
            if var in content:
                print(f"✅ Found session variable: {var}")
                
                # Find where it's set
                lines = content.split('\n')
                for i, line in enumerate(lines, 1):
                    if f"session['{var}']" in line or f'session["{var}"]' in line:
                        print(f"   Line {i}: {line.strip()}")
                        
                    if f"'{var}' in session" in line or f'"{var}" in session' in line:
                        print(f"   Check Line {i}: {line.strip()}")
                        
                    if f"del session['{var}']" in line or f'del session["{var}"]' in line:
                        print(f"   Delete Line {i}: {line.strip()}")
            else:
                print(f"❌ Session variable not found: {var}")
            
            print()
            
    except FileNotFoundError:
        print("❌ modules.py file not found")
    except Exception as e:
        print(f"❌ Error reading file: {e}")

def suggest_fixes():
    """Suggest potential fixes for the quiz duplication issue"""
    print("🔧 Suggested Fixes")
    print("=" * 50)
    
    fixes = [
        {
            "issue": "Session variables not cleared properly",
            "solution": "Wrap session cleanup in try-finally block",
            "code": """
try:
    # Quiz submission logic here
    pass
finally:
    # Always clear session variables
    session.pop('retaking_quiz', None)
    session.pop('previous_completion', None)
"""
        },
        {
            "issue": "Progress not updated correctly",
            "solution": "Add explicit database commit after progress update",
            "code": """
# After updating progress
quiz_progress.completed = True
quiz_progress.completion_date = datetime.utcnow()
db.session.commit()  # Explicit commit
"""
        },
        {
            "issue": "Race condition in quiz state",
            "solution": "Add database transaction isolation",
            "code": """
from sqlalchemy.exc import IntegrityError

try:
    with db.session.begin():
        # All quiz update operations here
        pass
except IntegrityError:
    db.session.rollback()
    flash('Error updating quiz progress', 'error')
"""
        },
        {
            "issue": "Frontend JavaScript causing redirect loops",
            "solution": "Add JavaScript debugging and state checks",
            "code": """
// Add to quiz template
console.log('Quiz state:', {
    completed: {{ 'true' if progress and progress.completed else 'false' }},
    retaking: {{ 'true' if session.get('retaking_quiz') else 'false' }}
});
"""
        }
    ]
    
    for i, fix in enumerate(fixes, 1):
        print(f"{i}. {fix['issue']}")
        print(f"   Solution: {fix['solution']}")
        print(f"   Code example:")
        print(f"   {fix['code']}")
        print()

if __name__ == "__main__":
    print("Quiz Flow Debugging Tool")
    print("=" * 50)
    
    # You can modify these parameters to debug a specific user
    # debug_user_progress(email="user@example.com")  # Replace with actual user email
    
    analyze_session_handling()
    suggest_fixes()
    
    print("\nTo debug a specific user, uncomment and modify the debug_user_progress call above")
