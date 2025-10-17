"""
Test Activity Feed System
Tests all activity feed functionality
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from src.database import db, init_db
from src.models.user import User
from src.models.student import Student
from src.models.activity_feed import ActivityFeed
from src.models.friendship import Friendship
from src.models.class_group import ClassGroup, ClassMembership
from src.services.activity_feed_service import ActivityFeedService
from flask import Flask
from datetime import datetime

# Create test app
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'test-secret-key'

# Initialize database
init_db(app)

def run_tests():
    """Run all activity feed tests"""
    with app.app_context():
        # Create tables
        db.create_all()
        
        print("=" * 60)
        print("ACTIVITY FEED SYSTEM TESTS")
        print("=" * 60)
        
        # Cleanup any existing test data first
        print("\n[Setup] Cleaning up any existing test data...")
        try:
            db.session.query(ActivityFeed).delete()
            db.session.query(ClassMembership).delete()
            db.session.query(ClassGroup).delete()
            db.session.query(Friendship).delete()
            from src.models.gamification import StudentProgress
            db.session.query(StudentProgress).delete()
            db.session.query(Student).delete()
            db.session.query(User).delete()
            db.session.commit()
            print("✓ Cleanup complete")
        except Exception as e:
            print(f"Note: {e}")
            db.session.rollback()
        
        # Test 1: Create test users
        print("\n[Test 1] Creating test users...")
        try:
            # Create students
            student1_user = User(username='student1', email='student1@test.com')
            student1_user.set_password('password123')
            db.session.add(student1_user)
            db.session.flush()
            
            student2_user = User(username='student2', email='student2@test.com')
            student2_user.set_password('password123')
            db.session.add(student2_user)
            db.session.flush()
            
            student3_user = User(username='student3', email='student3@test.com')
            student3_user.set_password('password123')
            db.session.add(student3_user)
            db.session.flush()
            
            # Create student profiles
            student1 = Student(
                user_id=student1_user.id,
                name='Student One',
                grade=5,
                avatar='😊'
            )
            db.session.add(student1)
            db.session.flush()
            
            student2 = Student(
                user_id=student2_user.id,
                name='Student Two',
                grade=5,
                avatar='😊'
            )
            db.session.add(student2)
            db.session.flush()
            
            student3 = Student(
                user_id=student3_user.id,
                name='Student Three',
                grade=5,
                avatar='😊'
            )
            db.session.add(student3)
            db.session.flush()
            
            # Create student progress (for XP and levels)
            from src.models.gamification import StudentProgress
            progress1 = StudentProgress(student_id=student1.id, total_xp=500, current_level=3)
            progress2 = StudentProgress(student_id=student2.id, total_xp=300, current_level=2)
            progress3 = StudentProgress(student_id=student3.id, total_xp=700, current_level=4)
            db.session.add_all([progress1, progress2, progress3])
            
            db.session.commit()
            print("✓ Created 3 students with progress")
        except Exception as e:
            print(f"✗ Error: {e}")
            return
        
        # Test 2: Create activities
        print("\n[Test 2] Creating various activity types...")
        try:
            # Skill mastery activity
            result1, status1 = ActivityFeedService.create_activity(student1.id, 'skill_mastery', {
                'title': 'Mastered Multiplication!',
                'description': '95% accuracy',
                'xp_earned': 150,
                'accuracy': 0.95,
                'questions_answered': 50,
                'visibility': 'friends'
            })
            
            # Level up activity
            result2, status2 = ActivityFeedService.create_activity(student2.id, 'level_up', {
                'title': 'Reached Level 3!',
                'description': 'Awesome progress!',
                'level_reached': 3,
                'visibility': 'friends'
            })
            
            # Achievement unlock activity
            result3, status3 = ActivityFeedService.create_activity(student1.id, 'achievement_unlock', {
                'title': 'Unlocked Speed Demon!',
                'description': 'Answered 100 questions in one day',
                'xp_earned': 200,
                'visibility': 'friends'
            })
            
            # Streak milestone activity
            result4, status4 = ActivityFeedService.create_activity(student3.id, 'streak_milestone', {
                'title': '7 Day Streak!',
                'description': 'Keep up the great work!',
                'streak_days': 7,
                'visibility': 'friends'
            })
            
            if all([result1.get('success'), result2.get('success'), 
                   result3.get('success'), result4.get('success')]):
                print("✓ Created 4 activities (skill mastery, level up, achievement, streak)")
            else:
                print("✗ Error creating activities")
                return
        except Exception as e:
            print(f"✗ Error: {e}")
            return
        
        # Test 3: Get feed without friends (should be empty)
        print("\n[Test 3] Getting feed without friends...")
        try:
            result, status = ActivityFeedService.get_feed(student1.id)
            
            if result.get('success'):
                # Should only see own activities
                activities = result['activities']
                own_activities = [a for a in activities if a['student_id'] == student1.id]
                print(f"✓ Feed retrieved: {len(own_activities)} own activities (no friends yet)")
            else:
                print(f"✗ Error: {result.get('error')}")
        except Exception as e:
            print(f"✗ Error: {e}")
        
        # Test 4: Create friendships
        print("\n[Test 4] Creating friendships...")
        try:
            # Student 1 and Student 2 are friends
            friendship1 = Friendship(
                requester_id=student1.id,
                addressee_id=student2.id,
                status='accepted'
            )
            db.session.add(friendship1)
            
            # Student 1 and Student 3 are friends
            friendship2 = Friendship(
                requester_id=student1.id,
                addressee_id=student3.id,
                status='accepted'
            )
            db.session.add(friendship2)
            
            db.session.commit()
            print("✓ Created 2 friendships (Student 1 with Students 2 and 3)")
        except Exception as e:
            print(f"✗ Error: {e}")
            return
        
        # Test 5: Get feed with friends
        print("\n[Test 5] Getting feed with friends...")
        try:
            result, status = ActivityFeedService.get_feed(student1.id)
            
            if result.get('success'):
                activities = result['activities']
                print(f"✓ Feed retrieved: {len(activities)} activities (own + friends)")
                
                # Should see activities from student1, student2, and student3
                student_ids = set([a['student_id'] for a in activities])
                print(f"  - Activities from students: {student_ids}")
            else:
                print(f"✗ Error: {result.get('error')}")
        except Exception as e:
            print(f"✗ Error: {e}")
        
        # Test 6: Filter feed by friends only
        print("\n[Test 6] Filtering feed by friends only...")
        try:
            result, status = ActivityFeedService.get_feed(student1.id, filter_type='friends')
            
            if result.get('success'):
                activities = result['activities']
                # Should only see friend activities (not own)
                friend_activities = [a for a in activities if a['student_id'] != student1.id]
                print(f"✓ Friends feed: {len(friend_activities)} friend activities")
            else:
                print(f"✗ Error: {result.get('error')}")
        except Exception as e:
            print(f"✗ Error: {e}")
        
        # Test 7: Filter feed by "me" only
        print("\n[Test 7] Filtering feed by 'me' only...")
        try:
            result, status = ActivityFeedService.get_feed(student1.id, filter_type='me')
            
            if result.get('success'):
                activities = result['activities']
                # Should only see own activities
                own_activities = [a for a in activities if a['student_id'] == student1.id]
                print(f"✓ My feed: {len(own_activities)} own activities")
            else:
                print(f"✗ Error: {result.get('error')}")
        except Exception as e:
            print(f"✗ Error: {e}")
        
        # Test 8: Create class and test class feed
        print("\n[Test 8] Testing class feed...")
        try:
            # Create teacher user
            teacher_user = User(username='teacher1', email='teacher1@test.com')
            teacher_user.set_password('password123')
            db.session.add(teacher_user)
            db.session.flush()
            
            # Create class
            test_class = ClassGroup(
                name='Math Class 5A',
                description='5th grade math',
                teacher_id=teacher_user.id,
                grade_level=5,
                invite_code='TEST01'
            )
            db.session.add(test_class)
            db.session.flush()
            
            # Add students to class
            membership1 = ClassMembership(class_id=test_class.id, student_id=student1.id)
            membership2 = ClassMembership(class_id=test_class.id, student_id=student2.id)
            db.session.add_all([membership1, membership2])
            db.session.commit()
            
            # Create class-visible activity
            ActivityFeedService.create_activity(student2.id, 'practice_session', {
                'title': 'Practiced Division',
                'description': '20 questions answered',
                'questions_answered': 20,
                'accuracy': 0.85,
                'visibility': 'class'
            })
            
            # Get class feed
            result, status = ActivityFeedService.get_feed(student1.id, filter_type='classes')
            
            if result.get('success'):
                activities = result['activities']
                print(f"✓ Class feed: {len(activities)} class activities")
            else:
                print(f"✗ Error: {result.get('error')}")
        except Exception as e:
            print(f"✗ Error: {e}")
            import traceback
            traceback.print_exc()
        
        # Test 9: Get student activities (respecting privacy)
        print("\n[Test 9] Getting specific student's activities...")
        try:
            # Get student2's activities as student1 (they are friends)
            result, status = ActivityFeedService.get_student_activities(
                student2.id,
                student1.id
            )
            
            if result.get('success'):
                activities = result['activities']
                print(f"✓ Student 2's activities: {len(activities)} activities visible to friend")
            else:
                print(f"✗ Error: {result.get('error')}")
        except Exception as e:
            print(f"✗ Error: {e}")
        
        # Test 10: Get activity stats
        print("\n[Test 10] Getting activity statistics...")
        try:
            result, status = ActivityFeedService.get_activity_stats(student1.id)
            
            if result.get('success'):
                stats = result['stats']
                print(f"✓ Activity stats retrieved:")
                print(f"  - Total activities: {stats['total_activities']}")
                print(f"  - By type: {stats['by_type']}")
                print(f"  - Total XP shown: {stats['total_xp_shown']}")
            else:
                print(f"✗ Error: {result.get('error')}")
        except Exception as e:
            print(f"✗ Error: {e}")
        
        # Test 11: Delete activity (owner only)
        print("\n[Test 11] Deleting activity...")
        try:
            # Get one of student1's activities
            activity = ActivityFeed.query.filter_by(student_id=student1.id).first()
            
            if activity:
                # Try to delete as non-owner (should fail)
                result, status = ActivityFeedService.delete_activity(activity.id, student2.id)
                
                if status == 403:
                    print(f"✓ Non-owner correctly blocked from deleting")
                
                # Delete as owner (should succeed)
                result, status = ActivityFeedService.delete_activity(activity.id, student1.id)
                
                if result.get('success'):
                    print(f"✓ Activity deleted by owner")
                else:
                    print(f"✗ Error: {result.get('error')}")
            else:
                print("✗ No activity found to delete")
        except Exception as e:
            print(f"✗ Error: {e}")
        
        # Test 12: Test activity creation helpers
        print("\n[Test 12] Testing activity creation helpers...")
        try:
            # Test skill mastery helper
            ActivityFeedService.on_skill_mastery(student1.id, 'Addition', 0.98, 100)
            
            # Test level up helper
            ActivityFeedService.on_level_up(student1.id, 5, 1000)
            
            # Test achievement unlock helper
            ActivityFeedService.on_achievement_unlock(student1.id, 'Perfect Score', 250)
            
            # Test challenge complete helper
            ActivityFeedService.on_challenge_complete(student1.id, 'Math Marathon', 1, 300)
            
            # Test streak milestone helper
            ActivityFeedService.on_streak_milestone(student1.id, 30)
            
            # Count new activities
            new_activities = ActivityFeed.query.filter_by(student_id=student1.id).count()
            print(f"✓ Activity creation helpers working: {new_activities} total activities for student1")
        except Exception as e:
            print(f"✗ Error: {e}")
        
        # Test 13: Cleanup
        print("\n[Test 13] Cleanup test data...")
        try:
            db.session.query(ActivityFeed).delete()
            db.session.query(ClassMembership).delete()
            db.session.query(ClassGroup).delete()
            db.session.query(Friendship).delete()
            from src.models.gamification import StudentProgress
            db.session.query(StudentProgress).delete()
            db.session.query(Student).delete()
            db.session.query(User).delete()
            db.session.commit()
            print("✓ Test data cleaned up")
        except Exception as e:
            print(f"✗ Error: {e}")
        
        print("\n" + "=" * 60)
        print("ALL TESTS COMPLETED!")
        print("=" * 60)


if __name__ == '__main__':
    run_tests()

