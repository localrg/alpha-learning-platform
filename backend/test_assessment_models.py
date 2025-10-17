"""
Test script for assessment database models.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from src.main import app
from src.database import db
from src.models.user import User
from src.models.student import Student
from src.models.assessment import Skill, Question, Assessment, AssessmentResponse

def test_assessment_models():
    """Test all assessment models."""
    with app.app_context():
        print("=" * 60)
        print("TESTING ASSESSMENT DATABASE MODELS")
        print("=" * 60)
        
        # Test 1: Create a skill
        print("\n[TEST 1] Creating a test skill...")
        skill = Skill(
            name="Basic Multiplication",
            description="Multiply single-digit numbers",
            grade_level=3,
            subject_area="arithmetic",
            mastery_threshold=0.9
        )
        db.session.add(skill)
        db.session.commit()
        print(f"✓ Skill created: {skill}")
        
        # Test 2: Create questions for the skill
        print("\n[TEST 2] Creating test questions...")
        question1 = Question(
            skill_id=skill.id,
            question_text="What is 7 × 8?",
            question_type="multiple_choice",
            correct_answer="56",
            options=["42", "48", "56", "64"],
            explanation="7 × 8 = 56 because 7 added 8 times equals 56",
            difficulty="medium",
            grade_level=3
        )
        question2 = Question(
            skill_id=skill.id,
            question_text="What is 9 × 6?",
            question_type="multiple_choice",
            correct_answer="54",
            options=["45", "54", "63", "72"],
            explanation="9 × 6 = 54",
            difficulty="medium",
            grade_level=3
        )
        db.session.add_all([question1, question2])
        db.session.commit()
        print(f"✓ Question 1 created: {question1}")
        print(f"✓ Question 2 created: {question2}")
        
        # Test 3: Get or create a student
        print("\n[TEST 3] Getting student for assessment...")
        student = Student.query.first()
        if not student:
            # Create a test user and student
            user = User(username="testuser_assess", email="test_assess@example.com")
            user.set_password("password123")
            db.session.add(user)
            db.session.commit()
            
            student = Student(user_id=user.id, name="Test Student", grade=5)
            db.session.add(student)
            db.session.commit()
        print(f"✓ Using student: {student}")
        
        # Test 4: Create an assessment
        print("\n[TEST 4] Creating an assessment...")
        assessment = Assessment(
            student_id=student.id,
            assessment_type="diagnostic",
            grade_level=5,
            total_questions=2
        )
        db.session.add(assessment)
        db.session.commit()
        print(f"✓ Assessment created: {assessment}")
        
        # Test 5: Create assessment responses
        print("\n[TEST 5] Creating assessment responses...")
        response1 = AssessmentResponse(
            assessment_id=assessment.id,
            question_id=question1.id,
            student_answer="56",
            is_correct=True,
            time_spent_seconds=15
        )
        response2 = AssessmentResponse(
            assessment_id=assessment.id,
            question_id=question2.id,
            student_answer="45",
            is_correct=False,
            time_spent_seconds=20
        )
        db.session.add_all([response1, response2])
        db.session.commit()
        print(f"✓ Response 1 created: {response1}")
        print(f"✓ Response 2 created: {response2}")
        
        # Test 6: Update assessment score
        print("\n[TEST 6] Calculating assessment score...")
        assessment.correct_answers = 1  # 1 out of 2 correct
        assessment.mark_complete()
        print(f"✓ Assessment score: {assessment.score_percentage}%")
        print(f"✓ Assessment completed: {assessment.completed}")
        
        # Test 7: Test relationships
        print("\n[TEST 7] Testing relationships...")
        print(f"✓ Skill has {len(skill.questions)} questions")
        print(f"✓ Assessment has {len(assessment.responses)} responses")
        print(f"✓ Student has {len(student.assessments)} assessments")
        
        # Test 8: Test to_dict methods
        print("\n[TEST 8] Testing to_dict() methods...")
        skill_dict = skill.to_dict()
        print(f"✓ Skill dict: {skill_dict}")
        question_dict = question1.to_dict(include_answer=False)
        print(f"✓ Question dict (no answer): {question_dict}")
        question_dict_with_answer = question1.to_dict(include_answer=True)
        print(f"✓ Question dict (with answer): {question_dict_with_answer}")
        assessment_dict = assessment.to_dict()
        print(f"✓ Assessment dict: {assessment_dict}")
        response_dict = response1.to_dict()
        print(f"✓ Response dict: {response_dict}")
        
        # Cleanup
        print("\n[CLEANUP] Removing test data...")
        db.session.delete(response1)
        db.session.delete(response2)
        db.session.delete(assessment)
        db.session.delete(question1)
        db.session.delete(question2)
        db.session.delete(skill)
        db.session.commit()
        print("✓ Test data cleaned up")
        
        print("\n" + "=" * 60)
        print("ALL TESTS PASSED! ✓")
        print("=" * 60)

if __name__ == '__main__':
    test_assessment_models()

