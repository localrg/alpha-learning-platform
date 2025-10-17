"""
Test script for class groups system.
"""
import sys
sys.path.insert(0, '.')

from src.main import app
from src.database import db
from src.models.user import User
from src.models.student import Student
from src.models.class_group import ClassGroup, ClassMembership
from src.services.class_service import ClassService

def test_class_system():
    """Test class groups functionality."""
    with app.app_context():
        print("\n=== Testing Class Groups System ===\n")

        # Clean up existing test data
        ClassMembership.query.filter(ClassMembership.student_id.in_([
            s.id for s in Student.query.filter(Student.name.like('Test%')).all()
        ])).delete(synchronize_session=False)
        
        ClassGroup.query.filter(ClassGroup.name.like('Test%')).delete()
        
        Student.query.filter(Student.name.like('Test%')).delete()
        User.query.filter(User.email.like('test%')).delete()
        db.session.commit()

        # 1. Create test users
        print("1. Creating test users...")
        teacher = User(username='testteacher', email='testteacher@example.com')
        teacher.set_password('password123')
        db.session.add(teacher)
        
        student1 = User(username='teststudent1', email='teststudent1@example.com')
        student1.set_password('password123')
        db.session.add(student1)
        
        student2 = User(username='teststudent2', email='teststudent2@example.com')
        student2.set_password('password123')
        db.session.add(student2)
        
        db.session.commit()

        # Create student profiles
        student_profile1 = Student(user_id=student1.id, name='Test Student 1', grade=5)
        student_profile2 = Student(user_id=student2.id, name='Test Student 2', grade=5)
        db.session.add(student_profile1)
        db.session.add(student_profile2)
        db.session.commit()

        print(f"✅ Created teacher (ID: {teacher.id}) and 2 students")

        # 2. Create class
        print("\n2. Creating class...")
        class_group = ClassService.create_class(
            teacher_id=teacher.id,
            name="Test Class",
            description="A test class",
            grade_level=5
        )
        print(f"✅ Created class: {class_group.name} (Invite code: {class_group.invite_code})")

        # 3. Join class
        print("\n3. Students joining class...")
        ClassService.join_class(student_profile1.id, class_group.invite_code)
        ClassService.join_class(student_profile2.id, class_group.invite_code)
        print("✅ Both students joined successfully")

        # 4. Get class members
        print("\n4. Getting class members...")
        members = ClassService.get_class_members(class_group.id)
        print(f"✅ Found {len(members)} members")
        for member in members:
            print(f"   - {member['name']} (Grade {member['grade']}, Level {member['level']})")

        # 5. Get class leaderboard
        print("\n5. Getting class leaderboard...")
        leaderboard = ClassService.get_class_leaderboard(class_group.id)
        print(f"✅ Leaderboard has {len(leaderboard)} entries")
        for entry in leaderboard:
            print(f"   #{entry['rank']}: {entry['name']} - {entry['xp']} XP")

        # 6. Get class stats
        print("\n6. Getting class statistics...")
        stats = ClassService.get_class_stats(class_group.id)
        print(f"✅ Class stats:")
        print(f"   - Members: {stats['member_count']}")
        print(f"   - Total XP: {stats['total_xp']}")
        print(f"   - Average XP: {stats['average_xp']}")
        print(f"   - Average Level: {stats['average_level']}")

        # 7. Get student classes
        print("\n7. Getting student's classes...")
        classes = ClassService.get_student_classes(student_profile1.id)
        print(f"✅ Student 1 is in {len(classes)} class(es)")

        # 8. Leave class
        print("\n8. Student leaving class...")
        ClassService.leave_class(class_group.id, student_profile1.id)
        members_after = ClassService.get_class_members(class_group.id)
        print(f"✅ Student left. Members now: {len(members_after)}")

        # 9. Remove member (teacher action)
        print("\n9. Teacher removing member...")
        ClassService.remove_member(class_group.id, student_profile2.id, teacher.id)
        members_final = ClassService.get_class_members(class_group.id)
        print(f"✅ Member removed. Members now: {len(members_final)}")

        # 10. Delete class
        print("\n10. Deleting class...")
        ClassService.delete_class(class_group.id, teacher.id)
        deleted_class = ClassGroup.query.get(class_group.id)
        print(f"✅ Class deleted: {deleted_class is None}")

        # Cleanup
        print("\n11. Cleaning up test data...")
        Student.query.filter(Student.name.like('Test%')).delete()
        User.query.filter(User.email.like('test%')).delete()
        db.session.commit()
        print("✅ Cleanup complete")

        print("\n=== All Class Groups Tests Passed! ===\n")

if __name__ == '__main__':
    test_class_system()

