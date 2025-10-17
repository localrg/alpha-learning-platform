"""
Comprehensive test script for the Interactive Examples System.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from src.main import app
from src.database import db
from src.models.student import Student
from src.models.assessment import Skill
from src.models.interactive_example import InteractiveExample, ExampleInteraction
from src.services.example_service import ExampleService

def test_example_system():
    """Test all aspects of the interactive examples system."""
    print("=" * 60)
    print("TESTING INTERACTIVE EXAMPLES SYSTEM")
    print("=" * 60)
    
    with app.app_context():
        # Test 1: Get example types
        print("\n1. Testing example types...")
        types = ExampleService.get_example_types()
        assert 'number_line' in types
        assert 'array' in types
        assert 'fraction_circles' in types
        print(f"  ✓ Found {len(types)} example types")
        for type_key, type_info in types.items():
            print(f"    - {type_info['name']}: {type_info['description']}")
        
        # Test 2: Create example
        print("\n2. Testing example creation...")
        skill = Skill.query.filter_by(name='Basic Multiplication').first()
        if not skill:
            print("  ⚠ Skill 'Basic Multiplication' not found, skipping...")
            return
        
        # Check if example already exists
        existing = InteractiveExample.query.filter_by(
            skill_id=skill.id,
            title='Test Number Line'
        ).first()
        
        if existing:
            db.session.delete(existing)
            db.session.commit()
        
        example = ExampleService.create_example(
            skill_id=skill.id,
            title='Test Number Line',
            example_type='number_line',
            config={
                'min': 0,
                'max': 20,
                'start_value': 5,
                'operation': 'add',
                'operand': 3
            },
            description='Test example for addition',
            difficulty='beginner'
        )
        
        assert example.id is not None
        assert example.title == 'Test Number Line'
        assert example.example_type == 'number_line'
        assert example.config['min'] == 0
        assert example.config['max'] == 20
        print(f"  ✓ Created example: {example.title}")
        print(f"  ✓ Example ID: {example.id}")
        print(f"  ✓ Config: {example.config}")
        
        # Test 3: Get examples for skill
        print("\n3. Testing get examples for skill...")
        examples = ExampleService.get_examples_for_skill(skill.id)
        assert len(examples) > 0
        print(f"  ✓ Found {len(examples)} example(s) for skill: {skill.name}")
        for ex in examples:
            print(f"    - {ex['title']} ({ex['example_type']}, {ex['difficulty']})")
        
        # Test 4: Get example by ID
        print("\n4. Testing get example by ID...")
        example_data = ExampleService.get_example_by_id(example.id)
        assert example_data is not None
        assert example_data['id'] == example.id
        assert example_data['title'] == example.title
        print(f"  ✓ Retrieved example: {example_data['title']}")
        print(f"  ✓ Type: {example_data['example_type']}")
        print(f"  ✓ Difficulty: {example_data['difficulty']}")
        
        # Test 5: Create test student
        print("\n5. Creating test student...")
        from src.models.user import User
        
        # Clean up existing test user and student
        test_user = User.query.filter_by(username='example_test_user').first()
        if test_user:
            # Delete student first if exists
            test_student_old = Student.query.filter_by(user_id=test_user.id).first()
            if test_student_old:
                db.session.delete(test_student_old)
            db.session.delete(test_user)
            db.session.commit()
        
        test_user = User(username='example_test_user', email='example_test@test.com')
        test_user.set_password('password')
        db.session.add(test_user)
        db.session.commit()
        
        test_student = Student(
            user_id=test_user.id,
            name='Example Test Student',
            grade=3
        )
        db.session.add(test_student)
        db.session.commit()
        
        print(f"  ✓ Created test student: {test_student.name}")
        
        # Test 6: Start interaction
        print("\n6. Testing start interaction...")
        interaction = ExampleService.start_interaction(example.id, test_student.id)
        assert interaction.id is not None
        assert interaction.example_id == example.id
        assert interaction.student_id == test_student.id
        assert interaction.completed == False
        print(f"  ✓ Started interaction ID: {interaction.id}")
        print(f"  ✓ Student: {test_student.name}")
        print(f"  ✓ Example: {example.title}")
        
        # Test 7: Log interactions
        print("\n7. Testing log interaction...")
        interaction = ExampleService.log_interaction(
            interaction.id,
            {
                'action': 'drag_marker',
                'from': 5,
                'to': 8
            }
        )
        assert len(interaction.interaction_data) == 1
        assert interaction.interaction_data[0]['action'] == 'drag_marker'
        print(f"  ✓ Logged action: drag_marker")
        
        # Log another action
        interaction = ExampleService.log_interaction(
            interaction.id,
            {
                'action': 'show_animation',
                'operation': 'add'
            }
        )
        assert len(interaction.interaction_data) == 2
        print(f"  ✓ Logged action: show_animation")
        print(f"  ✓ Total actions logged: {len(interaction.interaction_data)}")
        
        # Test 8: Update time spent
        print("\n8. Testing update time spent...")
        interaction = ExampleService.update_time_spent(interaction.id, 120)
        assert interaction.time_spent_seconds == 120
        print(f"  ✓ Updated time: {interaction.time_spent_seconds} seconds")
        
        # Test 9: Complete interaction
        print("\n9. Testing complete interaction...")
        interaction = ExampleService.complete_interaction(interaction.id)
        assert interaction.completed == True
        assert interaction.completed_at is not None
        print(f"  ✓ Interaction completed")
        print(f"  ✓ Completed at: {interaction.completed_at}")
        
        # Test 10: Get example with student data
        print("\n10. Testing get example with student data...")
        example_with_data = ExampleService.get_example_by_id(example.id, student_id=test_student.id)
        assert example_with_data['interacted'] == True
        assert example_with_data['completed'] == True
        assert example_with_data['time_spent'] == 120
        print(f"  ✓ Example includes student data")
        print(f"  ✓ Interacted: {example_with_data['interacted']}")
        print(f"  ✓ Completed: {example_with_data['completed']}")
        print(f"  ✓ Time spent: {example_with_data['time_spent']}s")
        
        # Test 11: Get student stats
        print("\n11. Testing student statistics...")
        stats = ExampleService.get_student_stats(test_student.id)
        assert stats['total_examples_tried'] >= 1
        assert stats['total_examples_completed'] >= 1
        assert stats['total_time_seconds'] >= 120
        print(f"  ✓ Total examples tried: {stats['total_examples_tried']}")
        print(f"  ✓ Total examples completed: {stats['total_examples_completed']}")
        print(f"  ✓ Total time: {stats['total_time_minutes']} minutes")
        print(f"  ✓ Completion rate: {stats['completion_rate']}%")
        
        # Test 12: Get recent examples
        print("\n12. Testing recent examples...")
        recent = ExampleService.get_recent_examples(test_student.id, limit=5)
        assert len(recent) >= 1
        print(f"  ✓ Found {len(recent)} recent example(s)")
        for ex in recent:
            print(f"    - {ex['title']} (completed: {ex.get('completed', False)})")
        
        # Test 13: Get recommended examples
        print("\n13. Testing recommended examples...")
        # First, create a learning path item for the student
        from src.models.learning_path import LearningPath
        
        # Clean up existing learning path
        existing_path = LearningPath.query.filter_by(
            student_id=test_student.id,
            skill_id=skill.id
        ).first()
        if existing_path:
            db.session.delete(existing_path)
            db.session.commit()
        
        learning_path_item = LearningPath(
            student_id=test_student.id,
            skill_id=skill.id,
            sequence_order=1,
            status='in_progress',
            mastery_achieved=False
        )
        db.session.add(learning_path_item)
        db.session.commit()
        
        recommended = ExampleService.get_recommended_examples(test_student.id, limit=5)
        print(f"  ✓ Found {len(recommended)} recommended example(s)")
        for ex in recommended:
            print(f"    - {ex['title']} for {ex['skill_name']}")
        
        # Test 14: Test array example creation
        print("\n14. Testing array example creation...")
        array_example = ExampleService.create_example(
            skill_id=skill.id,
            title='Test Array Grid',
            example_type='array',
            config={
                'rows': 3,
                'cols': 4,
                'editable': True,
                'show_equation': True
            },
            description='Test example for multiplication arrays',
            difficulty='beginner'
        )
        
        assert array_example.example_type == 'array'
        assert array_example.config['rows'] == 3
        assert array_example.config['cols'] == 4
        print(f"  ✓ Created array example: {array_example.title}")
        print(f"  ✓ Config: {array_example.config}")
        
        # Test 15: Test invalid example type
        print("\n15. Testing invalid example type...")
        try:
            ExampleService.create_example(
                skill_id=skill.id,
                title='Invalid Example',
                example_type='invalid_type'
            )
            print("  ✗ Should have raised ValueError")
            assert False
        except ValueError as e:
            print(f"  ✓ Correctly raised ValueError: {str(e)}")
        
        # Cleanup
        print("\n16. Cleaning up test data...")
        # Delete in correct order to avoid foreign key issues
        db.session.delete(learning_path_item)
        db.session.delete(example)
        db.session.delete(array_example)
        db.session.delete(test_student)
        db.session.delete(test_user)
        db.session.commit()
        print("  ✓ Test data cleaned up")
        
        print("\n" + "=" * 60)
        print("ALL TESTS PASSED! ✓")
        print("=" * 60)
        print("Interactive Examples System Features Verified:")
        print("  ✓ Example type definitions")
        print("  ✓ Example creation (number_line, array)")
        print("  ✓ Get examples for skill")
        print("  ✓ Get example by ID")
        print("  ✓ Start interaction tracking")
        print("  ✓ Log interaction actions")
        print("  ✓ Update time spent")
        print("  ✓ Complete interaction")
        print("  ✓ Get example with student data")
        print("  ✓ Student statistics")
        print("  ✓ Recent examples")
        print("  ✓ Recommended examples")
        print("  ✓ Invalid type handling")
        print("=" * 60)

if __name__ == '__main__':
    test_example_system()

