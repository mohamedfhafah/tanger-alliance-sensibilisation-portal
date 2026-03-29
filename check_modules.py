from app import create_app
from app.models import Module, Quiz

app = create_app()

with app.app_context():
    print("=== ALL MODULES IN DATABASE ===")
    modules = Module.query.all()
    
    if not modules:
        print("No modules found in database!")
    else:
        for module in modules:
            print(f"ID: {module.id}")
            print(f"Title: {module.title}")
            print(f"Description: {module.description[:100]}..." if len(module.description) > 100 else f"Description: {module.description}")
            print(f"Order: {module.order}")
            print(f"Active: {module.is_active}")
            print(f"Created: {module.created_at}")
            
            # Check quizzes for this module
            quizzes = Quiz.query.filter_by(module_id=module.id).all()
            print(f"Number of quizzes: {len(quizzes)}")
            
            for quiz in quizzes:
                print(f"  - Quiz ID: {quiz.id}, Title: {quiz.title}, Active: {quiz.is_active}")
            
            print("-" * 50)
    
    print(f"\nTotal modules found: {len(modules)}")
