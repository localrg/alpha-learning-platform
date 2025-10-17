"""
Script to populate sample video tutorials for testing.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from src.main import app
from src.database import db
from src.models.assessment import Skill
from src.services.video_service import VideoService

# Sample video data (using real educational YouTube videos)
SAMPLE_VIDEOS = [
    {
        'skill_name': 'Basic Multiplication',
        'videos': [
            {
                'title': 'Introduction to Multiplication',
                'description': 'Learn the basics of multiplication with simple examples and visual aids.',
                'video_url': 'https://www.youtube.com/watch?v=0x9cWC3WM9w',
                'difficulty': 'beginner',
                'duration': 240,
                'sequence_order': 0
            },
            {
                'title': 'Multiplication Strategies',
                'description': 'Discover different strategies to solve multiplication problems quickly and accurately.',
                'video_url': 'https://www.youtube.com/watch?v=JRlcXLxVGzg',
                'difficulty': 'intermediate',
                'duration': 360,
                'sequence_order': 1
            },
            {
                'title': 'Mental Math Tricks for Multiplication',
                'description': 'Learn shortcuts and tricks to multiply numbers in your head.',
                'video_url': 'https://www.youtube.com/watch?v=K0xgjUhEG3U',
                'difficulty': 'advanced',
                'duration': 300,
                'sequence_order': 2
            }
        ]
    },
    {
        'skill_name': 'Fractions',
        'videos': [
            {
                'title': 'What are Fractions?',
                'description': 'Understand what fractions are and how they represent parts of a whole.',
                'video_url': 'https://www.youtube.com/watch?v=uWyRTDyGq3U',
                'difficulty': 'beginner',
                'duration': 280,
                'sequence_order': 0
            },
            {
                'title': 'Adding and Subtracting Fractions',
                'description': 'Learn how to add and subtract fractions with the same and different denominators.',
                'video_url': 'https://www.youtube.com/watch?v=FPJDzwGWkqE',
                'difficulty': 'intermediate',
                'duration': 420,
                'sequence_order': 1
            }
        ]
    },
    {
        'skill_name': 'Division',
        'videos': [
            {
                'title': 'Introduction to Division',
                'description': 'Learn the concept of division and how it relates to multiplication.',
                'video_url': 'https://www.youtube.com/watch?v=WVIL2VuHVqc',
                'difficulty': 'beginner',
                'duration': 300,
                'sequence_order': 0
            },
            {
                'title': 'Long Division Step by Step',
                'description': 'Master the long division algorithm with clear step-by-step examples.',
                'video_url': 'https://www.youtube.com/watch?v=MTyFCfCGe5E',
                'difficulty': 'intermediate',
                'duration': 480,
                'sequence_order': 1
            }
        ]
    },
    {
        'skill_name': 'Decimals',
        'videos': [
            {
                'title': 'Understanding Decimals',
                'description': 'Learn what decimals are and how they relate to fractions and whole numbers.',
                'video_url': 'https://www.youtube.com/watch?v=vvwPJGAo7Gg',
                'difficulty': 'beginner',
                'duration': 320,
                'sequence_order': 0
            }
        ]
    },
    {
        'skill_name': 'Geometry Basics',
        'videos': [
            {
                'title': 'Introduction to Shapes',
                'description': 'Explore basic geometric shapes and their properties.',
                'video_url': 'https://www.youtube.com/watch?v=guNVhSVEmS0',
                'difficulty': 'beginner',
                'duration': 360,
                'sequence_order': 0
            }
        ]
    }
]

def populate_videos():
    """Populate sample video tutorials."""
    print("=" * 60)
    print("POPULATING SAMPLE VIDEO TUTORIALS")
    print("=" * 60)
    
    with app.app_context():
        total_videos = 0
        
        for skill_data in SAMPLE_VIDEOS:
            skill_name = skill_data['skill_name']
            
            # Find skill by name
            skill = Skill.query.filter_by(name=skill_name).first()
            
            if not skill:
                print(f"\n⚠ Skill '{skill_name}' not found, skipping...")
                continue
            
            print(f"\n📚 Adding videos for: {skill_name}")
            
            for video_data in skill_data['videos']:
                try:
                    # Check if video already exists
                    from src.models.video import VideoTutorial
                    existing = VideoTutorial.query.filter_by(
                        skill_id=skill.id,
                        title=video_data['title']
                    ).first()
                    
                    if existing:
                        print(f"  ⏭ Skipping '{video_data['title']}' (already exists)")
                        continue
                    
                    # Create video tutorial
                    video = VideoService.create_video_tutorial(
                        skill_id=skill.id,
                        title=video_data['title'],
                        video_url=video_data['video_url'],
                        description=video_data['description'],
                        difficulty=video_data['difficulty'],
                        duration=video_data['duration'],
                        sequence_order=video_data['sequence_order']
                    )
                    
                    print(f"  ✓ Added: {video_data['title']} ({video_data['difficulty']})")
                    total_videos += 1
                    
                except Exception as e:
                    print(f"  ✗ Error adding '{video_data['title']}': {str(e)}")
        
        print("\n" + "=" * 60)
        print(f"COMPLETED: {total_videos} videos added")
        print("=" * 60)

if __name__ == '__main__':
    populate_videos()

