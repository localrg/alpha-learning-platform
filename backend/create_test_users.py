"""
Create test users for all roles in the Alpha Learning Platform.
"""
import sys
import os

# Add the backend directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.database import db
from src.models.user import User
from src.models.student import Student
from src.models.teacher import Teacher
from src.models.parent import Parent
from src.main import app

def create_test_users():
    """Create test users for all roles"""
    with app.app_context():
        print("Creating test users...")
        
        # Create test student
        student_user = User.query.filter_by(email='student@test.com').first()
        if not student_user:
            student_user = User(
                email='student@test.com',
                username='teststudent',
                role='student'
            )
            student_user.set_password('password123')
            db.session.add(student_user)
            db.session.commit()
            
            # Create student profile
            student = Student(
                user_id=student_user.id,
                name='Test Student',
                grade=8
            )
            db.session.add(student)
            db.session.commit()
            print("✅ Created test student: student@test.com / password123")
        else:
            print("ℹ️  Test student already exists: student@test.com / password123")
        
        # Create test teacher
        teacher_user = User.query.filter_by(email='teacher@test.com').first()
        if not teacher_user:
            teacher_user = User(
                email='teacher@test.com',
                username='testteacher',
                role='teacher'
            )
            teacher_user.set_password('password123')
            db.session.add(teacher_user)
            db.session.commit()
            
            # Create teacher profile
            teacher = Teacher(
                user_id=teacher_user.id,
                name='Test Teacher',
                subject='Mathematics'
            )
            db.session.add(teacher)
            db.session.commit()
            print("✅ Created test teacher: teacher@test.com / password123")
        else:
            print("ℹ️  Test teacher already exists: teacher@test.com / password123")
        
        # Create test parent
        parent_user = User.query.filter_by(email='parent@test.com').first()
        if not parent_user:
            parent_user = User(
                email='parent@test.com',
                username='testparent',
                role='parent'
            )
            parent_user.set_password('password123')
            db.session.add(parent_user)
            db.session.commit()
            
            # Create parent profile
            parent = Parent(
                user_id=parent_user.id,
                name='Test Parent',
                email='parent@test.com',
                phone='555-1234'
            )
            db.session.add(parent)
            db.session.commit()
            print("✅ Created test parent: parent@test.com / password123")
        else:
            print("ℹ️  Test parent already exists: parent@test.com / password123")
        
        # Create test admin
        admin_user = User.query.filter_by(email='admin@test.com').first()
        if not admin_user:
            admin_user = User(
                email='admin@test.com',
                username='testadmin',
                role='admin'
            )
            admin_user.set_password('password123')
            db.session.add(admin_user)
            db.session.commit()
            print("✅ Created test admin: admin@test.com / password123")
        else:
            print("ℹ️  Test admin already exists: admin@test.com / password123")
        
        print("\n" + "="*60)
        print("Test users created successfully!")
        print("="*60)
        print("\nYou can now log in with:")
        print("  Student: student@test.com / password123")
        print("  Teacher: teacher@test.com / password123")
        print("  Parent:  parent@test.com / password123")
        print("  Admin:   admin@test.com / password123")
        print("="*60)

if __name__ == '__main__':
    create_test_users()

