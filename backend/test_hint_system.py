"""
Comprehensive test script for the Hint System.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from src.main import app
from src.database import db
from src.models.user import User
from src.models.student import Student
from src.models.assessment import Question, Skill
from src.models.hint import Hint, HintUsage
from src.services.hint_service import HintService

def test_hint_system():
    """Test all aspects of the hint system."""
    print("=" * 60)
    print("TESTING HINT SYSTEM")
    print("=" * 60)
    
    with app.app_context():
        # Test 1: Create test question
        print("\n1. Creating test question...")
        skill = Skill.query.first()
        if not skill:
            skill = Skill(
                name='Test Multiplication',
                description='Basic multiplication',
                category='arithmetic',
                grade_level=3,
                difficulty='beginner'
            )
            db.session.add(skill)
            db.session.commit()
        
        # Clean up existing test question and its hints
        test_question = Question.query.filter_by(question_text='What is 3 × 4?').first()
        if test_question:
            # Delete hints first
            Hint.query.filter_by(question_id=test_question.id).delete()
            HintUsage.query.filter_by(question_id=test_question.id).delete()
            db.session.delete(test_question)
            db.session.commit()
        
        question = Question(
            skill_id=skill.id,
            question_text='What is 3 × 4?',
            question_type='multiple_choice',
            options=["8", "10", "12", "15"],
            correct_answer='12',
            explanation='3 × 4 means adding 3 four times: 3 + 3 + 3 + 3 = 12',
            difficulty='easy',
            grade_level=3
        )
        db.session.add(question)
        db.session.commit()
        
        print(f"  ✓ Created question: {question.question_text}")
        print(f"  ✓ Question ID: {question.id}")
        
        # Test 2: Identify question type
        print("\n2. Testing question type identification...")
        question_type = HintService.identify_question_type(question)
        assert question_type == 'multiplication'
        print(f"  ✓ Identified type: {question_type}")
        
        # Test 3: Generate hints
        print("\n3. Testing hint generation...")
        hints_data = HintService.generate_hints_for_question(question)
        assert len(hints_data) == 4
        print(f"  ✓ Generated {len(hints_data)} hints")
        for hint in hints_data:
            print(f"    Level {hint['level']}: {hint['text'][:60]}...")
        
        # Test 4: Create hints in database
        print("\n4. Testing hint creation...")
        created_hints = HintService.create_hints_for_question(question.id, hints_data)
        assert len(created_hints) == 4
        print(f"  ✓ Created {len(created_hints)} hints in database")
        
        # Test 5: Get hints for question
        print("\n5. Testing get hints for question...")
        hints = HintService.get_hints_for_question(question.id)
        assert len(hints) == 4
        assert hints[0]['hint_level'] == 1
        assert hints[3]['hint_level'] == 4
        print(f"  ✓ Retrieved {len(hints)} hints")
        print(f"  ✓ Hints ordered by level: {[h['hint_level'] for h in hints]}")
        
        # Test 6: Get next hint
        print("\n6. Testing get next hint...")
        next_hint_data = HintService.get_next_hint(question.id, current_level=0)
        assert next_hint_data is not None
        assert next_hint_data['hint']['hint_level'] == 1
        assert next_hint_data['next_level_available'] == True
        assert next_hint_data['total_levels'] == 4
        print(f"  ✓ Got next hint: Level {next_hint_data['hint']['hint_level']}")
        print(f"  ✓ More hints available: {next_hint_data['next_level_available']}")
        print(f"  ✓ Total levels: {next_hint_data['total_levels']}")
        
        # Test 7: Create test student
        print("\n7. Creating test student...")
        # Clean up existing test user
        test_user = User.query.filter_by(username='hint_test_user').first()
        if test_user:
            test_student_old = Student.query.filter_by(user_id=test_user.id).first()
            if test_student_old:
                db.session.delete(test_student_old)
            db.session.delete(test_user)
            db.session.commit()
        
        test_user = User(username='hint_test_user', email='hint_test@test.com')
        test_user.set_password('password')
        db.session.add(test_user)
        db.session.commit()
        
        test_student = Student(
            user_id=test_user.id,
            name='Hint Test Student',
            grade=3
        )
        db.session.add(test_student)
        db.session.commit()
        
        print(f"  ✓ Created test student: {test_student.name}")
        
        # Test 8: Record hint usage
        print("\n8. Testing record hint usage...")
        usage = HintService.record_hint_usage(
            student_id=test_student.id,
            question_id=question.id,
            hint_id=created_hints[0].id,
            hint_level=1,
            attempt_number=1,
            time_before_hint=30
        )
        assert usage.id is not None
        assert usage.hint_level == 1
        assert usage.time_before_hint == 30
        print(f"  ✓ Recorded hint usage ID: {usage.id}")
        print(f"  ✓ Hint level: {usage.hint_level}")
        print(f"  ✓ Time before hint: {usage.time_before_hint}s")
        
        # Test 9: Update hint feedback
        print("\n9. Testing update hint feedback...")
        updated_usage = HintService.update_hint_feedback(
            usage_id=usage.id,
            helpful=True,
            answered_correctly=True,
            attempts_after_hint=1
        )
        assert updated_usage.helpful == True
        assert updated_usage.answered_correctly == True
        assert updated_usage.attempts_after_hint == 1
        print(f"  ✓ Updated feedback: helpful={updated_usage.helpful}")
        print(f"  ✓ Answered correctly: {updated_usage.answered_correctly}")
        print(f"  ✓ Attempts after hint: {updated_usage.attempts_after_hint}")
        
        # Test 10: Record more hint usages
        print("\n10. Testing multiple hint usages...")
        for i, hint in enumerate(created_hints[1:3], start=2):
            usage = HintService.record_hint_usage(
                student_id=test_student.id,
                question_id=question.id,
                hint_id=hint.id,
                hint_level=i,
                attempt_number=i
            )
            HintService.update_hint_feedback(
                usage_id=usage.id,
                helpful=i % 2 == 0,  # Alternate helpful/not helpful
                answered_correctly=False
            )
        print(f"  ✓ Recorded 2 more hint usages")
        
        # Test 11: Get student hint stats
        print("\n11. Testing student hint statistics...")
        stats = HintService.get_student_hint_stats(test_student.id)
        assert stats['total_hints_used'] == 3
        assert stats['hints_by_level'][1] == 1
        assert stats['hints_by_level'][2] == 1
        assert stats['hints_by_level'][3] == 1
        print(f"  ✓ Total hints used: {stats['total_hints_used']}")
        print(f"  ✓ Hints by level: {stats['hints_by_level']}")
        print(f"  ✓ Average level: {stats['average_level']}")
        print(f"  ✓ Helpful rate: {stats['helpful_rate']}")
        print(f"  ✓ Success rate after hint: {stats['success_rate_after_hint']}")
        
        # Test 12: Get question hint stats
        print("\n12. Testing question hint statistics...")
        q_stats = HintService.get_question_hint_stats(question.id)
        assert q_stats['total_students_used_hints'] == 1
        assert q_stats['total_hint_requests'] == 3
        print(f"  ✓ Students who used hints: {q_stats['total_students_used_hints']}")
        print(f"  ✓ Total hint requests: {q_stats['total_hint_requests']}")
        print(f"  ✓ Average hint level: {q_stats['average_hint_level']}")
        print(f"  ✓ Helpful rate: {q_stats['helpful_rate']}")
        print(f"  ✓ Success rate: {q_stats['success_rate_after_hint']}")
        
        # Test 13: Test addition question type
        print("\n13. Testing addition question type...")
        add_question = Question(
            skill_id=skill.id,
            question_text='What is 47 + 28?',
            question_type='multiple_choice',
            options=["65", "75", "85", "95"],
            correct_answer='75',
            explanation='47 + 28: Add ones (7+8=15), write 5 carry 1. Add tens (4+2+1=7). Answer: 75',
            difficulty='medium',
            grade_level=3
        )
        db.session.add(add_question)
        db.session.commit()
        
        add_type = HintService.identify_question_type(add_question)
        assert add_type == 'addition'
        print(f"  ✓ Identified type: {add_type}")
        
        add_hints = HintService.generate_hints_for_question(add_question)
        assert len(add_hints) == 4
        print(f"  ✓ Generated {len(add_hints)} hints for addition")
        
        # Test 14: Test generic hints
        print("\n14. Testing generic hints...")
        generic_question = Question(
            skill_id=skill.id,
            question_text='Which pattern comes next?',
            question_type='multiple_choice',
            options=["A", "B", "C", "D"],
            correct_answer='A',
            explanation='The pattern repeats every 3 items',
            difficulty='medium',
            grade_level=3
        )
        db.session.add(generic_question)
        db.session.commit()
        
        generic_type = HintService.identify_question_type(generic_question)
        assert generic_type == 'general'
        print(f"  ✓ Identified type: {generic_type}")
        
        generic_hints = HintService.generate_hints_for_question(generic_question)
        assert len(generic_hints) == 4
        print(f"  ✓ Generated {len(generic_hints)} generic hints")
        
        # Test 15: Test extract numbers
        print("\n15. Testing number extraction...")
        numbers = HintService.extract_numbers('What is 12.5 + 3.75?')
        assert 12.5 in numbers
        assert 3.75 in numbers
        print(f"  ✓ Extracted numbers: {numbers}")
        
        # Cleanup
        print("\n16. Cleaning up test data...")
        # Delete in correct order to avoid foreign key issues
        # Delete hints first (they reference questions)
        Hint.query.filter_by(question_id=question.id).delete()
        Hint.query.filter_by(question_id=add_question.id).delete()
        Hint.query.filter_by(question_id=generic_question.id).delete()
        # Delete hint usages
        HintUsage.query.filter_by(student_id=test_student.id).delete()
        # Then delete questions, student, and user
        db.session.delete(question)
        db.session.delete(add_question)
        db.session.delete(generic_question)
        db.session.delete(test_student)
        db.session.delete(test_user)
        db.session.commit()
        print("  ✓ Test data cleaned up")
        
        print("\n" + "=" * 60)
        print("ALL TESTS PASSED! ✓")
        print("=" * 60)
        print("Hint System Features Verified:")
        print("  ✓ Question type identification (multiplication, addition, general)")
        print("  ✓ Automatic hint generation (4 levels)")
        print("  ✓ Hint creation and storage")
        print("  ✓ Get hints for question")
        print("  ✓ Progressive hint retrieval")
        print("  ✓ Hint usage tracking")
        print("  ✓ Hint feedback recording")
        print("  ✓ Student statistics")
        print("  ✓ Question statistics")
        print("  ✓ Number extraction")
        print("  ✓ Generic hint fallback")
        print("=" * 60)

if __name__ == '__main__':
    test_hint_system()

