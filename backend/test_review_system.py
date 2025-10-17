"""
Test script for Review System functionality.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from src.database import db, init_db
from src.models.user import User
from src.models.student import Student
from src.models.learning_path import LearningPath
from src.models.assessment import Skill
from src.models.review import ReviewSession
from src.services.review_service import ReviewService
from datetime import datetime, timedelta
from flask import Flask

# Create test app
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test_review.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'test-secret-key'

init_db(app)

def test_review_system():
    """Test the complete review system."""
    print("=" * 60)
    print("TESTING REVIEW SYSTEM")
    print("=" * 60)
    
    with app.app_context():
        # Clean up
        db.drop_all()
        db.create_all()
        
        # Create test data
        print("\n1. Creating test data...")
        
        # Create user
        user = User(username="testuser", email="test@example.com")
        user.set_password("password123")
        db.session.add(user)
        db.session.commit()
        
        # Create student
        student = Student(
            user_id=user.id,
            name="Test Student",
            grade=5
        )
        db.session.add(student)
        db.session.commit()
        
        # Create skill
        skill = Skill(
            name="Basic Multiplication",
            description="Master multiplication facts",
            grade_level=3,
            subject_area="arithmetic"
        )
        db.session.add(skill)
        db.session.commit()
        
        # Create mastered learning path item
        learning_path_item = LearningPath(
            student_id=student.id,
            skill_id=skill.id,
            status='mastered',
            mastery_achieved=True,
            mastery_date=datetime.utcnow() - timedelta(days=2),
            current_accuracy=95.0,
            questions_answered=10,
            correct_answers=9,
            attempts=2
        )
        db.session.add(learning_path_item)
        db.session.commit()
        
        print(f"✓ Created user: {user.username}")
        print(f"✓ Created student: {student.name}")
        print(f"✓ Created skill: {skill.name}")
        print(f"✓ Created mastered learning path item")
        
        # Test 1: Schedule first review
        print("\n2. Testing review scheduling...")
        ReviewService.schedule_first_review(learning_path_item)
        
        assert learning_path_item.next_review_date is not None
        assert learning_path_item.review_count == 0
        assert learning_path_item.review_interval_days == 1
        
        print(f"✓ First review scheduled for: {learning_path_item.next_review_date}")
        print(f"✓ Review interval: {learning_path_item.review_interval_days} days")
        
        # Test 2: Calculate next review dates
        print("\n3. Testing review interval calculation...")
        
        intervals = {}
        for review_num in range(5):
            next_date = ReviewService.calculate_next_review_date(review_num)
            days_ahead = (next_date - datetime.utcnow()).days
            intervals[review_num] = days_ahead
            print(f"✓ Review #{review_num + 1}: {days_ahead} days from now")
        
        # Verify spaced repetition intervals (allow for rounding)
        assert intervals[0] in [0, 1], "First review should be ~1 day"
        assert intervals[1] in [2, 3], "Second review should be ~3 days"
        assert intervals[2] in [6, 7], "Third review should be ~7 days"
        assert intervals[3] in [13, 14], "Fourth review should be ~14 days"
        assert intervals[4] in [29, 30], "Fifth+ review should be ~30 days"
        
        # Test 3: Get reviews due
        print("\n4. Testing get reviews due...")
        
        # Set review date to past (make it due)
        learning_path_item.next_review_date = datetime.utcnow() - timedelta(hours=1)
        db.session.commit()
        
        reviews_due = ReviewService.get_reviews_due(student.id)
        assert len(reviews_due) == 1
        assert reviews_due[0].id == learning_path_item.id
        
        print(f"✓ Found {len(reviews_due)} review(s) due")
        print(f"✓ Review for skill: {reviews_due[0].skill.name}")
        
        # Test 4: Start review session
        print("\n5. Testing review session creation...")
        
        review_session = ReviewService.start_review_session(
            learning_path_item.id,
            student.id
        )
        
        assert review_session is not None
        assert review_session.student_id == student.id
        assert review_session.skill_id == skill.id
        assert review_session.review_number == 1
        
        print(f"✓ Created review session #{review_session.id}")
        print(f"✓ Review number: {review_session.review_number}")
        
        # Test 5: Complete review (passed)
        print("\n6. Testing review completion (passed)...")
        
        result = ReviewService.complete_review_session(
            review_session.id,
            correct=4,
            total=5
        )
        
        assert result is not None
        assert result['passed'] == True
        assert result['review_session']['accuracy'] == 80.0
        assert result['skill_status'] == 'mastered'
        assert result['next_review_date'] is not None
        
        print(f"✓ Review completed: {result['review_session']['accuracy']}% accuracy")
        print(f"✓ Status: {result['passed'] and 'PASSED' or 'FAILED'}")
        print(f"✓ Skill status: {result['skill_status']}")
        print(f"✓ Next review: {result['next_review_date']}")
        
        # Verify learning path updated
        db.session.refresh(learning_path_item)
        assert learning_path_item.review_count == 1
        assert learning_path_item.last_reviewed_at is not None
        
        print(f"✓ Review count updated: {learning_path_item.review_count}")
        
        # Test 6: Complete review (failed)
        print("\n7. Testing review completion (failed)...")
        
        # Create another review session
        learning_path_item.next_review_date = datetime.utcnow() - timedelta(hours=1)
        db.session.commit()
        
        review_session2 = ReviewService.start_review_session(
            learning_path_item.id,
            student.id
        )
        
        result2 = ReviewService.complete_review_session(
            review_session2.id,
            correct=2,
            total=5
        )
        
        assert result2 is not None
        assert result2['passed'] == False
        assert result2['review_session']['accuracy'] == 40.0
        assert result2['skill_status'] == 'needs_review'
        assert result2['next_review_date'] is None
        
        print(f"✓ Review completed: {result2['review_session']['accuracy']}% accuracy")
        print(f"✓ Status: {result2['passed'] and 'PASSED' or 'FAILED'}")
        print(f"✓ Skill status: {result2['skill_status']}")
        print(f"✓ Mastery revoked (needs more practice)")
        
        # Test 7: Get upcoming reviews
        print("\n8. Testing get upcoming reviews...")
        
        # Create another mastered skill with future review
        skill2 = Skill(
            name="Division Basics",
            description="Master division facts",
            grade_level=4,
            subject_area="arithmetic"
        )
        db.session.add(skill2)
        db.session.commit()
        
        learning_path_item2 = LearningPath(
            student_id=student.id,
            skill_id=skill2.id,
            status='mastered',
            mastery_achieved=True,
            mastery_date=datetime.utcnow(),
            current_accuracy=92.0,
            questions_answered=10,
            next_review_date=datetime.utcnow() + timedelta(days=3),
            review_count=0
        )
        db.session.add(learning_path_item2)
        db.session.commit()
        
        upcoming = ReviewService.get_upcoming_reviews(student.id, days_ahead=7)
        assert len(upcoming) >= 1
        
        print(f"✓ Found {len(upcoming)} upcoming review(s)")
        for item in upcoming:
            days_until = (item.next_review_date - datetime.utcnow()).days
            print(f"  - {item.skill.name}: in {days_until} days")
        
        # Test 8: Get review history
        print("\n9. Testing review history...")
        
        history = ReviewService.get_review_history(student.id, limit=10)
        assert len(history) == 2  # We completed 2 reviews
        
        print(f"✓ Found {len(history)} review(s) in history")
        for session in history:
            status = "PASSED" if session.passed else "FAILED"
            print(f"  - {session.skill.name}: {session.accuracy}% ({status})")
        
        print("\n" + "=" * 60)
        print("ALL TESTS PASSED! ✓")
        print("=" * 60)
        print("\nReview System Features Verified:")
        print("  ✓ Review scheduling with spaced repetition")
        print("  ✓ Automatic review interval calculation (1, 3, 7, 14, 30 days)")
        print("  ✓ Get reviews due")
        print("  ✓ Start review sessions")
        print("  ✓ Complete reviews (pass/fail)")
        print("  ✓ Maintain mastery with 80%+ accuracy")
        print("  ✓ Revoke mastery if accuracy drops below 80%")
        print("  ✓ Get upcoming reviews")
        print("  ✓ Review history tracking")
        print("=" * 60)

if __name__ == '__main__':
    test_review_system()

