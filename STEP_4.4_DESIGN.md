# Step 4.4: Worked Solutions - Design Document

**Date:** October 17, 2025  
**Week:** 4 - Content & Resources  
**Step:** 4.4 of 4.5

---

## Overview

The Worked Solutions system provides complete, step-by-step solutions to questions after students have attempted them. This enables students to learn from their mistakes by understanding the complete solution process, identifying where they went wrong, and building correct mental models.

---

## Learning Science Foundation

### 1. Worked Example Effect

Research shows that studying worked examples is highly effective for learning, especially for novice learners. Worked examples:
- Reduce cognitive load by showing complete solutions
- Help build problem-solving schemas
- Are more efficient than unguided problem-solving for beginners

### 2. Self-Explanation

When students study worked solutions and explain steps to themselves, they:
- Develop deeper understanding
- Identify gaps in knowledge
- Build connections between concepts

### 3. Learning from Errors

Reviewing worked solutions after mistakes helps students:
- Identify misconceptions
- Understand correct procedures
- Build accurate mental models
- Prevent error repetition

### 4. Cognitive Apprenticeship

Worked solutions model expert thinking by:
- Making invisible thinking visible
- Showing complete reasoning process
- Demonstrating problem-solving strategies

---

## System Architecture

### Data Model

```
WorkedSolution
├── id (Integer, PK)
├── question_id (Integer, FK)
├── solution_type (String) - 'step_by_step', 'visual', 'alternative'
├── steps (JSON) - Array of solution steps
├── difficulty_level (String) - 'beginner', 'intermediate', 'advanced'
├── show_after_attempts (Integer) - Minimum attempts before showing
├── is_active (Boolean)
├── created_at (DateTime)
└── updated_at (DateTime)

SolutionStep (JSON structure within steps)
├── step_number (Integer)
├── step_type (String) - 'calculation', 'explanation', 'visual', 'check'
├── content (String) - Step content
├── explanation (String) - Why this step
├── formula (String, optional) - Mathematical formula
├── image_url (String, optional) - Visual aid
└── highlight (Boolean) - Highlight important steps

SolutionView
├── id (Integer, PK)
├── student_id (Integer, FK)
├── question_id (Integer, FK)
├── solution_id (Integer, FK)
├── viewed_at (DateTime)
├── time_spent_seconds (Integer)
├── steps_viewed (JSON) - Array of step numbers viewed
├── helpful (Boolean, nullable) - Feedback
└── understood (Boolean, nullable) - Self-assessment
```

### Solution Generation Service

**SolutionService** will provide:
1. **Automatic Generation:** Create solutions based on question type
2. **Step Templates:** Pre-built templates for common operations
3. **Parameter Substitution:** Insert actual numbers from questions
4. **Multiple Representations:** Numerical, visual, verbal
5. **CRUD Operations:** Create, read, update solutions
6. **View Tracking:** Record when students view solutions
7. **Analytics:** Track solution effectiveness

---

## Solution Types

### 1. Step-by-Step Solutions

**Format:**
```
Step 1: [Action] - [Explanation]
Step 2: [Action] - [Explanation]
...
Final Answer: [Result]
```

**Example (Multiplication):**
```
Question: What is 12 × 5?

Step 1: Break down the multiplication
  12 × 5 means "12 added to itself 5 times"
  
Step 2: Set up repeated addition
  12 + 12 + 12 + 12 + 12
  
Step 3: Add the first two numbers
  12 + 12 = 24
  
Step 4: Continue adding
  24 + 12 = 36
  
Step 5: Continue adding
  36 + 12 = 48
  
Step 6: Add the final number
  48 + 12 = 60
  
Final Answer: 60
```

### 2. Visual Solutions

Include diagrams, arrays, number lines, or other visual representations.

**Example (Multiplication):**
```
Question: What is 3 × 4?

Visual: Array representation
[●●●●]
[●●●●]
[●●●●]

Explanation: 3 rows of 4 dots = 12 dots total
```

### 3. Alternative Methods

Show different approaches to the same problem.

**Example (Multiplication):**
```
Method 1: Repeated Addition
3 × 4 = 3 + 3 + 3 + 3 = 12

Method 2: Skip Counting
Count by 3s, four times: 3, 6, 9, 12

Method 3: Array Model
3 rows × 4 columns = 12 total
```

---

## Solution Templates by Question Type

### Multiplication

```json
{
  "type": "multiplication",
  "steps": [
    {
      "step_number": 1,
      "step_type": "explanation",
      "content": "Understand what {factor1} × {factor2} means",
      "explanation": "Multiplication means repeated addition"
    },
    {
      "step_number": 2,
      "step_type": "calculation",
      "content": "{factor1} × {factor2} = {factor1} added {factor2} times",
      "explanation": "Set up the repeated addition"
    },
    {
      "step_number": 3,
      "step_type": "calculation",
      "content": "{factor1} + {factor1} + ... (repeat {factor2} times)",
      "explanation": "Perform the addition"
    },
    {
      "step_number": 4,
      "step_type": "calculation",
      "content": "= {answer}",
      "explanation": "Final result"
    },
    {
      "step_number": 5,
      "step_type": "check",
      "content": "Check: {factor2} × {factor1} = {answer}",
      "explanation": "Verify using commutative property"
    }
  ]
}
```

### Addition (Multi-Digit)

```json
{
  "type": "addition",
  "steps": [
    {
      "step_number": 1,
      "step_type": "explanation",
      "content": "Line up the numbers by place value",
      "explanation": "Ones under ones, tens under tens"
    },
    {
      "step_number": 2,
      "step_type": "calculation",
      "content": "Add the ones place: {ones1} + {ones2} = {ones_sum}",
      "explanation": "Start with the rightmost column"
    },
    {
      "step_number": 3,
      "step_type": "calculation",
      "content": "Carry {carry} to the tens place (if needed)",
      "explanation": "When sum ≥ 10, carry the tens digit"
    },
    {
      "step_number": 4,
      "step_type": "calculation",
      "content": "Add the tens place: {tens1} + {tens2} + {carry} = {tens_sum}",
      "explanation": "Don't forget the carried number"
    },
    {
      "step_number": 5,
      "step_type": "calculation",
      "content": "Final answer: {answer}",
      "explanation": "Combine all place values"
    }
  ]
}
```

### Subtraction

```json
{
  "type": "subtraction",
  "steps": [
    {
      "step_number": 1,
      "step_type": "explanation",
      "content": "Line up the numbers by place value",
      "explanation": "Larger number on top"
    },
    {
      "step_number": 2,
      "step_type": "calculation",
      "content": "Subtract the ones place: {ones1} - {ones2} = {ones_diff}",
      "explanation": "Start with the rightmost column"
    },
    {
      "step_number": 3,
      "step_type": "calculation",
      "content": "Borrow from tens if needed",
      "explanation": "When top digit < bottom digit, borrow 10"
    },
    {
      "step_number": 4,
      "step_type": "calculation",
      "content": "Subtract the tens place: {tens1} - {tens2} = {tens_diff}",
      "explanation": "Remember to subtract 1 if you borrowed"
    },
    {
      "step_number": 5,
      "step_type": "calculation",
      "content": "Final answer: {answer}",
      "explanation": "Combine all place values"
    }
  ]
}
```

---

## Frontend Components

### 1. SolutionViewer Component

**Features:**
- Step-by-step display
- Progress indicator (Step X of Y)
- Next/Previous navigation
- Expand/collapse all steps
- Visual aids (images, diagrams)
- Formula rendering
- Highlight key steps

**Design:**
- Clean, readable typography
- Numbered steps
- Color-coded step types
- Smooth transitions
- Mobile-responsive

### 2. SolutionButton Component

**Features:**
- "View Solution" button
- Shows after minimum attempts
- Disabled until eligible
- Loading state
- Confirmation dialog (optional)

**Design:**
- Prominent but not distracting
- Clear eligibility messaging
- Icon indicator

### 3. SolutionFeedback Component

**Features:**
- "Was this helpful?" feedback
- "Did you understand?" self-assessment
- Optional comments
- Thank you message

**Design:**
- Simple thumbs up/down
- Checkbox for understanding
- Non-intrusive

---

## API Endpoints

### 1. Get Solution for Question

```
GET /api/solutions/question/<question_id>
Authorization: Bearer <token>

Response:
{
  "solution": {
    "id": 123,
    "question_id": 456,
    "solution_type": "step_by_step",
    "steps": [...],
    "difficulty_level": "beginner"
  },
  "eligible": true,
  "attempts_made": 2,
  "attempts_required": 1
}
```

### 2. Record Solution View

```
POST /api/solutions/view
Authorization: Bearer <token>
Content-Type: application/json

{
  "question_id": 456,
  "solution_id": 123,
  "time_spent_seconds": 45,
  "steps_viewed": [1, 2, 3, 4, 5]
}

Response:
{
  "view_id": 789,
  "message": "Solution view recorded"
}
```

### 3. Submit Solution Feedback

```
PUT /api/solutions/view/<view_id>/feedback
Authorization: Bearer <token>
Content-Type: application/json

{
  "helpful": true,
  "understood": true
}

Response:
{
  "message": "Feedback recorded"
}
```

### 4. Generate Solution for Question

```
POST /api/solutions/generate/<question_id>
Authorization: Bearer <token>

Response:
{
  "solution": {...},
  "message": "Solution generated successfully"
}
```

### 5. Get Student Solution Stats

```
GET /api/solutions/stats
Authorization: Bearer <token>

Response:
{
  "total_solutions_viewed": 15,
  "average_time_per_solution": 42,
  "helpful_rate": 0.87,
  "understanding_rate": 0.73,
  "solutions_by_type": {
    "multiplication": 8,
    "addition": 5,
    "subtraction": 2
  }
}
```

---

## User Flow

### Student Workflow

1. **Attempt Question**
   - Student tries to answer question
   - Submits answer (correct or incorrect)

2. **View Feedback**
   - Sees if answer was correct
   - Receives brief explanation

3. **Access Solution (if eligible)**
   - "View Complete Solution" button appears
   - Button enabled after minimum attempts (usually 1)
   - Click to open solution viewer

4. **Study Solution**
   - Read through steps sequentially
   - View visual aids
   - Navigate between steps
   - Spend time understanding

5. **Provide Feedback**
   - Mark if solution was helpful
   - Indicate if they understood
   - Submit feedback

6. **Continue Learning**
   - Return to practice
   - Apply learned approach to similar problems

---

## When to Show Solutions

### Timing Rules

1. **After Attempt:** Only show after student has attempted the question
2. **Minimum Attempts:** Require at least 1 attempt (configurable)
3. **Immediate Access:** For incorrect answers, show immediately
4. **Delayed for Correct:** For correct answers, show after completion (optional)

### Eligibility Logic

```python
def is_eligible_for_solution(student_id, question_id):
    attempts = get_student_attempts(student_id, question_id)
    solution = get_solution(question_id)
    
    if not solution:
        return False
    
    if len(attempts) < solution.show_after_attempts:
        return False
    
    return True
```

---

## Analytics & Insights

### Student Metrics

- Solutions viewed per session
- Time spent on solutions
- Helpful rate
- Understanding rate
- Improvement after viewing solutions

### Question Metrics

- % of students viewing solutions
- Average time spent on solution
- Helpful rate by question
- Correlation with subsequent performance

### Teacher Insights

- Which questions need better solutions
- Which solution types are most effective
- Student dependency on solutions
- Learning patterns

---

## Accessibility

### Features

1. **Keyboard Navigation**
   - Tab through steps
   - Arrow keys for next/previous
   - Enter to expand/collapse

2. **Screen Reader Support**
   - ARIA labels for steps
   - Descriptive button text
   - Announced progress

3. **Visual Design**
   - High contrast
   - Large, readable text
   - Clear step numbering
   - Color + text labels

4. **Responsive Design**
   - Mobile-optimized
   - Touch-friendly
   - Adaptive layouts

---

## Implementation Plan

### Phase 1: Backend (Current)

1. Create WorkedSolution and SolutionView models
2. Implement SolutionService with generation logic
3. Create API endpoints
4. Write solution templates
5. Test backend functionality

### Phase 2: Frontend

1. Create SolutionViewer component
2. Create SolutionButton component
3. Create SolutionFeedback component
4. Integrate with SkillPractice
5. Test UI/UX

### Phase 3: Testing & Refinement

1. Comprehensive testing
2. User feedback
3. Analytics review
4. Template refinement
5. Documentation

---

## Success Criteria

### Functional

✓ Solutions generated automatically for all question types  
✓ Step-by-step display with clear formatting  
✓ View tracking and analytics working  
✓ Feedback system functional  
✓ Eligibility logic correct  

### Quality

✓ Solutions are accurate and complete  
✓ Explanations are clear and age-appropriate  
✓ Visual design is professional  
✓ Performance is fast (< 1s load time)  
✓ Mobile experience is smooth  

### Learning Outcomes

✓ Students understand solutions  
✓ Performance improves after viewing  
✓ Students apply learned approaches  
✓ Dependency decreases over time  

---

## Future Enhancements

1. **Interactive Solutions:** Step-through with student input
2. **Video Solutions:** Recorded explanations
3. **Multiple Solutions:** Show different methods
4. **Personalized Solutions:** Adapt to student level
5. **AI-Generated Solutions:** Use LLM for custom solutions
6. **Peer Solutions:** Student-contributed approaches
7. **Solution Challenges:** "Can you solve it differently?"

---

## Conclusion

The Worked Solutions system will provide comprehensive step-by-step solutions that help students learn from mistakes, build correct mental models, and develop problem-solving skills. By combining automatic generation, clear presentation, and usage analytics, the system supports effective learning while providing valuable insights for teachers.

---

**Design Status:** ✅ Complete  
**Ready for Implementation:** Yes  
**Next Phase:** Backend Implementation

