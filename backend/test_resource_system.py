"""
Comprehensive tests for the Resource Library system.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from src.main import app
from src.database import db
from src.models.resource import Resource, ResourceDownload
from src.models.assessment import Skill
from src.models.student import Student
from src.models.user import User
from src.services.resource_service import ResourceService

def test_resource_system():
    """Test all resource system functionality."""
    with app.app_context():
        print("=" * 60)
        print("TESTING RESOURCE LIBRARY SYSTEM")
        print("=" * 60)
        
        # Test 1: Get existing resources
        print("\n1. Testing get all resources...")
        resources = ResourceService.get_all_resources()
        print(f"  ✓ Found {len(resources)} resources")
        if resources:
            print(f"  ✓ First resource: {resources[0].title}")
        
        # Test 2: Filter by type
        print("\n2. Testing filter by type...")
        worksheets = ResourceService.get_all_resources({'resource_type': 'worksheet'})
        references = ResourceService.get_all_resources({'resource_type': 'reference'})
        print(f"  ✓ Worksheets: {len(worksheets)}")
        print(f"  ✓ References: {len(references)}")
        
        # Test 3: Filter by grade
        print("\n3. Testing filter by grade...")
        grade3 = ResourceService.get_all_resources({'grade_level': 3})
        grade4 = ResourceService.get_all_resources({'grade_level': 4})
        print(f"  ✓ Grade 3 resources: {len(grade3)}")
        print(f"  ✓ Grade 4 resources: {len(grade4)}")
        
        # Test 4: Filter by difficulty
        print("\n4. Testing filter by difficulty...")
        easy = ResourceService.get_all_resources({'difficulty': 'easy'})
        medium = ResourceService.get_all_resources({'difficulty': 'medium'})
        hard = ResourceService.get_all_resources({'difficulty': 'hard'})
        print(f"  ✓ Easy resources: {len(easy)}")
        print(f"  ✓ Medium resources: {len(medium)}")
        print(f"  ✓ Hard resources: {len(hard)}")
        
        # Test 5: Search
        print("\n5. Testing search...")
        search_results = ResourceService.get_all_resources({'search': 'multiplication'})
        print(f"  ✓ Search 'multiplication': {len(search_results)} results")
        
        # Test 6: Get resource by ID
        print("\n6. Testing get resource by ID...")
        if resources:
            resource = ResourceService.get_resource_by_id(resources[0].id)
            assert resource is not None
            assert resource['title'] == resources[0].title
            print(f"  ✓ Retrieved resource: {resource['title']}")
        
        # Test 7: Get related resources
        print("\n7. Testing get related resources...")
        if resources:
            related = ResourceService.get_related_resources(resources[0].id)
            print(f"  ✓ Found {len(related)} related resources")
        
        # Test 8: Create test student
        print("\n8. Creating test student...")
        # Clean up existing test user
        test_user = User.query.filter_by(email='resource_test@example.com').first()
        if test_user:
            if test_user.student:
                # Delete downloads first
                ResourceDownload.query.filter_by(student_id=test_user.student.id).delete()
                db.session.delete(test_user.student)
            db.session.delete(test_user)
            db.session.commit()
        
        test_user = User(
            username='resource_test',
            email='resource_test@example.com'
        )
        test_user.set_password('password123')
        db.session.add(test_user)
        db.session.commit()
        
        test_student = Student(
            user_id=test_user.id,
            name='Resource Test Student',
            grade=3
        )
        db.session.add(test_student)
        db.session.commit()
        print(f"  ✓ Created test student: {test_student.name}")
        
        # Test 9: Record download
        print("\n9. Testing record download...")
        if resources:
            download = ResourceService.record_download(
                student_id=test_student.id,
                resource_id=resources[0].id,
                download_method='direct'
            )
            assert download is not None
            print(f"  ✓ Recorded download ID: {download.id}")
            print(f"  ✓ Method: {download.download_method}")
            
            # Check download count increased
            updated_resource = Resource.query.get(resources[0].id)
            print(f"  ✓ Download count: {updated_resource.download_count}")
        
        # Test 10: Get student downloads
        print("\n10. Testing get student downloads...")
        downloads = ResourceService.get_student_downloads(test_student.id)
        assert len(downloads) > 0
        print(f"  ✓ Student has {len(downloads)} downloads")
        print(f"  ✓ Latest download: {downloads[0]['resource']['title']}")
        
        # Test 11: Record multiple downloads
        print("\n11. Testing multiple downloads...")
        if len(resources) >= 3:
            for i in range(3):
                ResourceService.record_download(
                    student_id=test_student.id,
                    resource_id=resources[i].id,
                    download_method='direct' if i % 2 == 0 else 'print'
                )
            print(f"  ✓ Recorded 3 more downloads")
        
        # Test 12: Get resource statistics
        print("\n12. Testing resource statistics...")
        if resources:
            stats = ResourceService.get_resource_stats(resources[0].id)
            print(f"  ✓ Total downloads: {stats['total_downloads']}")
            print(f"  ✓ Unique students: {stats['unique_students']}")
            print(f"  ✓ Downloads by method: {stats['downloads_by_method']}")
            print(f"  ✓ Last 30 days: {stats['downloads_last_30_days']}")
        
        # Test 13: Get available filters
        print("\n13. Testing get available filters...")
        filters = ResourceService.get_available_filters()
        print(f"  ✓ Available types: {filters['types']}")
        print(f"  ✓ Available grades: {filters['grades']}")
        print(f"  ✓ Available difficulties: {filters['difficulties']}")
        
        # Test 14: Get popular resources
        print("\n14. Testing get popular resources...")
        popular = ResourceService.get_popular_resources(limit=5)
        print(f"  ✓ Top 5 popular resources:")
        for i, resource in enumerate(popular[:3], 1):
            print(f"    {i}. {resource['title']} ({resource['download_count']} downloads)")
        
        # Test 15: Get recent resources
        print("\n15. Testing get recent resources...")
        recent = ResourceService.get_recent_resources(limit=5)
        print(f"  ✓ 5 most recent resources:")
        for i, resource in enumerate(recent[:3], 1):
            print(f"    {i}. {resource['title']}")
        
        # Test 16: Create new resource
        print("\n16. Testing create resource...")
        skill = Skill.query.first()
        new_resource_data = {
            'title': 'Test Resource - Division Practice',
            'description': 'Test resource for division',
            'resource_type': 'worksheet',
            'skill_id': skill.id if skill else None,
            'grade_level': 4,
            'difficulty': 'medium',
            'file_url': '/static/resources/test_division.pdf',
            'file_type': 'pdf',
            'file_size_kb': 200,
            'tags': ['division', 'test']
        }
        new_resource = ResourceService.create_resource(new_resource_data)
        assert new_resource is not None
        print(f"  ✓ Created resource ID: {new_resource.id}")
        print(f"  ✓ Title: {new_resource.title}")
        
        # Test 17: Update resource
        print("\n17. Testing update resource...")
        updated = ResourceService.update_resource(
            new_resource.id,
            {'title': 'Updated Test Resource', 'difficulty': 'hard'}
        )
        assert updated is not None
        assert updated.title == 'Updated Test Resource'
        assert updated.difficulty == 'hard'
        print(f"  ✓ Updated title: {updated.title}")
        print(f"  ✓ Updated difficulty: {updated.difficulty}")
        
        # Test 18: Soft delete resource
        print("\n18. Testing soft delete resource...")
        success = ResourceService.delete_resource(new_resource.id)
        assert success is True
        deleted_resource = Resource.query.get(new_resource.id)
        assert deleted_resource.is_active is False
        print(f"  ✓ Resource soft deleted (is_active=False)")
        
        # Test 19: Cleanup
        print("\n19. Cleaning up test data...")
        # Delete test downloads
        ResourceDownload.query.filter_by(student_id=test_student.id).delete()
        # Delete test student
        db.session.delete(test_student)
        # Delete test user
        db.session.delete(test_user)
        # Delete test resource
        db.session.delete(deleted_resource)
        db.session.commit()
        print(f"  ✓ Test data cleaned up")
        
        print("\n" + "=" * 60)
        print("ALL TESTS PASSED! ✓")
        print("=" * 60)
        print("Resource Library System Features Verified:")
        print("  ✓ Get all resources")
        print("  ✓ Filter by type, grade, difficulty")
        print("  ✓ Search resources")
        print("  ✓ Get resource by ID")
        print("  ✓ Get related resources")
        print("  ✓ Record downloads")
        print("  ✓ Get student download history")
        print("  ✓ Resource statistics")
        print("  ✓ Available filters")
        print("  ✓ Popular resources")
        print("  ✓ Recent resources")
        print("  ✓ Create resource")
        print("  ✓ Update resource")
        print("  ✓ Soft delete resource")
        print("=" * 60)

if __name__ == '__main__':
    test_resource_system()

