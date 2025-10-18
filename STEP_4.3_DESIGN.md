# Step 4.3: Hint System - Design Document

**Date:** October 17, 2025  
**Status:** 🔄 In Progress  
**Week:** 4 - Content & Resources

---

## Overview

Step 4.3 implements an intelligent hint system that provides progressive, context-aware hints to help students when they're stuck. The system supports independent problem-solving by scaffolding understanding without giving away answers, following best practices in educational psychology and cognitive science.

---

## Goals

### Primary Goals
1. Provide progressive hints (increasing specificity)
2. Support independent problem-solving
3. Never give away the answer directly
4. Track hint usage for analytics
5. Adapt to student needs

### Secondary Goals
1. Generate hints automatically for question types
2. Allow custom hints for specific questions
3. Provide visual and textual hints
4. Track hint effectiveness
5. Reduce frustration without reducing challenge

---

## Hint Philosophy

### Progressive Disclosure

Hints should follow a progression from general to specific:

**Level 1: Strategic Hint** - Suggests a general approach or strategy
- "Think about what operation you need to use"
- "Try breaking this into smaller parts"

**Level 2: Conceptual Hint** - Reminds of relevant concepts
- "Remember that multiplication means repeated addition"
- "Think about place value when regrouping"

**Level 3: Procedural Hint** - Guides through specific steps
- "First, multiply the ones place: 3 × 4"
- "Start by finding the common denominator"

**Level 4: Worked Example** - Shows a similar problem solved
- "Here's how to solve 2 × 3: 2 + 2 + 2 = 6"
- "Example: 1/2 + 1/4 = 2/4 + 1/4 = 3/4"

### Scaffolding Principles

1. **Zone of Proximal Development** - Hints should bridge the gap between what students can do alone and with support
2. **Fading** - As students improve, hints should become less specific
3. **Just-in-Time** - Hints provided when needed, not preemptively
4. **Metacognitive** - Hints encourage thinking about thinking

---

## System Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Hint System                           │
├─────────────────────────────────────────────────────────┤
│                                                           │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │   Database   │  │   Backend    │  │   Frontend   │  │
│  │              │  │              │  │              │  │
│  │ • Hints      │  │ • Hint       │  │ • Hint       │  │
│  │ • Usage      │  │   Generator  │  │   Interface  │  │
│  │   Tracking   │  │ • API Routes │  │ • Progressive│  │
│  │              │  │ • Analytics  │  │   Reveal     │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
│                                                           │
└─────────────────────────────────────────────────────────┘
```

---

## Database Schema

### New Table: Hint

```python
class Hint(db.Model):
    id = Integer (Primary Key)
    question_id = Integer (Foreign Key -> questions.id)
    
    # Hint content
    hint_level = Integer  # 1-4 (strategic, conceptual, procedural, example)
    hint_text = Text
    hint_type = String(20)  # 'text', 'visual', 'example'
    
    # Optional visual hint
    image_url = String(500)
    
    # Metadata
    sequence_order = Integer
    is_active = Boolean
    
    # Timestamps
    created_at = DateTime
    updated_at = DateTime
```

### New Table: HintUsage

```python
class HintUsage(db.Model):
    id = Integer (Primary Key)
    student_id = Integer (Foreign Key -> students.id)
    question_id = Integer (Foreign Key -> questions.id)
    hint_id = Integer (Foreign Key -> hints.id)
    
    # Usage tracking
    hint_level = Integer
    viewed_at = DateTime
    helpful = Boolean (nullable)  # Student feedback
    
    # Context
    attempt_number = Integer  # Which attempt when hint was used
    time_before_hint = Integer  # Seconds before requesting hint
    
    # Outcome
    answered_correctly = Boolean (nullable)
    attempts_after_hint = Integer
```

---

## Hint Generation Strategy

### Automatic Hint Generation

For common question types, generate hints automatically:

#### Multiplication Questions

**Question:** "What is 3 × 4?"

**Level 1 (Strategic):** "Think about what multiplication means. How can you use addition to solve this?"

**Level 2 (Conceptual):** "Multiplication is repeated addition. 3 × 4 means adding 3 four times."

**Level 3 (Procedural):** "Start with 0, then add 3 four times: 0 + 3 + 3 + 3 + 3"

**Level 4 (Example):** "Here's a similar problem: 2 × 3 = 2 + 2 + 2 = 6"

#### Addition Questions

**Question:** "What is 47 + 28?"

**Level 1 (Strategic):** "Try breaking the numbers into tens and ones."

**Level 2 (Conceptual):** "Remember to add the ones place first, then the tens place."

**Level 3 (Procedural):** "First add the ones: 7 + 8 = 15. Write down 5 and carry the 1."

**Level 4 (Example):** "Example: 34 + 19 = (30 + 10) + (4 + 9) = 40 + 13 = 53"

#### Fraction Questions

**Question:** "What is 1/2 + 1/4?"

**Level 1 (Strategic):** "Think about finding a common denominator."

**Level 2 (Conceptual):** "To add fractions, they need the same denominator."

**Level 3 (Procedural):** "Convert 1/2 to fourths: 1/2 = 2/4. Now add: 2/4 + 1/4"

**Level 4 (Example):** "Example: 1/3 + 1/6 = 2/6 + 1/6 = 3/6 = 1/2"

### Custom Hints

For complex or unique questions, teachers can create custom hints:

```python
{
  "question_id": 123,
  "hints": [
    {
      "level": 1,
      "type": "text",
      "text": "Think about the pattern in the numbers"
    },
    {
      "level": 2,
      "type": "visual",
      "text": "Look at this diagram",
      "image_url": "/images/hints/pattern_hint.png"
    },
    {
      "level": 3,
      "type": "text",
      "text": "Each number is 5 more than the previous one"
    },
    {
      "level": 4,
      "type": "example",
      "text": "If the pattern is 2, 4, 6, the next number is 8"
    }
  ]
}
```

---

## Hint Templates by Question Type

### Template: Basic Arithmetic

```python
ARITHMETIC_HINTS = {
    'addition': {
        1: "Think about combining the numbers together.",
        2: "Addition means putting groups together. Start with the ones place.",
        3: "Add the ones: {ones1} + {ones2}. Then add the tens: {tens1} + {tens2}.",
        4: "Example: {example_num1} + {example_num2} = {example_result}"
    },
    'subtraction': {
        1: "Think about taking away or finding the difference.",
        2: "Subtraction means removing from a group. Start with the ones place.",
        3: "Subtract the ones: {ones1} - {ones2}. Then subtract the tens: {tens1} - {tens2}.",
        4: "Example: {example_num1} - {example_num2} = {example_result}"
    },
    'multiplication': {
        1: "Think about repeated addition or groups of items.",
        2: "Multiplication means adding the same number multiple times.",
        3: "Add {factor1} to itself {factor2} times: {step_by_step}",
        4: "Example: {example_factor1} × {example_factor2} = {example_result}"
    },
    'division': {
        1: "Think about splitting into equal groups.",
        2: "Division means sharing equally or repeated subtraction.",
        3: "How many groups of {divisor} fit into {dividend}?",
        4: "Example: {example_dividend} ÷ {example_divisor} = {example_result}"
    }
}
```

### Template: Fractions

```python
FRACTION_HINTS = {
    'addition': {
        1: "Think about whether the denominators are the same.",
        2: "To add fractions, you need a common denominator.",
        3: "Convert {fraction1} to have denominator {common_denom}: {converted1}. Now add.",
        4: "Example: 1/3 + 1/6 = 2/6 + 1/6 = 3/6 = 1/2"
    },
    'comparison': {
        1: "Think about which piece is larger.",
        2: "Compare fractions by finding a common denominator or visualizing.",
        3: "Convert both to denominator {common_denom}: {fraction1_converted} and {fraction2_converted}",
        4: "Example: 1/2 vs 1/3 → 3/6 vs 2/6, so 1/2 > 1/3"
    }
}
```

---

## API Endpoints

### Hint Management

#### GET `/api/hints/question/<question_id>`
Get all hints for a question.

**Response:**
```json
{
  "hints": [
    {
      "id": 1,
      "question_id": 123,
      "hint_level": 1,
      "hint_text": "Think about what operation to use",
      "hint_type": "text",
      "image_url": null
    },
    {
      "id": 2,
      "question_id": 123,
      "hint_level": 2,
      "hint_text": "Multiplication is repeated addition",
      "hint_type": "text",
      "image_url": null
    }
  ],
  "total_hints": 2
}
```

#### POST `/api/hints/request`
Request a hint for a question.

**Request:**
```json
{
  "question_id": 123,
  "current_level": 0,
  "attempt_number": 2
}
```

**Response:**
```json
{
  "hint": {
    "id": 1,
    "hint_level": 1,
    "hint_text": "Think about what operation to use",
    "hint_type": "text",
    "image_url": null
  },
  "next_level_available": true,
  "total_levels": 4
}
```

#### POST `/api/hints/usage`
Record hint usage.

**Request:**
```json
{
  "hint_id": 1,
  "question_id": 123,
  "attempt_number": 2,
  "time_before_hint": 45
}
```

#### PUT `/api/hints/usage/<usage_id>/feedback`
Record hint helpfulness.

**Request:**
```json
{
  "helpful": true,
  "answered_correctly": true,
  "attempts_after_hint": 1
}
```

#### GET `/api/hints/stats`
Get hint usage statistics for student.

**Response:**
```json
{
  "total_hints_used": 15,
  "hints_by_level": {
    "1": 8,
    "2": 5,
    "3": 2,
    "4": 0
  },
  "average_level": 1.6,
  "helpful_rate": 0.87,
  "success_rate_after_hint": 0.73
}
```

---

## Frontend Components

### HintButton Component

**Features:**
- Shows hint availability
- Displays current hint level
- Indicates remaining hints
- Disabled when no hints available

**States:**
- Default: "💡 Get Hint"
- Loading: "Loading hint..."
- Level indicator: "💡 Get Hint (Level 1/4)"
- No more: "No more hints available"

### HintDisplay Component

**Features:**
- Progressive reveal of hints
- Visual hint support (images)
- Example formatting
- Helpfulness feedback
- Collapse/expand functionality

**Design:**
- Color-coded by level
  - Level 1: Blue (strategic)
  - Level 2: Purple (conceptual)
  - Level 3: Orange (procedural)
  - Level 4: Green (example)
- Icon per hint type
- Clear, readable typography
- Smooth animations

### HintHistory Component

**Features:**
- Shows all hints viewed
- Collapsible list
- Level indicators
- Timestamp display

---

## User Experience Flow

### Requesting Hints

1. **Student clicks "Get Hint" button**
   - System checks available hints
   - Records request with timestamp
   - Returns next level hint

2. **Hint displays progressively**
   - Animated reveal
   - Color-coded by level
   - Clear formatting

3. **Student can request more hints**
   - Each click reveals next level
   - Maximum 4 levels per question
   - Clear indication of remaining hints

4. **After using hint**
   - Student attempts question
   - System tracks outcome
   - Optionally asks for feedback

### Hint Feedback Loop

1. **After answering (correctly or incorrectly)**
   - "Was this hint helpful?" prompt
   - Thumbs up/down buttons
   - Optional text feedback

2. **System learns from feedback**
   - Track helpful vs unhelpful hints
   - Identify confusing hints
   - Improve hint generation

---

## Analytics & Insights

### Student-Level Metrics

- **Hint dependency:** % of questions where hints used
- **Hint level distribution:** Which levels most used
- **Hint effectiveness:** Success rate after using hints
- **Hint timing:** How long before requesting hints
- **Hint helpfulness:** Student-reported ratings

### Question-Level Metrics

- **Hint request rate:** % of students requesting hints
- **Average hint level:** Which level most helpful
- **Hint effectiveness:** Success rate by hint level
- **Hint gaps:** Questions needing better hints

### System-Level Metrics

- **Overall hint usage:** Trends over time
- **Hint quality:** Helpfulness ratings
- **Hint coverage:** Questions with/without hints
- **Hint impact:** Correlation with mastery

---

## Hint Generation Algorithm

### Automatic Generation Process

```python
def generate_hints(question):
    """Generate hints for a question automatically."""
    
    # 1. Identify question type
    question_type = identify_type(question)
    
    # 2. Extract parameters
    params = extract_parameters(question)
    
    # 3. Get hint template
    template = get_template(question_type)
    
    # 4. Generate each level
    hints = []
    for level in [1, 2, 3, 4]:
        hint_text = template[level].format(**params)
        hints.append({
            'level': level,
            'text': hint_text,
            'type': 'text' if level < 4 else 'example'
        })
    
    return hints
```

### Example Generation

```python
def generate_example_hint(question):
    """Generate a worked example similar to the question."""
    
    # 1. Create simpler version
    simple_question = simplify_question(question)
    
    # 2. Solve step-by-step
    steps = solve_with_steps(simple_question)
    
    # 3. Format as hint
    hint_text = f"Example: {simple_question.text}\n"
    hint_text += "\n".join(f"Step {i+1}: {step}" for i, step in enumerate(steps))
    hint_text += f"\nAnswer: {simple_question.answer}"
    
    return hint_text
```

---

## Learning Science Foundation

### Cognitive Load Theory

Hints reduce extraneous cognitive load by providing scaffolding, allowing students to focus on germane load (actual learning) rather than struggling with problem-solving strategies.

### Productive Struggle

Hints are designed to support productive struggle - enough challenge to promote learning, but not so much that students give up. Progressive hints allow students to choose their level of support.

### Metacognition

Strategic hints (Level 1) encourage metacognitive thinking by prompting students to think about their thinking and problem-solving approaches.

### Worked Example Effect

Level 4 hints provide worked examples, which research shows are highly effective for novice learners, reducing cognitive load while building schema.

### Scaffolding and Fading

The progressive hint system embodies scaffolding (providing support) and fading (gradually removing support as competence increases).

---

## Accessibility

### Features

1. **Screen Reader Support**
   - ARIA labels on hint buttons
   - Descriptive text for hint levels
   - Announced hint content

2. **Keyboard Navigation**
   - Tab to hint button
   - Enter to reveal hint
   - Arrow keys to navigate hint history

3. **Visual Design**
   - High contrast hint displays
   - Clear typography
   - Color-coded with text labels (not color alone)

4. **Cognitive Accessibility**
   - Simple, clear language
   - Progressive complexity
   - Visual and textual options

---

## Future Enhancements

### Phase 2

1. **AI-Generated Hints**
   - Use LLM to generate contextual hints
   - Personalized to student level
   - Adaptive based on performance

2. **Video Hints**
   - Short video explanations
   - Animated demonstrations
   - Teacher-recorded hints

3. **Peer Hints**
   - Student-generated hints
   - Community-voted best hints
   - Collaborative learning

4. **Adaptive Hints**
   - Adjust based on student history
   - Skip levels for advanced students
   - Provide more support for struggling students

5. **Interactive Hints**
   - Embedded mini-examples
   - Interactive visualizations
   - Guided practice

---

## Success Metrics

### Engagement

- % of students using hints
- Average hints per question
- Hint request timing
- Hint level distribution

### Effectiveness

- Success rate after using hints
- Hint helpfulness ratings
- Reduction in frustration
- Increase in persistence

### Learning Outcomes

- Correlation between hint use and mastery
- Long-term retention with vs without hints
- Transfer to similar problems
- Independence over time (decreasing hint use)

---

## Conclusion

The hint system will provide intelligent, progressive support that helps students when stuck without giving away answers. By following research-based principles of scaffolding, productive struggle, and metacognition, the system will promote independent problem-solving while reducing frustration.

---

**Next Steps:**
1. Implement database models
2. Create hint service layer
3. Build hint generator
4. Develop frontend components
5. Test and integrate

---

**Design Status:** ✅ Complete  
**Ready for Implementation:** Yes

