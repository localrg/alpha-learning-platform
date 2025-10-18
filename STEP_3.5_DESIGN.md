# Step 3.5: Review System - Design Document

## Overview

Implement a spaced repetition review system to help students retain mastered skills over time and prevent knowledge decay.

## Key Concepts

### Spaced Repetition
- Review intervals increase over time
- First review: 1 day after mastery
- Second review: 3 days after first review
- Third review: 7 days after second review
- Fourth review: 14 days after third review
- Subsequent reviews: Every 30 days

### Review Criteria
- Only mastered skills are eligible for review
- Reviews consist of 3-5 questions per skill
- Must maintain 80%+ accuracy to keep "mastered" status
- If accuracy drops below 80%, skill returns to "needs_review" status

## Database Schema

### ReviewSession Model

```python
class ReviewSession(db.Model):
    __tablename__ = 'review_sessions'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    learning_path_id = db.Column(db.Integer, db.ForeignKey('learning_paths.id'), nullable=False)
    skill_id = db.Column(db.Integer, db.ForeignKey('skills.id'), nullable=False)
    
    # Session details
    questions_answered = db.Column(db.Integer, default=0)
    correct_answers = db.Column(db.Integer, default=0)
    accuracy = db.Column(db.Float, default=0.0)
    
    # Timing
    started_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)
    
    # Review tracking
    review_number = db.Column(db.Integer, default=1)  # 1st review, 2nd review, etc.
    passed = db.Column(db.Boolean, default=False)  # Did they maintain mastery?
    
    # Relationships
    student = db.relationship('Student', backref='review_sessions')
    learning_path = db.relationship('LearningPath', backref='review_sessions')
    skill = db.relationship('Skill', backref='review_sessions')
```

### LearningPath Model Updates

Add fields to track review schedule:

```python
# Review tracking
last_reviewed_at = db.Column(db.DateTime)
next_review_date = db.Column(db.DateTime)
review_count = db.Column(db.Integer, default=0)
review_interval_days = db.Column(db.Integer, default=1)  # Current interval
```

## Backend API Endpoints

### 1. GET /api/reviews/due
**Purpose:** Get all skills due for review

**Response:**
```json
{
  "reviews_due": [
    {
      "learning_path_id": 1,
      "skill_id": 5,
      "skill_name": "Basic Multiplication",
      "mastery_date": "2025-10-10T...",
      "last_reviewed_at": "2025-10-15T...",
      "next_review_date": "2025-10-17T...",
      "review_number": 2,
      "days_overdue": 0
    }
  ],
  "total_due": 1
}
```

### 2. POST /api/reviews/start
**Purpose:** Start a review session

**Request:**
```json
{
  "learning_path_id": 1
}
```

**Response:**
```json
{
  "review_session_id": 15,
  "skill": {...},
  "questions": [...],  // 3-5 questions
  "review_number": 2
}
```

### 3. PUT /api/reviews/:id/complete
**Purpose:** Complete a review session

**Request:**
```json
{
  "answers": [
    {"question_id": 1, "selected_answer": "a", "is_correct": true},
    {"question_id": 2, "selected_answer": "b", "is_correct": true},
    {"question_id": 3, "selected_answer": "c", "is_correct": false}
  ]
}
```

**Response:**
```json
{
  "review_session": {
    "accuracy": 66.7,
    "passed": false,
    "questions_answered": 3,
    "correct_answers": 2
  },
  "skill_status": "needs_review",  // or "mastered" if passed
  "next_review_date": "2025-10-20T...",
  "message": "Keep practicing! This skill needs more work."
}
```

## Frontend Components

### 1. ReviewDashboard Component
**Location:** `frontend/src/components/ReviewDashboard.jsx`

**Features:**
- Shows all skills due for review
- Displays review schedule
- Shows review history
- "Start Review" button for each skill

**UI:**
```
┌─────────────────────────────────────────┐
│ 📚 Skills Ready for Review              │
├─────────────────────────────────────────┤
│                                         │
│ ⭐ Basic Multiplication                 │
│    Last reviewed: 3 days ago            │
│    Review #2                            │
│    [Start Review]                       │
│                                         │
│ ⭐ Fraction Basics                      │
│    Last reviewed: 7 days ago            │
│    Review #3                            │
│    [Start Review]                       │
│                                         │
├─────────────────────────────────────────┤
│ 📅 Upcoming Reviews                     │
│                                         │
│ • Division Basics - in 2 days           │
│ • Place Value - in 5 days               │
│                                         │
└─────────────────────────────────────────┘
```

### 2. ReviewSession Component
**Location:** `frontend/src/components/ReviewSession.jsx`

**Features:**
- Similar to SkillPractice but focused on review
- Shows 3-5 questions
- Immediate feedback
- Review completion screen

**UI:**
```
┌─────────────────────────────────────────┐
│ 🔄 Review: Basic Multiplication         │
│ Review #2 • Question 2 of 3             │
├─────────────────────────────────────────┤
│                                         │
│ What is 8 × 7?                          │
│                                         │
│ ○ 54                                    │
│ ○ 56                                    │
│ ○ 63                                    │
│ ○ 64                                    │
│                                         │
│ [Submit Answer]                         │
│                                         │
└─────────────────────────────────────────┘
```

### 3. ReviewResults Component
**Location:** `frontend/src/components/ReviewResults.jsx`

**Features:**
- Shows review accuracy
- Pass/fail status
- Next review date
- Encouragement message

**UI (Passed):**
```
┌─────────────────────────────────────────┐
│ ✅ Review Passed!                       │
├─────────────────────────────────────────┤
│                                         │
│ You maintained mastery of               │
│ Basic Multiplication                    │
│                                         │
│ Accuracy: 100% (3/3 correct)            │
│                                         │
│ Next review: October 24, 2025           │
│ (in 7 days)                             │
│                                         │
│ Great job maintaining your skills!      │
│                                         │
│ [Back to Dashboard]                     │
│                                         │
└─────────────────────────────────────────┘
```

**UI (Failed):**
```
┌─────────────────────────────────────────┐
│ 📝 Needs More Practice                  │
├─────────────────────────────────────────┤
│                                         │
│ Basic Multiplication                    │
│                                         │
│ Accuracy: 67% (2/3 correct)             │
│                                         │
│ This skill needs more practice to       │
│ maintain mastery.                       │
│                                         │
│ Status: Needs Review                    │
│                                         │
│ [Practice This Skill]                   │
│ [Back to Dashboard]                     │
│                                         │
└─────────────────────────────────────────┘
```

## Review Scheduling Algorithm

```python
def calculate_next_review_date(review_count):
    """Calculate next review date based on spaced repetition"""
    intervals = {
        0: 1,    # First review: 1 day after mastery
        1: 3,    # Second review: 3 days after first
        2: 7,    # Third review: 7 days after second
        3: 14,   # Fourth review: 14 days after third
        4: 30,   # Fifth+ review: 30 days
    }
    
    days = intervals.get(review_count, 30)
    return datetime.utcnow() + timedelta(days=days)

def schedule_review(learning_path_item):
    """Schedule next review for a mastered skill"""
    learning_path_item.review_count += 1
    learning_path_item.last_reviewed_at = datetime.utcnow()
    learning_path_item.next_review_date = calculate_next_review_date(
        learning_path_item.review_count
    )
    learning_path_item.review_interval_days = (
        learning_path_item.next_review_date - datetime.utcnow()
    ).days
```

## Integration with Dashboard

Add a "Reviews" section to the main dashboard:

```javascript
// In Dashboard.jsx
<div className="dashboard-section">
  <h2>📚 Reviews</h2>
  {reviewsDue > 0 ? (
    <div className="reviews-alert">
      <p>You have {reviewsDue} skill{reviewsDue > 1 ? 's' : ''} ready for review!</p>
      <button onClick={() => navigate('/reviews')}>
        Start Reviews
      </button>
    </div>
  ) : (
    <p className="no-reviews">No reviews due today. Great job!</p>
  )}
</div>
```

## User Flow

```
1. Student masters a skill
   ↓
2. System schedules first review (1 day later)
   ↓
3. Next day, review appears on dashboard
   ↓
4. Student clicks "Start Review"
   ↓
5. System presents 3-5 questions
   ↓
6. Student answers questions
   ↓
7. System calculates accuracy
   ↓
8. If ≥80%: Maintain mastery, schedule next review
   If <80%: Mark as "needs_review", add to learning path
   ↓
9. Show results and next review date
```

## Acceptance Criteria

- [ ] ReviewSession model created
- [ ] LearningPath model updated with review fields
- [ ] Backend API endpoints implemented
- [ ] Review scheduling algorithm working
- [ ] ReviewDashboard component displays due reviews
- [ ] ReviewSession component allows practice
- [ ] ReviewResults component shows outcome
- [ ] Integration with main dashboard
- [ ] Spaced repetition intervals correct
- [ ] Skills marked correctly (mastered vs needs_review)
- [ ] Next review dates calculated accurately
- [ ] Database migrations run successfully
- [ ] All tests pass

## Testing Plan

### Backend Tests
1. Create review session
2. Complete review with 80%+ (pass)
3. Complete review with <80% (fail)
4. Calculate next review dates
5. Get reviews due
6. Schedule reviews correctly

### Frontend Tests
1. Display reviews due
2. Start review session
3. Answer review questions
4. Show pass/fail results
5. Navigate back to dashboard
6. Update review status

### Integration Tests
1. Master skill → Schedule review
2. Complete review → Update status
3. Failed review → Return to learning path
4. Passed review → Schedule next review
5. Dashboard shows correct review count


