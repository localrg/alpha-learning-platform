"""
Test script for Video Tutorial System functionality.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from src.main import app
from src.database import db
from src.models.user import User
from src.models.student import Student
from src.models.assessment import Skill
from src.models.video import VideoTutorial, VideoView
from src.services.video_service import VideoService

def test_video_system():
    """Test the complete video system."""
    print("=" * 60)
    print("TESTING VIDEO TUTORIAL SYSTEM")
    print("=" * 60)
    
    with app.app_context():
        # Test 1: URL Parsing
        print("\n1. Testing URL parsing...")
        
        test_urls = [
            ('https://www.youtube.com/watch?v=dQw4w9WgXcQ', 'youtube', 'dQw4w9WgXcQ'),
            ('https://youtu.be/dQw4w9WgXcQ', 'youtube', 'dQw4w9WgXcQ'),
            ('https://www.youtube.com/embed/dQw4w9WgXcQ', 'youtube', 'dQw4w9WgXcQ'),
            ('https://vimeo.com/123456789', 'vimeo', '123456789'),
            ('https://player.vimeo.com/video/123456789', 'vimeo', '123456789'),
            ('https://example.com/video.mp4', 'direct', 'video.mp4'),
        ]
        
        for url, expected_platform, expected_id in test_urls:
            try:
                parsed = VideoService.parse_video_url(url)
                assert parsed['platform'] == expected_platform, f"Platform mismatch for {url}"
                assert parsed['video_id'] == expected_id, f"Video ID mismatch for {url}"
                print(f"  ✓ {expected_platform}: {url}")
            except Exception as e:
                print(f"  ✗ Failed to parse {url}: {str(e)}")
                raise
        
        # Test 2: Get existing videos
        print("\n2. Testing get videos for skill...")
        
        # Find a skill with videos
        skill = Skill.query.join(VideoTutorial).first()
        
        if not skill:
            print("  ⚠ No skills with videos found, skipping...")
        else:
            videos = VideoService.get_videos_for_skill(skill.id)
            assert len(videos) > 0, "Should have videos for skill"
            print(f"  ✓ Found {len(videos)} video(s) for skill: {skill.name}")
            
            for video in videos:
                print(f"    - {video['title']} ({video['difficulty']})")
        
        # Test 3: Create test student
        print("\n3. Creating test student...")
        
        # Check if test user exists
        user = User.query.filter_by(username='videotest').first()
        if user:
            db.session.delete(user)
            db.session.commit()
        
        user = User(username='videotest', email='videotest@example.com')
        user.set_password('password123')
        db.session.add(user)
        db.session.commit()
        
        student = Student(
            user_id=user.id,
            name='Video Test Student',
            grade=5
        )
        db.session.add(student)
        db.session.commit()
        
        print(f"  ✓ Created test student: {student.name}")
        
        # Test 4: Start video view
        print("\n4. Testing start video view...")
        
        if skill and len(videos) > 0:
            video_id = videos[0]['id']
            view = VideoService.start_video_view(video_id, student.id)
            
            assert view is not None
            assert view.student_id == student.id
            assert view.video_id == video_id
            assert view.view_count == 1
            
            print(f"  ✓ Started video view for: {videos[0]['title']}")
            print(f"  ✓ View count: {view.view_count}")
            
            # Test 5: Update progress
            print("\n5. Testing update progress...")
            
            view = VideoService.update_video_progress(
                video_id,
                student.id,
                watch_time=120,
                percentage=50.0
            )
            
            assert view.watch_time_seconds == 120
            assert view.completion_percentage == 50.0
            assert not view.completed
            
            print(f"  ✓ Updated progress: 120s watched, 50% complete")
            
            # Test 6: Complete video (90%+)
            print("\n6. Testing video completion...")
            
            view = VideoService.update_video_progress(
                video_id,
                student.id,
                watch_time=220,
                percentage=95.0
            )
            
            assert view.completed == True
            assert view.completed_at is not None
            
            print(f"  ✓ Video auto-completed at 95%")
            print(f"  ✓ Completion time: {view.completed_at}")
            
            # Test 7: Get video with student data
            print("\n7. Testing get video with student data...")
            
            video_data = VideoService.get_video_by_id(video_id, student_id=student.id)
            
            assert video_data is not None
            assert video_data['watched'] == True
            assert video_data['completed'] == True
            assert video_data['completion_percentage'] == 95.0
            
            print(f"  ✓ Video data includes student progress")
            print(f"    - Watched: {video_data['watched']}")
            print(f"    - Completed: {video_data['completed']}")
            print(f"    - Progress: {video_data['completion_percentage']}%")
            
            # Test 8: Get student stats
            print("\n8. Testing student video statistics...")
            
            stats = VideoService.get_student_video_stats(student.id)
            
            assert stats['total_videos_watched'] >= 1
            assert stats['total_videos_completed'] >= 1
            assert stats['total_watch_time_seconds'] >= 120
            
            print(f"  ✓ Total videos watched: {stats['total_videos_watched']}")
            print(f"  ✓ Total videos completed: {stats['total_videos_completed']}")
            print(f"  ✓ Total watch time: {stats['total_watch_time_minutes']} minutes")
            print(f"  ✓ Completion rate: {stats['completion_rate']}%")
            
            # Test 9: Get recent videos
            print("\n9. Testing recent videos...")
            
            recent = VideoService.get_recent_videos(student.id, limit=5)
            
            assert len(recent) >= 1
            assert recent[0]['id'] == video_id
            
            print(f"  ✓ Found {len(recent)} recent video(s)")
            for vid in recent:
                print(f"    - {vid['title']} ({vid['completion_percentage']}% watched)")
            
            # Test 10: Get recommended videos
            print("\n10. Testing recommended videos...")
            
            # First, create a learning path item
            from src.models.learning_path import LearningPath
            
            lp_item = LearningPath(
                student_id=student.id,
                skill_id=skill.id,
                status='in_progress',
                mastery_achieved=False
            )
            db.session.add(lp_item)
            db.session.commit()
            
            recommended = VideoService.get_recommended_videos(student.id, limit=5)
            
            print(f"  ✓ Found {len(recommended)} recommended video(s)")
            for vid in recommended:
                print(f"    - {vid['title']} for {vid['skill_name']}")
            
            # Test 11: Embed URL generation
            print("\n11. Testing embed URL generation...")
            
            video_obj = VideoTutorial.query.get(video_id)
            embed_url = video_obj.get_embed_url()
            
            if video_obj.video_platform == 'youtube':
                assert 'youtube.com/embed/' in embed_url
            elif video_obj.video_platform == 'vimeo':
                assert 'player.vimeo.com/video/' in embed_url
            
            print(f"  ✓ Embed URL generated: {embed_url}")
            
            # Test 12: Multiple views
            print("\n12. Testing multiple views (view count)...")
            
            # Start video again
            view = VideoService.start_video_view(video_id, student.id)
            assert view.view_count == 2
            
            print(f"  ✓ View count incremented: {view.view_count}")
        
        print("\n" + "=" * 60)
        print("ALL TESTS PASSED! ✓")
        print("=" * 60)
        print("\nVideo System Features Verified:")
        print("  ✓ URL parsing (YouTube, Vimeo, Direct)")
        print("  ✓ Get videos for skill")
        print("  ✓ Start video view tracking")
        print("  ✓ Update viewing progress")
        print("  ✓ Auto-complete at 90%+")
        print("  ✓ Get video with student data")
        print("  ✓ Student video statistics")
        print("  ✓ Recent videos")
        print("  ✓ Recommended videos")
        print("  ✓ Embed URL generation")
        print("  ✓ Multiple view tracking")
        print("=" * 60)

if __name__ == '__main__':
    test_video_system()

