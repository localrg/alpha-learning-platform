"""
Seed script to populate the question bank with initial skills and questions.
This creates a comprehensive question bank for grades 3-5 mathematics.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from src.main import app
from src.database import db
from src.models.assessment import Skill, Question

# Skills data organized by grade level
SKILLS_DATA = [
    # Grade 3 Skills
    {
        "name": "Basic Multiplication",
        "description": "Multiply single-digit numbers (0-12)",
        "grade_level": 3,
        "subject_area": "arithmetic",
        "prerequisite_skill_ids": [],
        "mastery_threshold": 0.9
    },
    {
        "name": "Basic Division",
        "description": "Divide numbers within 100",
        "grade_level": 3,
        "subject_area": "arithmetic",
        "prerequisite_skill_ids": [],
        "mastery_threshold": 0.9
    },
    {
        "name": "Introduction to Fractions",
        "description": "Understand fractions as parts of a whole",
        "grade_level": 3,
        "subject_area": "fractions",
        "prerequisite_skill_ids": [],
        "mastery_threshold": 0.9
    },
    
    # Grade 4 Skills
    {
        "name": "Multi-Digit Multiplication",
        "description": "Multiply multi-digit numbers",
        "grade_level": 4,
        "subject_area": "arithmetic",
        "prerequisite_skill_ids": [1],  # Requires Basic Multiplication
        "mastery_threshold": 0.9
    },
    {
        "name": "Adding Fractions",
        "description": "Add fractions with like denominators",
        "grade_level": 4,
        "subject_area": "fractions",
        "prerequisite_skill_ids": [3],  # Requires Introduction to Fractions
        "mastery_threshold": 0.9
    },
    {
        "name": "Decimal Basics",
        "description": "Understand and compare decimals",
        "grade_level": 4,
        "subject_area": "decimals",
        "prerequisite_skill_ids": [],
        "mastery_threshold": 0.9
    },
    
    # Grade 5 Skills
    {
        "name": "Multiplying Fractions",
        "description": "Multiply fractions by whole numbers and fractions",
        "grade_level": 5,
        "subject_area": "fractions",
        "prerequisite_skill_ids": [5],  # Requires Adding Fractions
        "mastery_threshold": 0.9
    },
    {
        "name": "Decimal Operations",
        "description": "Add, subtract, multiply, and divide decimals",
        "grade_level": 5,
        "subject_area": "decimals",
        "prerequisite_skill_ids": [6],  # Requires Decimal Basics
        "mastery_threshold": 0.9
    },
    {
        "name": "Volume and Area",
        "description": "Calculate volume and area of basic shapes",
        "grade_level": 5,
        "subject_area": "geometry",
        "prerequisite_skill_ids": [4],  # Requires Multi-Digit Multiplication
        "mastery_threshold": 0.9
    },
]

# Questions data organized by skill
QUESTIONS_DATA = [
    # Basic Multiplication (Skill 1) - Grade 3
    {
        "skill_id": 1,
        "question_text": "What is 7 × 8?",
        "question_type": "multiple_choice",
        "correct_answer": "56",
        "options": ["48", "54", "56", "64"],
        "explanation": "7 × 8 = 56. You can think of it as 7 groups of 8, or 8 added together 7 times.",
        "difficulty": "medium",
        "grade_level": 3
    },
    {
        "skill_id": 1,
        "question_text": "What is 9 × 6?",
        "question_type": "multiple_choice",
        "correct_answer": "54",
        "options": ["45", "54", "63", "72"],
        "explanation": "9 × 6 = 54. This is 9 groups of 6.",
        "difficulty": "medium",
        "grade_level": 3
    },
    {
        "skill_id": 1,
        "question_text": "What is 12 × 5?",
        "question_type": "multiple_choice",
        "correct_answer": "60",
        "options": ["50", "55", "60", "65"],
        "explanation": "12 × 5 = 60. You can use the trick: 10 × 5 = 50, plus 2 × 5 = 10, so 50 + 10 = 60.",
        "difficulty": "hard",
        "grade_level": 3
    },
    {
        "skill_id": 1,
        "question_text": "What is 4 × 9?",
        "question_type": "multiple_choice",
        "correct_answer": "36",
        "options": ["32", "36", "40", "45"],
        "explanation": "4 × 9 = 36. This is 4 groups of 9.",
        "difficulty": "easy",
        "grade_level": 3
    },
    {
        "skill_id": 1,
        "question_text": "What is 8 × 7?",
        "question_type": "multiple_choice",
        "correct_answer": "56",
        "options": ["49", "54", "56", "63"],
        "explanation": "8 × 7 = 56. This is the same as 7 × 8.",
        "difficulty": "medium",
        "grade_level": 3
    },
    
    # Basic Division (Skill 2) - Grade 3
    {
        "skill_id": 2,
        "question_text": "What is 56 ÷ 8?",
        "question_type": "multiple_choice",
        "correct_answer": "7",
        "options": ["6", "7", "8", "9"],
        "explanation": "56 ÷ 8 = 7. Division is the opposite of multiplication: 8 × 7 = 56.",
        "difficulty": "medium",
        "grade_level": 3
    },
    {
        "skill_id": 2,
        "question_text": "What is 45 ÷ 9?",
        "question_type": "multiple_choice",
        "correct_answer": "5",
        "options": ["4", "5", "6", "7"],
        "explanation": "45 ÷ 9 = 5. Think: 9 × 5 = 45.",
        "difficulty": "easy",
        "grade_level": 3
    },
    {
        "skill_id": 2,
        "question_text": "What is 72 ÷ 6?",
        "question_type": "multiple_choice",
        "correct_answer": "12",
        "options": ["10", "11", "12", "13"],
        "explanation": "72 ÷ 6 = 12. Think: 6 × 12 = 72.",
        "difficulty": "hard",
        "grade_level": 3
    },
    {
        "skill_id": 2,
        "question_text": "What is 36 ÷ 4?",
        "question_type": "multiple_choice",
        "correct_answer": "9",
        "options": ["7", "8", "9", "10"],
        "explanation": "36 ÷ 4 = 9. Think: 4 × 9 = 36.",
        "difficulty": "medium",
        "grade_level": 3
    },
    {
        "skill_id": 2,
        "question_text": "What is 81 ÷ 9?",
        "question_type": "multiple_choice",
        "correct_answer": "9",
        "options": ["7", "8", "9", "10"],
        "explanation": "81 ÷ 9 = 9. Think: 9 × 9 = 81.",
        "difficulty": "medium",
        "grade_level": 3
    },
    
    # Introduction to Fractions (Skill 3) - Grade 3
    {
        "skill_id": 3,
        "question_text": "What fraction of the circle is shaded if 3 out of 4 equal parts are shaded?",
        "question_type": "multiple_choice",
        "correct_answer": "3/4",
        "options": ["1/4", "2/4", "3/4", "4/4"],
        "explanation": "3/4 means 3 parts out of 4 total parts are shaded.",
        "difficulty": "easy",
        "grade_level": 3
    },
    {
        "skill_id": 3,
        "question_text": "Which fraction is equivalent to one half?",
        "question_type": "multiple_choice",
        "correct_answer": "2/4",
        "options": ["1/4", "2/4", "3/4", "1/3"],
        "explanation": "2/4 = 1/2 because 2 is half of 4, just like 1 is half of 2.",
        "difficulty": "medium",
        "grade_level": 3
    },
    {
        "skill_id": 3,
        "question_text": "What is 1/2 + 1/2?",
        "question_type": "multiple_choice",
        "correct_answer": "1",
        "options": ["1/4", "1/2", "1", "2"],
        "explanation": "1/2 + 1/2 = 2/2 = 1 whole.",
        "difficulty": "easy",
        "grade_level": 3
    },
    {
        "skill_id": 3,
        "question_text": "Which is larger: 1/3 or 1/4?",
        "question_type": "multiple_choice",
        "correct_answer": "1/3",
        "options": ["1/3", "1/4", "They are equal", "Cannot determine"],
        "explanation": "1/3 is larger. When the numerator is the same, the fraction with the smaller denominator is larger.",
        "difficulty": "medium",
        "grade_level": 3
    },
    {
        "skill_id": 3,
        "question_text": "What fraction represents 'none' of something?",
        "question_type": "multiple_choice",
        "correct_answer": "0/1",
        "options": ["0/1", "1/1", "1/2", "1/0"],
        "explanation": "0/1 = 0, which represents none or zero parts.",
        "difficulty": "easy",
        "grade_level": 3
    },
    
    # Multi-Digit Multiplication (Skill 4) - Grade 4
    {
        "skill_id": 4,
        "question_text": "What is 23 × 4?",
        "question_type": "multiple_choice",
        "correct_answer": "92",
        "options": ["82", "88", "92", "96"],
        "explanation": "23 × 4 = 92. Break it down: (20 × 4) + (3 × 4) = 80 + 12 = 92.",
        "difficulty": "medium",
        "grade_level": 4
    },
    {
        "skill_id": 4,
        "question_text": "What is 15 × 6?",
        "question_type": "multiple_choice",
        "correct_answer": "90",
        "options": ["80", "85", "90", "95"],
        "explanation": "15 × 6 = 90. You can use: (10 × 6) + (5 × 6) = 60 + 30 = 90.",
        "difficulty": "easy",
        "grade_level": 4
    },
    {
        "skill_id": 4,
        "question_text": "What is 47 × 3?",
        "question_type": "multiple_choice",
        "correct_answer": "141",
        "options": ["131", "137", "141", "147"],
        "explanation": "47 × 3 = 141. Break it down: (40 × 3) + (7 × 3) = 120 + 21 = 141.",
        "difficulty": "hard",
        "grade_level": 4
    },
    {
        "skill_id": 4,
        "question_text": "What is 32 × 5?",
        "question_type": "multiple_choice",
        "correct_answer": "160",
        "options": ["150", "155", "160", "165"],
        "explanation": "32 × 5 = 160. Use: (30 × 5) + (2 × 5) = 150 + 10 = 160.",
        "difficulty": "medium",
        "grade_level": 4
    },
    {
        "skill_id": 4,
        "question_text": "What is 18 × 7?",
        "question_type": "multiple_choice",
        "correct_answer": "126",
        "options": ["116", "121", "126", "132"],
        "explanation": "18 × 7 = 126. Use: (10 × 7) + (8 × 7) = 70 + 56 = 126.",
        "difficulty": "hard",
        "grade_level": 4
    },
    
    # Adding Fractions (Skill 5) - Grade 4
    {
        "skill_id": 5,
        "question_text": "What is 1/4 + 2/4?",
        "question_type": "multiple_choice",
        "correct_answer": "3/4",
        "options": ["2/4", "3/4", "3/8", "4/4"],
        "explanation": "1/4 + 2/4 = 3/4. When denominators are the same, just add the numerators.",
        "difficulty": "easy",
        "grade_level": 4
    },
    {
        "skill_id": 5,
        "question_text": "What is 2/5 + 1/5?",
        "question_type": "multiple_choice",
        "correct_answer": "3/5",
        "options": ["2/5", "3/5", "3/10", "4/5"],
        "explanation": "2/5 + 1/5 = 3/5. Add the numerators: 2 + 1 = 3, keep the denominator 5.",
        "difficulty": "easy",
        "grade_level": 4
    },
    {
        "skill_id": 5,
        "question_text": "What is 3/8 + 4/8?",
        "question_type": "multiple_choice",
        "correct_answer": "7/8",
        "options": ["6/8", "7/8", "7/16", "8/8"],
        "explanation": "3/8 + 4/8 = 7/8. Add the numerators: 3 + 4 = 7.",
        "difficulty": "medium",
        "grade_level": 4
    },
    {
        "skill_id": 5,
        "question_text": "What is 1/3 + 1/3?",
        "question_type": "multiple_choice",
        "correct_answer": "2/3",
        "options": ["1/3", "2/3", "2/6", "3/3"],
        "explanation": "1/3 + 1/3 = 2/3. Add the numerators: 1 + 1 = 2.",
        "difficulty": "easy",
        "grade_level": 4
    },
    {
        "skill_id": 5,
        "question_text": "What is 5/6 + 1/6?",
        "question_type": "multiple_choice",
        "correct_answer": "1",
        "options": ["5/6", "6/6", "1", "6/12"],
        "explanation": "5/6 + 1/6 = 6/6 = 1. When the numerator equals the denominator, it equals 1 whole.",
        "difficulty": "medium",
        "grade_level": 4
    },
    
    # Decimal Basics (Skill 6) - Grade 4
    {
        "skill_id": 6,
        "question_text": "Which decimal is equivalent to 1/2?",
        "question_type": "multiple_choice",
        "correct_answer": "0.5",
        "options": ["0.2", "0.5", "0.25", "0.75"],
        "explanation": "1/2 = 0.5 because 1 divided by 2 equals 0.5.",
        "difficulty": "easy",
        "grade_level": 4
    },
    {
        "skill_id": 6,
        "question_text": "Which is larger: 0.7 or 0.5?",
        "question_type": "multiple_choice",
        "correct_answer": "0.7",
        "options": ["0.7", "0.5", "They are equal", "Cannot determine"],
        "explanation": "0.7 is larger than 0.5. Think of it as 7 tenths vs 5 tenths.",
        "difficulty": "easy",
        "grade_level": 4
    },
    {
        "skill_id": 6,
        "question_text": "What is 0.3 + 0.4?",
        "question_type": "multiple_choice",
        "correct_answer": "0.7",
        "options": ["0.6", "0.7", "0.8", "0.12"],
        "explanation": "0.3 + 0.4 = 0.7. Add the tenths: 3 + 4 = 7 tenths.",
        "difficulty": "medium",
        "grade_level": 4
    },
    {
        "skill_id": 6,
        "question_text": "Which decimal is equivalent to 3/4?",
        "question_type": "multiple_choice",
        "correct_answer": "0.75",
        "options": ["0.25", "0.5", "0.75", "0.34"],
        "explanation": "3/4 = 0.75 because 3 divided by 4 equals 0.75.",
        "difficulty": "hard",
        "grade_level": 4
    },
    {
        "skill_id": 6,
        "question_text": "What is 1.0 - 0.6?",
        "question_type": "multiple_choice",
        "correct_answer": "0.4",
        "options": ["0.3", "0.4", "0.5", "0.6"],
        "explanation": "1.0 - 0.6 = 0.4. Think: 10 tenths - 6 tenths = 4 tenths.",
        "difficulty": "medium",
        "grade_level": 4
    },
    
    # Multiplying Fractions (Skill 7) - Grade 5
    {
        "skill_id": 7,
        "question_text": "What is 1/2 × 4?",
        "question_type": "multiple_choice",
        "correct_answer": "2",
        "options": ["1", "2", "4", "8"],
        "explanation": "1/2 × 4 = 4/2 = 2. Multiply the numerator by the whole number.",
        "difficulty": "easy",
        "grade_level": 5
    },
    {
        "skill_id": 7,
        "question_text": "What is 1/3 × 1/2?",
        "question_type": "multiple_choice",
        "correct_answer": "1/6",
        "options": ["1/5", "1/6", "2/5", "2/6"],
        "explanation": "1/3 × 1/2 = 1/6. Multiply numerators (1×1=1) and denominators (3×2=6).",
        "difficulty": "medium",
        "grade_level": 5
    },
    {
        "skill_id": 7,
        "question_text": "What is 2/3 × 3?",
        "question_type": "multiple_choice",
        "correct_answer": "2",
        "options": ["1", "2", "3", "6"],
        "explanation": "2/3 × 3 = 6/3 = 2. Multiply 2 × 3 = 6, then divide by 3.",
        "difficulty": "medium",
        "grade_level": 5
    },
    {
        "skill_id": 7,
        "question_text": "What is 1/4 × 1/4?",
        "question_type": "multiple_choice",
        "correct_answer": "1/16",
        "options": ["1/8", "1/16", "2/8", "1/2"],
        "explanation": "1/4 × 1/4 = 1/16. Multiply: 1×1=1 and 4×4=16.",
        "difficulty": "hard",
        "grade_level": 5
    },
    {
        "skill_id": 7,
        "question_text": "What is 3/5 × 2?",
        "question_type": "multiple_choice",
        "correct_answer": "6/5",
        "options": ["5/5", "6/5", "3/10", "6/10"],
        "explanation": "3/5 × 2 = 6/5. Multiply the numerator: 3 × 2 = 6.",
        "difficulty": "medium",
        "grade_level": 5
    },
    
    # Decimal Operations (Skill 8) - Grade 5
    {
        "skill_id": 8,
        "question_text": "What is 2.5 + 1.3?",
        "question_type": "multiple_choice",
        "correct_answer": "3.8",
        "options": ["3.7", "3.8", "3.9", "4.8"],
        "explanation": "2.5 + 1.3 = 3.8. Add whole numbers (2+1=3) and decimals (0.5+0.3=0.8).",
        "difficulty": "easy",
        "grade_level": 5
    },
    {
        "skill_id": 8,
        "question_text": "What is 5.0 - 2.7?",
        "question_type": "multiple_choice",
        "correct_answer": "2.3",
        "options": ["2.3", "2.7", "3.3", "3.7"],
        "explanation": "5.0 - 2.7 = 2.3. Subtract: 5.0 - 2.0 = 3.0, then 3.0 - 0.7 = 2.3.",
        "difficulty": "medium",
        "grade_level": 5
    },
    {
        "skill_id": 8,
        "question_text": "What is 0.5 × 4?",
        "question_type": "multiple_choice",
        "correct_answer": "2.0",
        "options": ["1.0", "1.5", "2.0", "2.5"],
        "explanation": "0.5 × 4 = 2.0. Think: 1/2 × 4 = 2.",
        "difficulty": "easy",
        "grade_level": 5
    },
    {
        "skill_id": 8,
        "question_text": "What is 1.2 × 3?",
        "question_type": "multiple_choice",
        "correct_answer": "3.6",
        "options": ["3.2", "3.5", "3.6", "4.2"],
        "explanation": "1.2 × 3 = 3.6. Multiply: 1 × 3 = 3, and 0.2 × 3 = 0.6, so 3 + 0.6 = 3.6.",
        "difficulty": "medium",
        "grade_level": 5
    },
    {
        "skill_id": 8,
        "question_text": "What is 4.8 ÷ 2?",
        "question_type": "multiple_choice",
        "correct_answer": "2.4",
        "options": ["2.2", "2.4", "2.6", "2.8"],
        "explanation": "4.8 ÷ 2 = 2.4. Divide both the whole number and decimal: 4÷2=2, 0.8÷2=0.4.",
        "difficulty": "medium",
        "grade_level": 5
    },
    
    # Volume and Area (Skill 9) - Grade 5
    {
        "skill_id": 9,
        "question_text": "What is the area of a rectangle with length 8 and width 5?",
        "question_type": "multiple_choice",
        "correct_answer": "40",
        "options": ["26", "32", "40", "48"],
        "explanation": "Area = length × width = 8 × 5 = 40 square units.",
        "difficulty": "easy",
        "grade_level": 5
    },
    {
        "skill_id": 9,
        "question_text": "What is the volume of a cube with side length 3?",
        "question_type": "multiple_choice",
        "correct_answer": "27",
        "options": ["9", "18", "27", "36"],
        "explanation": "Volume = side × side × side = 3 × 3 × 3 = 27 cubic units.",
        "difficulty": "medium",
        "grade_level": 5
    },
    {
        "skill_id": 9,
        "question_text": "What is the area of a square with side length 7?",
        "question_type": "multiple_choice",
        "correct_answer": "49",
        "options": ["28", "42", "49", "56"],
        "explanation": "Area = side × side = 7 × 7 = 49 square units.",
        "difficulty": "easy",
        "grade_level": 5
    },
    {
        "skill_id": 9,
        "question_text": "What is the volume of a rectangular prism with length 4, width 3, and height 2?",
        "question_type": "multiple_choice",
        "correct_answer": "24",
        "options": ["18", "20", "24", "28"],
        "explanation": "Volume = length × width × height = 4 × 3 × 2 = 24 cubic units.",
        "difficulty": "hard",
        "grade_level": 5
    },
    {
        "skill_id": 9,
        "question_text": "What is the area of a rectangle with length 12 and width 6?",
        "question_type": "multiple_choice",
        "correct_answer": "72",
        "options": ["36", "54", "72", "84"],
        "explanation": "Area = length × width = 12 × 6 = 72 square units.",
        "difficulty": "medium",
        "grade_level": 5
    },
]


def seed_question_bank():
    """Seed the database with skills and questions."""
    with app.app_context():
        print("=" * 70)
        print("SEEDING QUESTION BANK")
        print("=" * 70)
        
        # Check if data already exists
        existing_skills = Skill.query.count()
        if existing_skills > 0:
            print(f"\n⚠️  Database already has {existing_skills} skills.")
            response = input("Do you want to clear and re-seed? (yes/no): ")
            if response.lower() != 'yes':
                print("Seeding cancelled.")
                return
            
            # Clear existing data
            print("\n[CLEANUP] Clearing existing data...")
            Question.query.delete()
            Skill.query.delete()
            db.session.commit()
            print("✓ Existing data cleared")
        
        # Create skills
        print(f"\n[SKILLS] Creating {len(SKILLS_DATA)} skills...")
        skills = []
        for skill_data in SKILLS_DATA:
            skill = Skill(**skill_data)
            db.session.add(skill)
            skills.append(skill)
        db.session.commit()
        print(f"✓ Created {len(skills)} skills")
        
        # Display skills
        for skill in skills:
            prereqs = f" (requires: {skill.prerequisite_skill_ids})" if skill.prerequisite_skill_ids else ""
            print(f"  - [{skill.id}] {skill.name} (Grade {skill.grade_level}){prereqs}")
        
        # Create questions
        print(f"\n[QUESTIONS] Creating {len(QUESTIONS_DATA)} questions...")
        questions = []
        for question_data in QUESTIONS_DATA:
            question = Question(**question_data)
            db.session.add(question)
            questions.append(question)
        db.session.commit()
        print(f"✓ Created {len(questions)} questions")
        
        # Display question count by skill
        print("\n[SUMMARY] Questions per skill:")
        for skill in skills:
            q_count = len(skill.questions)
            print(f"  - {skill.name}: {q_count} questions")
        
        # Display statistics
        print("\n[STATISTICS]")
        print(f"  Total Skills: {len(skills)}")
        print(f"  Total Questions: {len(questions)}")
        print(f"  Grade 3 Skills: {sum(1 for s in skills if s.grade_level == 3)}")
        print(f"  Grade 4 Skills: {sum(1 for s in skills if s.grade_level == 4)}")
        print(f"  Grade 5 Skills: {sum(1 for s in skills if s.grade_level == 5)}")
        print(f"  Easy Questions: {sum(1 for q in questions if q.difficulty == 'easy')}")
        print(f"  Medium Questions: {sum(1 for q in questions if q.difficulty == 'medium')}")
        print(f"  Hard Questions: {sum(1 for q in questions if q.difficulty == 'hard')}")
        
        print("\n" + "=" * 70)
        print("QUESTION BANK SEEDED SUCCESSFULLY! ✓")
        print("=" * 70)


if __name__ == '__main__':
    seed_question_bank()

