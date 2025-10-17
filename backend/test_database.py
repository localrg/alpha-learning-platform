"""
Test script to verify database setup and User model functionality.
"""
import os
import sys
sys.path.insert(0, os.path.dirname(__file__))

from src.main import app
from src.database import db
from src.models.user import User

def test_database():
    """Test database connection and User model operations."""
    
    with app.app_context():
        print("=" * 60)
        print("DATABASE SETUP TEST")
        print("=" * 60)
        
        # Test 1: Create a test user
        print("\n[TEST 1] Creating test user...")
        test_user = User(username="testuser", email="test@example.com")
        test_user.set_password("password123")
        
        db.session.add(test_user)
        db.session.commit()
        print(f"✓ User created: {test_user}")
        print(f"  - ID: {test_user.id}")
        print(f"  - Username: {test_user.username}")
        print(f"  - Email: {test_user.email}")
        print(f"  - Password hash: {test_user.password_hash[:30]}...")
        print(f"  - Created at: {test_user.created_at}")
        
        # Test 2: Retrieve the user
        print("\n[TEST 2] Retrieving user from database...")
        retrieved_user = User.query.filter_by(username="testuser").first()
        assert retrieved_user is not None, "User not found in database!"
        print(f"✓ User retrieved: {retrieved_user}")
        print(f"  - ID matches: {retrieved_user.id == test_user.id}")
        print(f"  - Username matches: {retrieved_user.username == test_user.username}")
        
        # Test 3: Test password verification
        print("\n[TEST 3] Testing password verification...")
        correct_password = retrieved_user.check_password("password123")
        wrong_password = retrieved_user.check_password("wrongpassword")
        print(f"✓ Correct password check: {correct_password}")
        print(f"✓ Wrong password check: {wrong_password}")
        assert correct_password == True, "Password verification failed for correct password!"
        assert wrong_password == False, "Password verification failed for wrong password!"
        
        # Test 4: Test to_dict method
        print("\n[TEST 4] Testing to_dict() method...")
        user_dict = retrieved_user.to_dict()
        print(f"✓ User dictionary: {user_dict}")
        assert 'password_hash' not in user_dict, "Password hash should not be in dictionary!"
        assert user_dict['username'] == 'testuser', "Username mismatch in dictionary!"
        
        # Test 5: Test database schema
        print("\n[TEST 5] Verifying database schema...")
        from sqlalchemy import inspect
        inspector = inspect(db.engine)
        tables = inspector.get_table_names()
        print(f"✓ Tables in database: {tables}")
        assert 'users' in tables, "Users table not found!"
        
        columns = [col['name'] for col in inspector.get_columns('users')]
        print(f"✓ Columns in users table: {columns}")
        required_columns = ['id', 'username', 'password_hash', 'email', 'created_at', 'last_login']
        for col in required_columns:
            assert col in columns, f"Required column '{col}' not found!"
        
        # Cleanup
        print("\n[CLEANUP] Removing test user...")
        db.session.delete(retrieved_user)
        db.session.commit()
        print("✓ Test user deleted")
        
        # Verify deletion
        deleted_user = User.query.filter_by(username="testuser").first()
        assert deleted_user is None, "User was not deleted!"
        print("✓ Deletion verified")
        
        print("\n" + "=" * 60)
        print("ALL TESTS PASSED! ✓")
        print("=" * 60)
        print("\nDatabase setup is working correctly!")
        print(f"Database file: {app.config['SQLALCHEMY_DATABASE_URI']}")
        print("\nUser model has the following fields:")
        print("  - id (Integer, Primary Key)")
        print("  - username (String, Unique, Indexed)")
        print("  - password_hash (String)")
        print("  - email (String, Unique)")
        print("  - created_at (DateTime)")
        print("  - last_login (DateTime)")
        print("\nUser model methods:")
        print("  - set_password(password) - Hash and store password")
        print("  - check_password(password) - Verify password")
        print("  - update_last_login() - Update last login timestamp")
        print("  - to_dict() - Convert to dictionary (excludes password)")
        print("=" * 60)

if __name__ == '__main__':
    test_database()

