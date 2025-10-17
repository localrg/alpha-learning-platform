"""
Script to populate sample interactive examples for testing.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from src.main import app
from src.database import db
from src.models.assessment import Skill
from src.services.example_service import ExampleService

# Sample interactive examples
SAMPLE_EXAMPLES = [
    {
        'skill_name': 'Basic Multiplication',
        'examples': [
            {
                'title': 'Multiplication as Repeated Addition',
                'description': 'See how multiplication is the same as adding the same number multiple times.',
                'example_type': 'number_line',
                'difficulty': 'beginner',
                'sequence_order': 0,
                'config': {
                    'min': 0,
                    'max': 20,
                    'start_value': 0,
                    'operation': 'multiply',
                    'factor1': 3,
                    'factor2': 4,
                    'show_jumps': True,
                    'show_labels': True,
                    'instructions': 'Watch how 3 × 4 means making 4 jumps of 3'
                }
            },
            {
                'title': 'Build a Multiplication Array',
                'description': 'Create an array to visualize multiplication as rows and columns.',
                'example_type': 'array',
                'difficulty': 'beginner',
                'sequence_order': 1,
                'config': {
                    'rows': 3,
                    'cols': 4,
                    'editable': True,
                    'show_equation': True,
                    'instructions': 'Click to fill cells and build a 3 × 4 array'
                }
            },
            {
                'title': 'Explore Different Arrays',
                'description': 'Try different array sizes to see how multiplication works.',
                'example_type': 'array',
                'difficulty': 'intermediate',
                'sequence_order': 2,
                'config': {
                    'rows': 5,
                    'cols': 6,
                    'editable': True,
                    'show_equation': True,
                    'allow_resize': True,
                    'instructions': 'Build different arrays and see the multiplication equations'
                }
            }
        ]
    },
    {
        'skill_name': 'Basic Addition',
        'examples': [
            {
                'title': 'Addition on the Number Line',
                'description': 'See addition as moving forward on a number line.',
                'example_type': 'number_line',
                'difficulty': 'beginner',
                'sequence_order': 0,
                'config': {
                    'min': 0,
                    'max': 20,
                    'start_value': 5,
                    'operation': 'add',
                    'operand': 3,
                    'show_jumps': True,
                    'show_labels': True,
                    'instructions': 'Start at 5 and jump forward 3 to find 5 + 3'
                }
            },
            {
                'title': 'Adding Larger Numbers',
                'description': 'Practice addition with larger numbers on the number line.',
                'example_type': 'number_line',
                'difficulty': 'intermediate',
                'sequence_order': 1,
                'config': {
                    'min': 0,
                    'max': 50,
                    'start_value': 12,
                    'operation': 'add',
                    'operand': 8,
                    'show_jumps': True,
                    'show_labels': True,
                    'instructions': 'Find 12 + 8 on the number line'
                }
            }
        ]
    },
    {
        'skill_name': 'Basic Subtraction',
        'examples': [
            {
                'title': 'Subtraction on the Number Line',
                'description': 'See subtraction as moving backward on a number line.',
                'example_type': 'number_line',
                'difficulty': 'beginner',
                'sequence_order': 0,
                'config': {
                    'min': 0,
                    'max': 20,
                    'start_value': 10,
                    'operation': 'subtract',
                    'operand': 4,
                    'show_jumps': True,
                    'show_labels': True,
                    'instructions': 'Start at 10 and jump backward 4 to find 10 - 4'
                }
            }
        ]
    }
]

def populate_examples():
    """Populate sample interactive examples."""
    print("=" * 60)
    print("POPULATING SAMPLE INTERACTIVE EXAMPLES")
    print("=" * 60)
    
    with app.app_context():
        total_examples = 0
        
        for skill_data in SAMPLE_EXAMPLES:
            skill_name = skill_data['skill_name']
            
            # Find skill by name
            skill = Skill.query.filter_by(name=skill_name).first()
            
            if not skill:
                print(f"\n⚠ Skill '{skill_name}' not found, skipping...")
                continue
            
            print(f"\n📐 Adding examples for: {skill_name}")
            
            for example_data in skill_data['examples']:
                try:
                    # Check if example already exists
                    from src.models.interactive_example import InteractiveExample
                    existing = InteractiveExample.query.filter_by(
                        skill_id=skill.id,
                        title=example_data['title']
                    ).first()
                    
                    if existing:
                        print(f"  ⏭ Skipping '{example_data['title']}' (already exists)")
                        continue
                    
                    # Create interactive example
                    example = ExampleService.create_example(
                        skill_id=skill.id,
                        title=example_data['title'],
                        example_type=example_data['example_type'],
                        config=example_data['config'],
                        description=example_data['description'],
                        difficulty=example_data['difficulty'],
                        sequence_order=example_data['sequence_order']
                    )
                    
                    print(f"  ✓ Added: {example_data['title']} ({example_data['example_type']}, {example_data['difficulty']})")
                    total_examples += 1
                    
                except Exception as e:
                    print(f"  ✗ Error adding '{example_data['title']}': {str(e)}")
        
        print("\n" + "=" * 60)
        print(f"COMPLETED: {total_examples} examples added")
        print("=" * 60)

if __name__ == '__main__':
    populate_examples()

