"""
Populate sample worked solutions for existing questions.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from src.main import app
from src.database import db
from src.models.assessment import Question
from src.services.solution_service import SolutionService

def populate_solutions():
    """Generate and populate solutions for all questions."""
    with app.app_context():
        questions = Question.query.all()
        
        print(f"Found {len(questions)} questions")
        print("Generating solutions...\n")
        
        solutions_created = 0
        
        for question in questions:
            # Check if solution already exists
            existing_solution = SolutionService.get_solution_for_question(question.id)
            if existing_solution:
                print(f"  ⚠ Question {question.id} already has a solution, skipping")
                continue
            
            # Generate solution
            solution_data = SolutionService.generate_solution_for_question(question)
            
            # Create solution
            solution = SolutionService.create_solution(question.id, solution_data)
            
            print(f"  ✓ Created solution for question {question.id}: \"{question.question_text[:50]}...\"")
            print(f"    - {len(solution_data['steps'])} steps")
            solutions_created += 1
        
        print(f"\n✅ Successfully created {solutions_created} solutions for {len(questions)} questions")

if __name__ == '__main__':
    populate_solutions()

