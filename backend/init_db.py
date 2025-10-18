"""
Initialize database and create test users on startup.
"""
import os
from src.database import db
from src.models.user import User
from src.models.student import Student
from src.models.teacher import Teacher
from src.models.parent import Parent
from src.main import app

def init_database():
    """Initialize database and create test users if they don't exist"""
    with app.app_context():
        # Create all tables
        db.create_all()
        
        # Check if we already have users
        if User.query.count() > 0:
            print("Database already initialized")
            return
        
        print("Initializing database with test users...")
        
        # Create test student
        student_user = User(
            email='student@test.com',
            username='student1',
            role='student'
        )
        student_user.set_password('password123')
        db.session.add(student_user)
        db.session.flush()
        
        student = Student(
            user_id=student_user.id,
            name='Test Student',
            grade=8
        )
        db.session.add(student)
        
        # Create test teacher
        teacher_user = User(
            email='teacher@test.com',
            username='teacher1',
            role='teacher'
        )
        teacher_user.set_password('password123')
        db.session.add(teacher_user)
        db.session.flush()
        
        teacher = Teacher(
            user_id=teacher_user.id,
            name='Test Teacher',
            email='teacher@test.com',
            subject='Mathematics'
        )
        db.session.add(teacher)
        
        # Create test parent
        parent_user = User(
            email='parent@test.com',
            username='parent1',
            role='parent'
        )
        parent_user.set_password('password123')
        db.session.add(parent_user)
        db.session.flush()
        
        parent = Parent(
            user_id=parent_user.id,
            name='Test Parent',
            email='parent@test.com',
            phone='555-1234'
        )
        db.session.add(parent)
        
        # Create test admin
        admin_user = User(
            email='admin@test.com',
            username='admin1',
            role='admin'
        )
        admin_user.set_password('password123')
        db.session.add(admin_user)
        
        db.session.commit()
        print("✅ Test users created successfully!")

if __name__ == '__main__':
    init_database()

