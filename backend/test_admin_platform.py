"""
Comprehensive tests for Week 10: Platform Administration & Management
Tests all 5 steps: Admin Dashboard, User Management, Content Management, Settings, Audit Logging
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from src.database import db
# Create app without importing main.py to avoid circular dependencies
from flask import Flask
app = Flask(__name__)
app.config['SECRET_KEY'] = 'test-secret'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
from src.database import init_db
init_db(app)
from src.models.user import User
from src.models.student import Student
from src.models.student_session import StudentSession
from src.models.learning_path import LearningPath
from src.models.assessment import Skill
from src.models.class_group import ClassGroup  # Import before Assignment
from src.models.assignment_model import Assignment
from src.models.admin_models import AuditLog, SystemSetting
from src.services.admin_service import AdminService
from src.services.user_management_service import UserManagementService
from src.services.content_management_service import ContentManagementService
from src.services.settings_audit_service import SettingsService, AuditService
from datetime import datetime, timedelta


def setup_test_data():
    """Create test data for admin tests"""
    # Create admin user
    admin = User(username='admin1', email='admin@test.com', role='admin')
    admin.set_password('password')
    db.session.add(admin)
    db.session.flush()
    
    # Create some users
    for i in range(1, 4):
        user = User(username=f'student{i}', email=f'student{i}@test.com', role='student')
        user.set_password('password')
        db.session.add(user)
        db.session.flush()
        
        student = Student(user_id=user.id, name=f'Student {i}', grade=i)
        db.session.add(student)
    
    # Create a teacher
    teacher_user = User(username='teacher1', email='teacher@test.com', role='teacher')
    teacher_user.set_password('password')
    db.session.add(teacher_user)
    
    db.session.commit()
    
    return admin.id


def test_admin_dashboard():
    """Test Step 10.1: Admin Dashboard"""
    print("\n" + "="*60)
    print("WEEK 10 ADMIN PLATFORM TESTS")
    print("="*60)
    
    with app.app_context():
        # Clear database
        db.drop_all()
        db.create_all()
        
        admin_id = setup_test_data()
        
        # Test 1: Get platform metrics
        print("[Test 1] Getting platform metrics...")
        result, status = AdminService.get_platform_metrics()
        assert status == 200, f"Expected 200, got {status}"
        assert result['success'], "Metrics retrieval failed"
        assert 'metrics' in result
        metrics = result['metrics']
        assert metrics['users']['total'] == 5, f"Expected 5 users, got {metrics['users']['total']}"
        assert metrics['users']['students'] == 3
        assert metrics['users']['teachers'] == 1
        assert metrics['users']['admins'] == 1
        print(f"✓ Platform metrics retrieved")
        print(f"  - Total users: {metrics['users']['total']}")
        print(f"  - Students: {metrics['users']['students']}")
        print(f"  - Teachers: {metrics['users']['teachers']}")
        
        # Test 2: Get user growth
        print("[Test 2] Getting user growth trends...")
        result, status = AdminService.get_user_growth(days=7)
        assert status == 200
        assert result['success']
        assert 'growth' in result
        growth = result['growth']
        assert growth['total_new_users'] == 5
        print(f"✓ User growth retrieved")
        print(f"  - New users (7 days): {growth['total_new_users']}")
        
        # Test 3: Get system health
        print("[Test 3] Getting system health...")
        result, status = AdminService.get_system_health()
        assert status == 200
        assert result['success']
        assert 'health' in result
        health = result['health']
        assert health['status'] == 'healthy'
        print(f"✓ System health retrieved")
        print(f"  - Status: {health['status']}")
        print(f"  - Total records: {health['database']['total_records']}")
        
        # Test 4: Get recent activity
        print("[Test 4] Getting recent activity...")
        result, status = AdminService.get_recent_activity(limit=10)
        assert status == 200
        assert result['success']
        print(f"✓ Recent activity retrieved")
        print(f"  - Activity count: {len(result['activity'])}")


def test_user_management():
    """Test Step 10.2: User Management"""
    with app.app_context():
        admin_id = User.query.filter_by(role='admin').first().id
        
        # Test 5: Create user
        print("[Test 5] Creating new user...")
        user_data = {
            'username': 'newstudent',
            'email': 'newstudent@test.com',
            'password': 'password',
            'role': 'student',
            'name': 'New Student',
            'grade': 5
        }
        result, status = UserManagementService.create_user(admin_id, user_data)
        assert status == 201
        assert result['success']
        new_user_id = result['user_id']
        print(f"✓ User created")
        print(f"  - User ID: {new_user_id}")
        
        # Test 6: Update user
        print("[Test 6] Updating user...")
        update_data = {'email': 'updated@test.com'}
        result, status = UserManagementService.update_user(admin_id, new_user_id, update_data)
        assert status == 200
        assert result['success']
        print(f"✓ User updated")
        
        # Test 7: Search users
        print("[Test 7] Searching users...")
        result, status = UserManagementService.search_users(query='student', role='student')
        assert status == 200
        assert result['success']
        assert result['count'] >= 3
        print(f"✓ Users searched")
        print(f"  - Found: {result['count']} users")
        
        # Test 8: Get user details
        print("[Test 8] Getting user details...")
        result, status = UserManagementService.get_user_details(new_user_id)
        assert status == 200
        assert result['success']
        assert result['user']['email'] == 'updated@test.com'
        print(f"✓ User details retrieved")
        print(f"  - Username: {result['user']['username']}")
        print(f"  - Email: {result['user']['email']}")
        
        # Test 9: Delete user
        print("[Test 9] Deleting user...")
        result, status = UserManagementService.delete_user(admin_id, new_user_id)
        if status != 200:
            print(f"  Delete failed: {result}")
        assert status == 200
        assert result['success']
        print(f"✓ User deleted")
        
        # Test 10: Verify deletion
        print("[Test 10] Verifying user deletion...")
        result, status = UserManagementService.get_user_details(new_user_id)
        assert status == 404
        print(f"✓ User deletion verified")


def test_content_management():
    """Test Step 10.3: Content Management"""
    with app.app_context():
        admin_id = User.query.filter_by(role='admin').first().id
        
        # Test 11: Create skill
        print("[Test 11] Creating new skill...")
        skill_data = {
            'name': 'Advanced Algebra',
            'subject_area': 'math',
            'grade_level': 8,
            'description': 'Advanced algebraic concepts'
        }
        result, status = ContentManagementService.create_skill(admin_id, skill_data)
        assert status == 201
        assert result['success']
        new_skill_id = result['skill_id']
        print(f"✓ Skill created")
        print(f"  - Skill ID: {new_skill_id}")
        print(f"  - Name: {skill_data['name']}")
        
        # Test 12: Update skill
        print("[Test 12] Updating skill...")
        update_data = {'description': 'Updated description'}
        result, status = ContentManagementService.update_skill(admin_id, new_skill_id, update_data)
        assert status == 200
        assert result['success']
        print(f"✓ Skill updated")
        
        # Test 13: Get skills
        print("[Test 13] Getting skills...")
        result, status = ContentManagementService.get_skills(subject_area='math')
        assert status == 200
        assert result['success']
        print(f"✓ Skills retrieved")
        print(f"  - Count: {result['count']}")
        
        # Test 14: Delete skill
        print("[Test 14] Deleting skill...")
        result, status = ContentManagementService.delete_skill(admin_id, new_skill_id)
        assert status == 200
        assert result['success']
        print(f"✓ Skill deleted")


def test_settings():
    """Test Step 10.4: System Settings"""
    with app.app_context():
        admin_id = User.query.filter_by(role='admin').first().id
        
        # Test 15: Create setting
        print("[Test 15] Creating system setting...")
        result, status = SettingsService.update_setting(
            admin_id=admin_id,
            key='general.platform_name',
            value='Alpha Learning Platform',
            description='Platform display name'
        )
        assert status == 200
        assert result['success']
        print(f"✓ Setting created")
        
        # Test 16: Get setting
        print("[Test 16] Getting setting...")
        result, status = SettingsService.get_setting('general.platform_name')
        assert status == 200
        assert result['success']
        assert result['setting']['value'] == 'Alpha Learning Platform'
        print(f"✓ Setting retrieved")
        print(f"  - Value: {result['setting']['value']}")
        
        # Test 17: Update setting
        print("[Test 17] Updating setting...")
        result, status = SettingsService.update_setting(
            admin_id=admin_id,
            key='general.platform_name',
            value='Alpha Learning - Updated'
        )
        assert status == 200
        assert result['success']
        print(f"✓ Setting updated")
        
        # Test 18: Get all settings
        print("[Test 18] Getting all settings...")
        result, status = SettingsService.get_settings()
        assert status == 200
        assert result['success']
        assert len(result['settings']) >= 1
        print(f"✓ All settings retrieved")
        print(f"  - Count: {len(result['settings'])}")
        
        # Test 19: Get settings by category
        print("[Test 19] Getting settings by category...")
        result, status = SettingsService.get_settings(category='general')
        assert status == 200
        assert result['success']
        print(f"✓ Settings by category retrieved")
        print(f"  - Count: {len(result['settings'])}")


def test_audit_logging():
    """Test Step 10.5: Audit Logging"""
    with app.app_context():
        admin_id = User.query.filter_by(role='admin').first().id
        
        # Test 20: Log action
        print("[Test 20] Logging admin action...")
        result, status = AuditService.log_action(
            admin_id=admin_id,
            action_type='create',
            entity_type='user',
            entity_id=1,
            after_value='{"username": "testuser"}',
            description='Created test user',
            ip_address='127.0.0.1',
            user_agent='Test Agent'
        )
        assert status == 201
        assert result['success']
        log_id = result['log_id']
        print(f"✓ Action logged")
        print(f"  - Log ID: {log_id}")
        
        # Test 21: Get logs
        print("[Test 21] Getting audit logs...")
        result, status = AuditService.get_logs(limit=10)
        assert status == 200
        assert result['success']
        assert result['count'] > 0
        print(f"✓ Audit logs retrieved")
        print(f"  - Count: {result['count']}")
        
        # Test 22: Get logs by action type
        print("[Test 22] Getting logs by action type...")
        result, status = AuditService.get_logs(action_type='create')
        assert status == 200
        assert result['success']
        print(f"✓ Logs by action type retrieved")
        print(f"  - Count: {result['count']}")
        
        # Test 23: Get logs by entity type
        print("[Test 23] Getting logs by entity type...")
        result, status = AuditService.get_logs(entity_type='user')
        assert status == 200
        assert result['success']
        print(f"✓ Logs by entity type retrieved")
        print(f"  - Count: {result['count']}")
        
        # Test 24: Get admin activity
        print("[Test 24] Getting admin activity...")
        result, status = AuditService.get_admin_activity(admin_id, days=7)
        assert status == 200
        assert result['success']
        assert result['activity']['total_actions'] > 0
        print(f"✓ Admin activity retrieved")
        print(f"  - Total actions: {result['activity']['total_actions']}")
        print(f"  - Action counts: {result['activity']['action_counts']}")
        
        # Test 25: Export logs (JSON)
        print("[Test 25] Exporting logs (JSON)...")
        result, status = AuditService.export_logs({}, format='json')
        assert status == 200
        assert result['success']
        assert result['format'] == 'json'
        print(f"✓ Logs exported (JSON)")
        print(f"  - Records: {len(result['data'])}")
        
        # Test 26: Export logs (CSV)
        print("[Test 26] Exporting logs (CSV)...")
        result, status = AuditService.export_logs({}, format='csv')
        assert status == 200
        assert result['success']
        assert result['format'] == 'csv'
        assert 'admin_name' in result['data']
        print(f"✓ Logs exported (CSV)")
        print(f"  - CSV length: {len(result['data'])} characters")


if __name__ == '__main__':
    print("\n" + "="*60)
    print("WEEK 10: PLATFORM ADMINISTRATION & MANAGEMENT TESTS")
    print("="*60)
    
    try:
        test_admin_dashboard()
        test_user_management()
        test_content_management()
        test_settings()
        test_audit_logging()
        
        print("\n" + "="*60)
        print("ALL TESTS COMPLETED!")
        print("="*60)
        print("✓ Step 10.1: Admin Dashboard (4 tests)")
        print("✓ Step 10.2: User Management (6 tests)")
        print("✓ Step 10.3: Content Management (4 tests)")
        print("✓ Step 10.4: System Settings (5 tests)")
        print("✓ Step 10.5: Audit Logging (7 tests)")
        print("="*60)
        print("TOTAL: 26/26 tests passed ✅")
        print("="*60)
        
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        raise
    except Exception as e:
        print(f"\n❌ Error: {e}")
        raise

