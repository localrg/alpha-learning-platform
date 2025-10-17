"""
Test Parent Accounts System
Tests all parent account and child linking functionality
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from src.database import db, init_db
from src.models.user import User
from src.models.student import Student
from src.models.parent import Parent, ParentChildLink, LinkRequest
from src.services.parent_service import ParentService
from flask import Flask
from datetime import datetime, timedelta

# Create test app
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'test-secret-key'

# Initialize database
init_db(app)

def run_tests():
    """Run all parent account tests"""
    with app.app_context():
        # Drop and recreate tables
        db.drop_all()
        db.create_all()
        
        print("=" * 60)
        print("PARENT ACCOUNTS SYSTEM TESTS")
        print("=" * 60)
        
        # Test 1: Create test users and students
        print("\n[Test 1] Creating test users and students...")
        try:
            # Create parent user
            parent_user = User(username='parent1', email='parent1@email.com', role='parent')
            parent_user.set_password('password123')
            db.session.add(parent_user)
            db.session.flush()
            
            # Create student users
            student1_user = User(username='student1', email='student1@email.com')
            student1_user.set_password('password123')
            db.session.add(student1_user)
            db.session.flush()
            
            student2_user = User(username='student2', email='student2@email.com')
            student2_user.set_password('password123')
            db.session.add(student2_user)
            db.session.flush()
            
            # Create students
            student1 = Student(
                user_id=student1_user.id,
                name='Student One',
                grade=5
            )
            db.session.add(student1)
            
            student2 = Student(
                user_id=student2_user.id,
                name='Student Two',
                grade=6
            )
            db.session.add(student2)
            
            db.session.commit()
            print(f"✓ Created parent user and 2 student users")
        except Exception as e:
            print(f"✗ Error: {e}")
            import traceback
            traceback.print_exc()
            return
        
        # Test 2: Create parent account
        print("\n[Test 2] Creating parent account...")
        try:
            result, status = ParentService.create_parent_account(
                user_id=parent_user.id,
                name='Jane Smith',
                email='parent1@email.com',
                phone='555-1234'
            )
            
            if result.get('success'):
                parent_id = result['parent']['id']
                print(f"✓ Parent account created")
                print(f"  - Parent ID: {parent_id}")
                print(f"  - Name: {result['parent']['name']}")
                print(f"  - Email: {result['parent']['email']}")
                print(f"  - Phone: {result['parent']['phone']}")
                print(f"  - Notification prefs: {len(result['parent']['notification_preferences'])} settings")
            else:
                print(f"✗ Error: {result.get('error')}")
                return
        except Exception as e:
            print(f"✗ Error: {e}")
            import traceback
            traceback.print_exc()
            return
        
        # Test 3: Get parent by user ID
        print("\n[Test 3] Getting parent by user ID...")
        try:
            result, status = ParentService.get_parent_by_user_id(parent_user.id)
            
            if result.get('success'):
                print(f"✓ Parent retrieved")
                print(f"  - Parent ID: {result['parent']['id']}")
                print(f"  - Name: {result['parent']['name']}")
            else:
                print(f"✗ Error: {result.get('error')}")
        except Exception as e:
            print(f"✗ Error: {e}")
        
        # Test 4: Update parent profile
        print("\n[Test 4] Updating parent profile...")
        try:
            result, status = ParentService.update_parent_profile(
                parent_id=parent_id,
                name='Jane M. Smith',
                phone='555-5678'
            )
            
            if result.get('success'):
                print(f"✓ Profile updated")
                print(f"  - New name: {result['parent']['name']}")
                print(f"  - New phone: {result['parent']['phone']}")
            else:
                print(f"✗ Error: {result.get('error')}")
        except Exception as e:
            print(f"✗ Error: {e}")
        
        # Test 5: Update notification preferences
        print("\n[Test 5] Updating notification preferences...")
        try:
            new_prefs = {
                'daily_summary': {'enabled': False, 'method': 'email'},
                'achievements': {'enabled': True, 'method': 'email'}
            }
            
            result, status = ParentService.update_notification_preferences(
                parent_id=parent_id,
                preferences=new_prefs
            )
            
            if result.get('success'):
                print(f"✓ Notification preferences updated")
                print(f"  - Daily summary: {result['preferences']['daily_summary']['enabled']}")
                print(f"  - Achievements: {result['preferences']['achievements']['enabled']}")
            else:
                print(f"✗ Error: {result.get('error')}")
        except Exception as e:
            print(f"✗ Error: {e}")
        
        # Test 6: Generate invite code
        print("\n[Test 6] Generating parent invite code...")
        try:
            result, status = ParentService.generate_invite_code(student1.id)
            
            if result.get('success'):
                invite_code = result['invite_code']
                print(f"✓ Invite code generated")
                print(f"  - Code: {invite_code}")
                print(f"  - Expires: {result['expires_at']}")
                print(f"  - Request ID: {result['request_id']}")
            else:
                print(f"✗ Error: {result.get('error')}")
                return
        except Exception as e:
            print(f"✗ Error: {e}")
            import traceback
            traceback.print_exc()
            return
        
        # Test 7: Link child by invite code
        print("\n[Test 7] Linking child by invite code...")
        try:
            result, status = ParentService.link_child_by_code(
                parent_id=parent_id,
                invite_code=invite_code
            )
            
            if result.get('success'):
                print(f"✓ Child linked successfully")
                print(f"  - Link ID: {result['link']['id']}")
                print(f"  - Student: {result['link']['student_name']}")
                print(f"  - Status: {result['link']['status']}")
            else:
                print(f"✗ Error: {result.get('error')}")
        except Exception as e:
            print(f"✗ Error: {e}")
            import traceback
            traceback.print_exc()
        
        # Test 8: Get linked children
        print("\n[Test 8] Getting linked children...")
        try:
            result, status = ParentService.get_linked_children(parent_id)
            
            if result.get('success'):
                print(f"✓ Linked children retrieved")
                print(f"  - Count: {result['count']}")
                for child in result['children']:
                    print(f"  - {child['student_name']} ({child['student_email']})")
            else:
                print(f"✗ Error: {result.get('error')}")
        except Exception as e:
            print(f"✗ Error: {e}")
        
        # Test 9: Request child link by email
        print("\n[Test 9] Requesting child link by email...")
        try:
            result, status = ParentService.request_child_link(
                parent_id=parent_id,
                student_email='student2@email.com'
            )
            
            if result.get('success'):
                request_id = result['request']['id']
                print(f"✓ Link request created")
                print(f"  - Request ID: {request_id}")
                print(f"  - Student: {result['request']['student_name']}")
                print(f"  - Status: {result['request']['status']}")
            else:
                print(f"✗ Error: {result.get('error')}")
                return
        except Exception as e:
            print(f"✗ Error: {e}")
            import traceback
            traceback.print_exc()
            return
        
        # Test 10: Get pending requests (student view)
        print("\n[Test 10] Getting pending requests for student...")
        try:
            result, status = ParentService.get_pending_requests(student2.id)
            
            if result.get('success'):
                print(f"✓ Pending requests retrieved")
                print(f"  - Count: {result['count']}")
                for req in result['requests']:
                    print(f"  - From: {req['parent_name']} ({req['parent_email']})")
                    print(f"    Status: {req['status']}")
            else:
                print(f"✗ Error: {result.get('error')}")
        except Exception as e:
            print(f"✗ Error: {e}")
        
        # Test 11: Approve link request
        print("\n[Test 11] Approving link request...")
        try:
            result, status = ParentService.approve_link_request(
                request_id=request_id,
                student_id=student2.id
            )
            
            if result.get('success'):
                print(f"✓ Link request approved")
                print(f"  - Link ID: {result['link']['id']}")
                print(f"  - Student: {result['link']['student_name']}")
            else:
                print(f"✗ Error: {result.get('error')}")
        except Exception as e:
            print(f"✗ Error: {e}")
        
        # Test 12: Verify both children are linked
        print("\n[Test 12] Verifying both children are linked...")
        try:
            result, status = ParentService.get_linked_children(parent_id)
            
            if result.get('success'):
                print(f"✓ Both children linked")
                print(f"  - Total children: {result['count']}")
                if result['count'] == 2:
                    print(f"  ✓ Correct count")
                else:
                    print(f"  ✗ Expected 2, got {result['count']}")
            else:
                print(f"✗ Error: {result.get('error')}")
        except Exception as e:
            print(f"✗ Error: {e}")
        
        # Test 13: Remove child link
        print("\n[Test 13] Removing child link...")
        try:
            result, status = ParentService.remove_child_link(
                parent_id=parent_id,
                student_id=student2.id
            )
            
            if result.get('success'):
                print(f"✓ Child link removed")
            else:
                print(f"✗ Error: {result.get('error')}")
        except Exception as e:
            print(f"✗ Error: {e}")
        
        # Test 14: Verify child was removed
        print("\n[Test 14] Verifying child was removed...")
        try:
            result, status = ParentService.get_linked_children(parent_id)
            
            if result.get('success'):
                print(f"✓ Linked children retrieved")
                print(f"  - Count: {result['count']}")
                if result['count'] == 1:
                    print(f"  ✓ Correct count after removal")
                else:
                    print(f"  ✗ Expected 1, got {result['count']}")
            else:
                print(f"✗ Error: {result.get('error')}")
        except Exception as e:
            print(f"✗ Error: {e}")
        
        # Test 15: Test expired invite code
        print("\n[Test 15] Testing expired invite code...")
        try:
            # Generate code
            result, status = ParentService.generate_invite_code(student2.id)
            expired_code = result['invite_code']
            
            # Manually expire it
            request = LinkRequest.query.filter_by(invite_code=expired_code).first()
            request.expires_at = datetime.utcnow() - timedelta(days=1)
            db.session.commit()
            
            # Try to use expired code
            result, status = ParentService.link_child_by_code(parent_id, expired_code)
            
            if status == 400 and 'expired' in result.get('error', '').lower():
                print(f"✓ Correctly rejected expired code")
            else:
                print(f"✗ Should reject expired code")
        except Exception as e:
            print(f"✗ Error: {e}")
        
        # Test 16: Test duplicate link prevention
        print("\n[Test 16] Testing duplicate link prevention...")
        try:
            # Try to link student1 again (already linked)
            result, status = ParentService.generate_invite_code(student1.id)
            new_code = result['invite_code']
            
            result, status = ParentService.link_child_by_code(parent_id, new_code)
            
            if status == 400 and 'already linked' in result.get('error', '').lower():
                print(f"✓ Correctly prevented duplicate link")
            else:
                print(f"✗ Should prevent duplicate links")
        except Exception as e:
            print(f"✗ Error: {e}")
        
        # Test 17: Test invalid invite code
        print("\n[Test 17] Testing invalid invite code...")
        try:
            result, status = ParentService.link_child_by_code(parent_id, 'INVALID123')
            
            if status == 404:
                print(f"✓ Correctly rejected invalid code")
            else:
                print(f"✗ Should reject invalid code")
        except Exception as e:
            print(f"✗ Error: {e}")
        
        # Test 18: Test reject link request
        print("\n[Test 18] Testing link request rejection...")
        try:
            # Create new parent
            parent2_user = User(username='parent2', email='parent2@email.com', role='parent')
            parent2_user.set_password('password123')
            db.session.add(parent2_user)
            db.session.flush()
            
            result, status = ParentService.create_parent_account(
                user_id=parent2_user.id,
                name='John Doe',
                email='parent2@email.com'
            )
            parent2_id = result['parent']['id']
            
            # Request link
            result, status = ParentService.request_child_link(
                parent_id=parent2_id,
                student_email='student1@email.com'
            )
            reject_request_id = result['request']['id']
            
            # Reject request
            result, status = ParentService.reject_link_request(
                request_id=reject_request_id,
                student_id=student1.id
            )
            
            if result.get('success'):
                print(f"✓ Link request rejected successfully")
            else:
                print(f"✗ Error: {result.get('error')}")
        except Exception as e:
            print(f"✗ Error: {e}")
            import traceback
            traceback.print_exc()
        
        # Test 19: Test non-existent student
        print("\n[Test 19] Testing with non-existent student...")
        try:
            result, status = ParentService.generate_invite_code(9999)
            
            if status == 404:
                print(f"✓ Correctly returned 404 for non-existent student")
            else:
                print(f"✗ Should return 404")
        except Exception as e:
            print(f"✗ Error: {e}")
        
        # Test 20: Test non-existent parent
        print("\n[Test 20] Testing with non-existent parent...")
        try:
            result, status = ParentService.get_linked_children(9999)
            
            if result.get('success') and result.get('count') == 0:
                print(f"✓ Correctly returned empty list for non-existent parent")
            else:
                print(f"✗ Should return empty list")
        except Exception as e:
            print(f"✗ Error: {e}")
        
        print("\n" + "=" * 60)
        print("ALL TESTS COMPLETED!")
        print("=" * 60)


if __name__ == '__main__':
    run_tests()

