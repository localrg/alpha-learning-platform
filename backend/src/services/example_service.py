"""
Example Service for managing interactive examples and tracking interactions.
"""
from src.database import db
from src.models.interactive_example import InteractiveExample, ExampleInteraction
from datetime import datetime


class ExampleService:
    """Service for managing interactive examples."""
    
    # Example type templates
    EXAMPLE_TYPES = {
        'number_line': {
            'name': 'Number Line',
            'description': 'Interactive number line for visualizing operations',
            'default_config': {
                'min': 0,
                'max': 20,
                'start_value': 0,
                'show_jumps': True,
                'show_labels': True
            }
        },
        'array': {
            'name': 'Array Grid',
            'description': 'Interactive grid for building arrays',
            'default_config': {
                'rows': 3,
                'cols': 4,
                'editable': True,
                'show_equation': True
            }
        },
        'fraction_circles': {
            'name': 'Fraction Circles',
            'description': 'Visual fraction representation with circles',
            'default_config': {
                'numerator': 1,
                'denominator': 2,
                'show_equivalence': False
            }
        },
        'fraction_bars': {
            'name': 'Fraction Bars',
            'description': 'Visual fraction representation with bars',
            'default_config': {
                'numerator': 1,
                'denominator': 2,
                'show_equivalence': False
            }
        },
        'place_value': {
            'name': 'Place Value Blocks',
            'description': 'Base-10 blocks for place value understanding',
            'default_config': {
                'value': 0,
                'show_trading': True,
                'max_value': 999
            }
        }
    }
    
    @staticmethod
    def create_example(skill_id, title, example_type, config=None, 
                      description=None, difficulty='beginner', sequence_order=0):
        """
        Create a new interactive example.
        
        Args:
            skill_id: ID of the skill
            title: Example title
            example_type: Type of example
            config: Configuration dictionary
            description: Example description
            difficulty: Difficulty level
            sequence_order: Order within skill
            
        Returns:
            InteractiveExample: Created example
        """
        # Validate example type
        if example_type not in ExampleService.EXAMPLE_TYPES:
            raise ValueError(f"Invalid example type: {example_type}")
        
        # Use default config if not provided
        if config is None:
            config = ExampleService.EXAMPLE_TYPES[example_type]['default_config'].copy()
        
        # Create example
        example = InteractiveExample(
            skill_id=skill_id,
            title=title,
            description=description,
            example_type=example_type,
            difficulty_level=difficulty,
            sequence_order=sequence_order
        )
        example.config = config
        
        db.session.add(example)
        db.session.commit()
        
        return example
    
    @staticmethod
    def get_examples_for_skill(skill_id, student_id=None):
        """
        Get all active examples for a skill.
        
        Args:
            skill_id: ID of the skill
            student_id: Optional student ID to include interaction data
            
        Returns:
            list: List of example dictionaries
        """
        examples = InteractiveExample.query.filter_by(
            skill_id=skill_id,
            is_active=True
        ).order_by(InteractiveExample.sequence_order).all()
        
        return [example.to_dict(student_id=student_id) for example in examples]
    
    @staticmethod
    def get_example_by_id(example_id, student_id=None):
        """
        Get a specific example by ID.
        
        Args:
            example_id: ID of the example
            student_id: Optional student ID to include interaction data
            
        Returns:
            dict: Example data
        """
        example = InteractiveExample.query.get(example_id)
        if not example:
            return None
        
        return example.to_dict(student_id=student_id)
    
    @staticmethod
    def start_interaction(example_id, student_id):
        """
        Record that a student started an interactive example.
        
        Args:
            example_id: ID of the example
            student_id: ID of the student
            
        Returns:
            ExampleInteraction: Interaction record
        """
        # Create new interaction record
        interaction = ExampleInteraction(
            example_id=example_id,
            student_id=student_id
        )
        
        db.session.add(interaction)
        db.session.commit()
        
        return interaction
    
    @staticmethod
    def log_interaction(interaction_id, action_data):
        """
        Log a student interaction action.
        
        Args:
            interaction_id: ID of the interaction
            action_data: Dictionary with action details
            
        Returns:
            ExampleInteraction: Updated interaction
        """
        interaction = ExampleInteraction.query.get(interaction_id)
        if not interaction:
            return None
        
        interaction.add_interaction(action_data)
        db.session.commit()
        
        return interaction
    
    @staticmethod
    def update_time_spent(interaction_id, time_spent):
        """
        Update time spent on an example.
        
        Args:
            interaction_id: ID of the interaction
            time_spent: Time in seconds
            
        Returns:
            ExampleInteraction: Updated interaction
        """
        interaction = ExampleInteraction.query.get(interaction_id)
        if not interaction:
            return None
        
        interaction.time_spent_seconds = time_spent
        db.session.commit()
        
        return interaction
    
    @staticmethod
    def complete_interaction(interaction_id):
        """
        Mark an interaction as completed.
        
        Args:
            interaction_id: ID of the interaction
            
        Returns:
            ExampleInteraction: Updated interaction
        """
        interaction = ExampleInteraction.query.get(interaction_id)
        if not interaction:
            return None
        
        if not interaction.completed:
            interaction.completed = True
            interaction.completed_at = datetime.utcnow()
            db.session.commit()
        
        return interaction
    
    @staticmethod
    def get_student_stats(student_id):
        """
        Get interaction statistics for a student.
        
        Args:
            student_id: ID of the student
            
        Returns:
            dict: Statistics
        """
        interactions = ExampleInteraction.query.filter_by(
            student_id=student_id
        ).all()
        
        total_examples = len(interactions)
        total_completed = len([i for i in interactions if i.completed])
        total_time = sum(i.time_spent_seconds for i in interactions)
        
        return {
            'total_examples_tried': total_examples,
            'total_examples_completed': total_completed,
            'total_time_seconds': total_time,
            'total_time_minutes': round(total_time / 60, 1),
            'completion_rate': round((total_completed / total_examples * 100), 1) if total_examples > 0 else 0
        }
    
    @staticmethod
    def get_recent_examples(student_id, limit=5):
        """
        Get recently interacted examples for a student.
        
        Args:
            student_id: ID of the student
            limit: Maximum number to return
            
        Returns:
            list: List of example dictionaries
        """
        interactions = ExampleInteraction.query.filter_by(
            student_id=student_id
        ).order_by(ExampleInteraction.started_at.desc()).limit(limit).all()
        
        result = []
        for interaction in interactions:
            example = InteractiveExample.query.get(interaction.example_id)
            if example:
                example_data = example.to_dict(student_id=student_id)
                result.append(example_data)
        
        return result
    
    @staticmethod
    def get_recommended_examples(student_id, limit=5):
        """
        Get recommended examples based on learning path.
        
        Args:
            student_id: ID of the student
            limit: Maximum number to return
            
        Returns:
            list: List of recommended examples
        """
        from src.models.learning_path import LearningPath
        
        # Get student's current learning path (non-mastered skills)
        learning_path = LearningPath.query.filter_by(
            student_id=student_id,
            mastery_achieved=False
        ).order_by(LearningPath.sequence_order).limit(limit).all()
        
        recommended = []
        for item in learning_path:
            # Get examples for this skill that student hasn't completed
            examples = InteractiveExample.query.filter_by(
                skill_id=item.skill_id,
                is_active=True
            ).order_by(InteractiveExample.sequence_order).all()
            
            for example in examples:
                # Check if student has completed this example
                interaction = ExampleInteraction.query.filter_by(
                    example_id=example.id,
                    student_id=student_id,
                    completed=True
                ).first()
                
                if not interaction:
                    recommended.append(example.to_dict(student_id=student_id))
                    if len(recommended) >= limit:
                        return recommended
        
        return recommended
    
    @staticmethod
    def get_example_types():
        """
        Get available example types with descriptions.
        
        Returns:
            dict: Example types
        """
        return ExampleService.EXAMPLE_TYPES

