"""
Populate sample educational resources.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from src.main import app
from src.database import db
from src.models.assessment import Skill
from src.services.resource_service import ResourceService

def populate_resources():
    """Create sample resources for the library."""
    with app.app_context():
        # Get a skill to link resources to
        skill = Skill.query.first()
        if not skill:
            print("No skills found. Please create skills first.")
            return
        
        print(f"Creating sample resources linked to skill: {skill.name}")
        print("=" * 60)
        
        # Sample resources
        resources_data = [
            {
                'title': 'Multiplication Practice - Basic Facts',
                'description': 'Practice basic multiplication facts 0-12 with 20 problems. Perfect for building fluency and speed.',
                'resource_type': 'worksheet',
                'skill_id': skill.id,
                'grade_level': 3,
                'difficulty': 'easy',
                'file_url': '/static/resources/worksheet_multiplication_basic_v1.pdf',
                'file_type': 'pdf',
                'file_size_kb': 245,
                'thumbnail_url': '/static/resources/thumbnails/worksheet_multiplication_basic.png',
                'tags': ['multiplication', 'basic facts', 'practice', 'fluency']
            },
            {
                'title': 'Multiplication Strategies Quick Reference',
                'description': 'Visual guide to multiplication strategies including repeated addition, skip counting, arrays, and number lines.',
                'resource_type': 'reference',
                'skill_id': skill.id,
                'grade_level': 3,
                'difficulty': 'medium',
                'file_url': '/static/resources/reference_multiplication_strategies_v1.pdf',
                'file_type': 'pdf',
                'file_size_kb': 180,
                'thumbnail_url': '/static/resources/thumbnails/reference_multiplication_strategies.png',
                'tags': ['multiplication', 'strategies', 'reference', 'visual']
            },
            {
                'title': 'Mixed Arithmetic Practice - Grade 3',
                'description': '50 mixed problems covering addition, subtraction, and multiplication. Includes word problems and real-world applications.',
                'resource_type': 'practice',
                'skill_id': skill.id,
                'grade_level': 3,
                'difficulty': 'medium',
                'file_url': '/static/resources/practice_mixed_arithmetic_grade3_v1.pdf',
                'file_type': 'pdf',
                'file_size_kb': 320,
                'thumbnail_url': '/static/resources/thumbnails/practice_mixed_arithmetic.png',
                'tags': ['mixed practice', 'arithmetic', 'word problems', 'grade 3']
            },
            {
                'title': 'Multiplication Mastery Study Guide',
                'description': 'Complete guide to understanding multiplication with visual models, strategies, common mistakes, and self-assessment.',
                'resource_type': 'study_guide',
                'skill_id': skill.id,
                'grade_level': 3,
                'difficulty': 'medium',
                'file_url': '/static/resources/study_guide_multiplication_mastery_v1.pdf',
                'file_type': 'pdf',
                'file_size_kb': 420,
                'thumbnail_url': '/static/resources/thumbnails/study_guide_multiplication.png',
                'tags': ['multiplication', 'study guide', 'concepts', 'strategies']
            },
            {
                'title': 'Multiplication Practice - Answer Key',
                'description': 'Complete answer key for Multiplication Practice - Basic Facts worksheet with step-by-step solutions.',
                'resource_type': 'answer_key',
                'skill_id': skill.id,
                'grade_level': 3,
                'difficulty': 'easy',
                'file_url': '/static/resources/answer_key_multiplication_basic_v1.pdf',
                'file_type': 'pdf',
                'file_size_kb': 150,
                'thumbnail_url': '/static/resources/thumbnails/answer_key_multiplication.png',
                'tags': ['multiplication', 'answer key', 'solutions']
            },
            {
                'title': 'Multiplication Arrays Visual Guide',
                'description': 'Colorful visual guide showing how to use arrays to understand multiplication. Great for visual learners.',
                'resource_type': 'reference',
                'skill_id': skill.id,
                'grade_level': 3,
                'difficulty': 'easy',
                'file_url': '/static/resources/reference_multiplication_arrays_v1.pdf',
                'file_type': 'pdf',
                'file_size_kb': 280,
                'thumbnail_url': '/static/resources/thumbnails/reference_arrays.png',
                'tags': ['multiplication', 'arrays', 'visual', 'models']
            },
            {
                'title': 'Times Tables Challenge - Grade 4',
                'description': 'Advanced multiplication practice for grade 4 students. Includes larger numbers and multi-step problems.',
                'resource_type': 'worksheet',
                'skill_id': skill.id,
                'grade_level': 4,
                'difficulty': 'hard',
                'file_url': '/static/resources/worksheet_times_tables_challenge_v1.pdf',
                'file_type': 'pdf',
                'file_size_kb': 290,
                'thumbnail_url': '/static/resources/thumbnails/worksheet_challenge.png',
                'tags': ['multiplication', 'challenge', 'advanced', 'grade 4']
            },
            {
                'title': 'Multiplication Word Problems',
                'description': '15 real-world word problems that require multiplication to solve. Includes space for work and answers.',
                'resource_type': 'practice',
                'skill_id': skill.id,
                'grade_level': 3,
                'difficulty': 'medium',
                'file_url': '/static/resources/practice_multiplication_word_problems_v1.pdf',
                'file_type': 'pdf',
                'file_size_kb': 265,
                'thumbnail_url': '/static/resources/thumbnails/practice_word_problems.png',
                'tags': ['multiplication', 'word problems', 'application', 'real-world']
            },
            {
                'title': 'Skip Counting Practice Sheet',
                'description': 'Practice skip counting by 2s, 3s, 4s, 5s, and 10s. Foundation for multiplication fluency.',
                'resource_type': 'worksheet',
                'skill_id': skill.id,
                'grade_level': 3,
                'difficulty': 'easy',
                'file_url': '/static/resources/worksheet_skip_counting_v1.pdf',
                'file_type': 'pdf',
                'file_size_kb': 195,
                'thumbnail_url': '/static/resources/thumbnails/worksheet_skip_counting.png',
                'tags': ['skip counting', 'multiplication', 'fluency', 'foundation']
            },
            {
                'title': 'Multiplication Facts 1-12 Chart',
                'description': 'Complete multiplication table from 1×1 to 12×12. Perfect for reference and memorization.',
                'resource_type': 'reference',
                'skill_id': skill.id,
                'grade_level': 3,
                'difficulty': 'easy',
                'file_url': '/static/resources/reference_multiplication_chart_v1.pdf',
                'file_type': 'pdf',
                'file_size_kb': 120,
                'thumbnail_url': '/static/resources/thumbnails/reference_chart.png',
                'tags': ['multiplication', 'chart', 'reference', 'facts']
            }
        ]
        
        created_count = 0
        
        for resource_data in resources_data:
            # Check if resource already exists
            from src.models.resource import Resource
            existing = Resource.query.filter_by(title=resource_data['title']).first()
            if existing:
                print(f"  ⚠ Resource already exists: {resource_data['title']}")
                continue
            
            # Create resource
            resource = ResourceService.create_resource(resource_data)
            print(f"  ✓ Created: {resource.title}")
            print(f"    Type: {resource.resource_type} | Grade: {resource.grade_level} | Difficulty: {resource.difficulty}")
            created_count += 1
        
        print("\n" + "=" * 60)
        print(f"✅ Successfully created {created_count} resources")
        print(f"Total resources in library: {len(Resource.query.filter_by(is_active=True).all())}")

if __name__ == '__main__':
    populate_resources()

