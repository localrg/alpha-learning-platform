"""
Test script for friend system.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from src.main import app
from src.database import db
from src.models.user import User
from src.models.student import Student
from src.models.friendship import Friendship
from src.services.friend_service import FriendService


def test_friend_system():
    """Test friend system functionality."""
    with app.app_context():
        # Clean up
        Friendship.query.delete()
        Student.query.delete()
        User.query.delete()
        db.session.commit()
        
        # Create test users
        user1 = User(username='alice', email='alice@test.com')
        user1.set_password('password123')
        user2 = User(username='bob', email='bob@test.com')
        user2.set_password('password123')
        user3 = User(username='charlie', email='charlie@test.com')
        user3.set_password('password123')
        
        db.session.add_all([user1, user2, user3])
        db.session.commit()
        
        # Create students
        student1 = Student(
            user_id=user1.id,
            name='Alice Smith',
            grade=5
        )
        student2 = Student(
            user_id=user2.id,
            name='Bob Jones',
            grade=5
        )
        student3 = Student(
            user_id=user3.id,
            name='Charlie Brown',
            grade=6
        )
        
        db.session.add_all([student1, student2, student3])
        db.session.commit()
        
        print("✅ Test 1: Created test users and students")
        
        # Test 2: Send friend request
        friendship = FriendService.send_request(student1.id, student2.id)
        assert friendship.requester_id == student1.id
        assert friendship.addressee_id == student2.id
        assert friendship.status == 'pending'
        print("✅ Test 2: Send friend request")
        
        # Test 3: Cannot send duplicate request
        try:
            FriendService.send_request(student1.id, student2.id)
            assert False, "Should not allow duplicate request"
        except ValueError as e:
            assert 'already pending' in str(e).lower()
            print("✅ Test 3: Prevent duplicate requests")
        
        # Test 4: Cannot send request to self
        try:
            FriendService.send_request(student1.id, student1.id)
            assert False, "Should not allow self-request"
        except ValueError as e:
            assert 'yourself' in str(e).lower()
            print("✅ Test 4: Prevent self-requests")
        
        # Test 5: Get received requests
        requests = FriendService.get_received_requests(student2.id)
        assert len(requests) == 1
        assert requests[0]['requester']['id'] == student1.id
        print("✅ Test 5: Get received requests")
        
        # Test 6: Get sent requests
        sent = FriendService.get_sent_requests(student1.id)
        assert len(sent) == 1
        assert sent[0]['addressee']['id'] == student2.id
        print("✅ Test 6: Get sent requests")
        
        # Test 7: Accept friend request
        accepted = FriendService.accept_request(friendship.id, student2.id)
        assert accepted.status == 'accepted'
        print("✅ Test 7: Accept friend request")
        
        # Test 8: Get friends list
        friends = FriendService.get_friends(student1.id)
        assert len(friends) == 1
        assert friends[0]['id'] == student2.id
        
        friends2 = FriendService.get_friends(student2.id)
        assert len(friends2) == 1
        assert friends2[0]['id'] == student1.id
        print("✅ Test 8: Get friends list (bidirectional)")
        
        # Test 9: Friend count
        count = FriendService.get_friend_count(student1.id)
        assert count == 1
        print("✅ Test 9: Friend count")
        
        # Test 10: Are friends check
        assert FriendService.are_friends(student1.id, student2.id) == True
        assert FriendService.are_friends(student1.id, student3.id) == False
        print("✅ Test 10: Are friends check")
        
        # Test 11: Search students
        results = FriendService.search_students('Charlie', student1.id)
        assert len(results) == 1
        assert results[0]['id'] == student3.id
        assert results[0]['friendship_status'] == 'none'
        print("✅ Test 11: Search students")
        
        # Test 12: Remove friend
        FriendService.remove_friend(student1.id, student2.id)
        friends = FriendService.get_friends(student1.id)
        assert len(friends) == 0
        print("✅ Test 12: Remove friend")
        
        # Test 13: Reject request
        friendship2 = FriendService.send_request(student1.id, student3.id)
        FriendService.reject_request(friendship2.id, student3.id)
        
        # Should be deleted
        rejected = Friendship.query.get(friendship2.id)
        assert rejected is None
        print("✅ Test 13: Reject request")
        
        # Test 14: Cancel request
        friendship3 = FriendService.send_request(student2.id, student3.id)
        FriendService.cancel_request(friendship3.id, student2.id)
        
        # Should be deleted
        cancelled = Friendship.query.get(friendship3.id)
        assert cancelled is None
        print("✅ Test 14: Cancel request")
        
        # Clean up
        Friendship.query.delete()
        Student.query.delete()
        User.query.delete()
        db.session.commit()
        
        print("\n🎉 All 14 friend system tests passed!")


if __name__ == '__main__':
    test_friend_system()

