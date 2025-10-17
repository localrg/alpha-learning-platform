"""
Database initialization routes
"""
from flask import Blueprint, jsonify
from src.database import db
from src.models.user import User
from src.models.student import Student
from src.models.teacher import Teacher
from src.models.parent import Parent

init_bp = Blueprint('init', __name__)

@init_bp.route('/api/init-db', methods=['POST'])
def initialize_database():
    """Initialize database with test users"""
    try:
        # Create all tables
        db.create_all()
        
        # Check if we already have users
        existing_count = User.query.count()
        if existing_count > 0:
            return jsonify({
                'message': f'Database already has {existing_count} users',
                'status': 'already_initialized'
            }), 200
        
        # Create test student
        student_user = User(
            email='student@test.com',
            username='teststudent',
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
            username='testteacher',
            role='teacher'
        )
        teacher_user.set_password('password123')
        db.session.add(teacher_user)
        db.session.flush()
        
        teacher = Teacher(
            user_id=teacher_user.id,
            name='Test Teacher',
            subject='Mathematics'
        )
        db.session.add(teacher)
        
        # Create test parent
        parent_user = User(
            email='parent@test.com',
            username='testparent',
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
            username='testadmin',
            role='admin'
        )
        admin_user.set_password('password123')
        db.session.add(admin_user)
        
        db.session.commit()
        
        return jsonify({
            'message': 'Database initialized successfully with test users',
            'users': [
                {'email': 'student@test.com', 'password': 'password123', 'role': 'student'},
                {'email': 'teacher@test.com', 'password': 'password123', 'role': 'teacher'},
                {'email': 'parent@test.com', 'password': 'password123', 'role': 'parent'},
                {'email': 'admin@test.com', 'password': 'password123', 'role': 'admin'}
            ]
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

