"""
Populate sample hints for existing questions.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from src.main import app
from src.database import db
from src.models.assessment import Question
from src.services.hint_service import HintService

def populate_hints():
    """Generate and populate hints for all questions."""
    with app.app_context():
        questions = Question.query.all()
        
        print(f"Found {len(questions)} questions")
        print("Generating hints...\n")
        
        hints_created = 0
        
        for question in questions:
            # Check if hints already exist
            existing_hints = HintService.get_hints_for_question(question.id)
            if existing_hints:
                print(f"  ⚠ Question {question.id} already has {len(existing_hints)} hints, skipping")
                continue
            
            # Generate hints
            hints_data = HintService.generate_hints_for_question(question)
            
            # Create hints
            created = HintService.create_hints_for_question(question.id, hints_data)
            
            print(f"  ✓ Created {len(created)} hints for question {question.id}: \"{question.question_text[:50]}...\"")
            hints_created += len(created)
        
        print(f"\n✅ Successfully created {hints_created} hints for {len(questions)} questions")

if __name__ == '__main__':
    populate_hints()

