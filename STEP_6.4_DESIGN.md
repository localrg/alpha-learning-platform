# Step 6.4: Shared Challenges - Design Document

## Overview

Implement a shared challenges system that allows students to challenge friends and classmates to compete on specific math skills, creating engaging social competition and collaborative learning opportunities.

---

## Goals

1. **Social Competition** - Enable students to challenge friends on specific skills
2. **Class Challenges** - Allow teachers to create class-wide challenges
3. **Multiple Challenge Types** - Support competitive and collaborative modes
4. **Progress Tracking** - Real-time tracking of challenge participation and completion
5. **Rewards System** - Bonus XP and achievements for challenge winners

---

## Database Schema

### SharedChallenge Model

```python
class SharedChallenge(db.Model):
    __tablename__ = 'shared_challenges'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    
    # Challenge creator
    creator_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    
    # Challenge scope
    challenge_type = db.Column(db.String(20), nullable=False)  # 'friend', 'class'
    class_id = db.Column(db.Integer, db.ForeignKey('class_groups.id'))  # For class challenges
    
    # Challenge mode
    mode = db.Column(db.String(20), nullable=False)  # 'competitive', 'collaborative'
    
    # Challenge content
    skill_id = db.Column(db.Integer, nullable=False)
    target_questions = db.Column(db.Integer, nullable=False)  # Number of questions to answer
    target_accuracy = db.Column(db.Float, nullable=False)  # Required accuracy (e.g., 0.9 for 90%)
    
    # Timing
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)
    
    # Status
    status = db.Column(db.String(20), default='active')  # 'active', 'completed', 'expired'
    
    # Rewards
    xp_reward = db.Column(db.Integer, default=0)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    creator = db.relationship('Student', foreign_keys=[creator_id], backref='created_challenges')
    class_group = db.relationship('ClassGroup', backref='challenges')
```

### ChallengeParticipant Model

```python
class ChallengeParticipant(db.Model):
    __tablename__ = 'challenge_participants'
    
    id = db.Column(db.Integer, primary_key=True)
    challenge_id = db.Column(db.Integer, db.ForeignKey('shared_challenges.id'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    
    # Invitation status
    status = db.Column(db.String(20), default='invited')  # 'invited', 'accepted', 'declined'
    
    # Progress tracking
    questions_answered = db.Column(db.Integer, default=0)
    questions_correct = db.Column(db.Integer, default=0)
    accuracy = db.Column(db.Float, default=0.0)
    
    # Completion
    completed = db.Column(db.Boolean, default=False)
    completed_at = db.Column(db.DateTime)
    
    # Ranking (for competitive mode)
    rank = db.Column(db.Integer)
    
    # Timestamps
    joined_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    challenge = db.relationship('SharedChallenge', backref='participants')
    student = db.relationship('Student', backref='challenge_participations')
    
    # Unique constraint
    __table_args__ = (db.UniqueConstraint('challenge_id', 'student_id'),)
```

---

## Backend Implementation

### ChallengeService

**Core Methods:**

1. **`create_challenge(creator_id, data)`**
   - Create new challenge (friend or class)
   - Validate creator permissions (class challenges require teacher role)
   - Auto-invite participants based on type
   - Calculate XP reward based on difficulty

2. **`get_challenge(challenge_id, student_id)`**
   - Get challenge details
   - Include participant list and progress
   - Check if student is participant

3. **`get_student_challenges(student_id, filter_type=None)`**
   - Get all challenges for student
   - Filter by: 'active', 'completed', 'invited'
   - Sort by end_time (soonest first)

4. **`accept_challenge(challenge_id, student_id)`**
   - Accept challenge invitation
   - Update participant status to 'accepted'
   - Send notification to creator

5. **`decline_challenge(challenge_id, student_id)`**
   - Decline challenge invitation
   - Update participant status to 'declined'

6. **`update_progress(challenge_id, student_id, question_result)`**
   - Update participant progress after each question
   - Increment questions_answered and questions_correct
   - Recalculate accuracy
   - Check for completion
   - Award XP if completed

7. **`get_challenge_leaderboard(challenge_id)`**
   - Get ranked participant list
   - Sort by: completion (completed first), then accuracy, then speed
   - Assign ranks

8. **`complete_challenge(challenge_id)`**
   - Mark challenge as completed
   - Calculate final rankings
   - Award XP to winners/completers
   - Create achievement notifications

9. **`expire_challenges()`**
   - Background task to expire old challenges
   - Mark challenges past end_time as 'expired'

**Helper Methods:**

10. **`calculate_xp_reward(skill_id, target_questions, target_accuracy)`**
    - Calculate XP based on difficulty
    - Formula: base_xp * questions * accuracy_multiplier

11. **`invite_participants(challenge_id, participant_ids)`**
    - Add participants to challenge
    - Create ChallengeParticipant records
    - Send notifications

12. **`check_completion(challenge_id, student_id)`**
    - Check if student met challenge criteria
    - Mark as completed if criteria met
    - Award XP

---

## API Endpoints

### Challenge Management

**POST `/api/challenges`** - Create challenge
```json
Request:
{
  "title": "Multiplication Mastery",
  "description": "Who can master multiplication fastest?",
  "challenge_type": "friend",  // or "class"
  "mode": "competitive",  // or "collaborative"
  "skill_id": 5,
  "target_questions": 20,
  "target_accuracy": 0.9,
  "duration_hours": 24,
  "participant_ids": [2, 3, 4],  // For friend challenges
  "class_id": 1  // For class challenges
}

Response:
{
  "success": true,
  "challenge": {
    "id": 1,
    "title": "Multiplication Mastery",
    "creator": {...},
    "participants": [...],
    "end_time": "2024-12-20T10:00:00Z"
  }
}
```

**GET `/api/challenges`** - Get my challenges
```
Query params: ?status=active|completed|invited
Response: List of challenges
```

**GET `/api/challenges/<id>`** - Get challenge details
```json
Response:
{
  "id": 1,
  "title": "Multiplication Mastery",
  "description": "...",
  "creator": {...},
  "skill": {...},
  "target_questions": 20,
  "target_accuracy": 0.9,
  "start_time": "...",
  "end_time": "...",
  "status": "active",
  "xp_reward": 500,
  "participants": [
    {
      "student": {...},
      "status": "accepted",
      "questions_answered": 15,
      "questions_correct": 14,
      "accuracy": 0.93,
      "completed": false,
      "rank": 1
    }
  ],
  "my_participation": {...}
}
```

**DELETE `/api/challenges/<id>`** - Delete challenge (creator only)

### Challenge Participation

**POST `/api/challenges/<id>/accept`** - Accept challenge invitation

**POST `/api/challenges/<id>/decline`** - Decline challenge invitation

**POST `/api/challenges/<id>/progress`** - Update progress
```json
Request:
{
  "question_id": 123,
  "correct": true
}

Response:
{
  "success": true,
  "progress": {
    "questions_answered": 16,
    "questions_correct": 15,
    "accuracy": 0.9375,
    "completed": false
  },
  "challenge_completed": false
}
```

**GET `/api/challenges/<id>/leaderboard`** - Get challenge leaderboard
```json
Response:
{
  "challenge": {...},
  "leaderboard": [
    {
      "rank": 1,
      "student": {...},
      "questions_answered": 20,
      "accuracy": 0.95,
      "completed": true,
      "completed_at": "..."
    }
  ]
}
```

---

## Frontend Implementation

### ChallengesPage Component

**Layout:**
```
┌─────────────────────────────────────────┐
│  🎯 Challenges                          │
├─────────────────────────────────────────┤
│  [Active] [Invitations] [Completed]     │
├─────────────────────────────────────────┤
│  [+ Create Challenge]                   │
├─────────────────────────────────────────┤
│  ┌───────────────────────────────────┐  │
│  │ 🏆 Multiplication Mastery         │  │
│  │ Created by: Alex                  │  │
│  │ Skill: Multiplication (1-digit)   │  │
│  │ Goal: 20 questions @ 90% accuracy │  │
│  │ Ends: 2 hours remaining           │  │
│  │                                   │  │
│  │ Progress: 15/20 (93% accuracy) ✓  │  │
│  │ Rank: #1 of 4 participants        │  │
│  │                                   │  │
│  │ [Continue Challenge →]            │  │
│  └───────────────────────────────────┘  │
└─────────────────────────────────────────┘
```

**Features:**
- Three tabs: Active, Invitations, Completed
- Create challenge button (opens modal)
- Challenge cards with progress bars
- Real-time countdown timers
- Rank badges for competitive challenges
- Accept/Decline buttons for invitations

### CreateChallengeModal Component

**Form Fields:**
- Challenge title (text input)
- Description (textarea)
- Challenge type (friend/class selector)
- Mode (competitive/collaborative selector)
- Skill selector (dropdown of mastered skills)
- Target questions (number input, 5-50)
- Target accuracy (slider, 70-100%)
- Duration (dropdown: 1hr, 6hr, 24hr, 3days, 1week)
- Participants (friend/class selector based on type)

**Validation:**
- Title required (max 200 chars)
- At least 1 participant
- Valid skill selection
- Reasonable targets (5-50 questions, 70-100% accuracy)

### ChallengeDetailPage Component

**Sections:**
1. **Header** - Title, description, creator, time remaining
2. **Challenge Info** - Skill, targets, mode, rewards
3. **My Progress** - Questions answered, accuracy, completion status
4. **Leaderboard** - Ranked participant list with progress
5. **Actions** - Continue challenge, view results, share

**Real-time Updates:**
- Progress bars update after each question
- Leaderboard refreshes on progress updates
- Countdown timer updates every second
- Completion notifications

### ChallengeCard Component

**Compact Display:**
- Challenge title and creator
- Skill name and icon
- Progress bar (questions answered / target)
- Accuracy indicator
- Time remaining (countdown)
- Rank badge (competitive mode)
- Status badge (invited/active/completed)
- Quick action button

---

## Challenge Types

### Friend Challenge
- **Creator:** Any student
- **Participants:** Selected friends
- **Invitation:** Automatic to selected friends
- **Scope:** Small group (2-10 participants)
- **Use Case:** Friendly competition between peers

### Class Challenge
- **Creator:** Teacher only
- **Participants:** All class members
- **Invitation:** Automatic to all class members
- **Scope:** Entire class (10-30 participants)
- **Use Case:** Classroom-wide activities

---

## Challenge Modes

### Competitive Mode
- **Goal:** Individual performance
- **Ranking:** By accuracy, then speed
- **Rewards:** Top 3 get bonus XP
- **Display:** Leaderboard with ranks
- **Motivation:** Beat your friends!

### Collaborative Mode
- **Goal:** Group achievement
- **Ranking:** No individual ranks
- **Rewards:** All participants get XP if group goal met
- **Display:** Group progress bar
- **Motivation:** Work together!

---

## XP Reward Calculation

**Formula:**
```python
base_xp = 50
difficulty_multiplier = skill_difficulty  # 1.0 - 2.0
question_multiplier = target_questions / 10  # More questions = more XP
accuracy_multiplier = target_accuracy  # Higher accuracy = more XP

xp_reward = base_xp * difficulty_multiplier * question_multiplier * accuracy_multiplier

# Bonus for competitive winners
winner_bonus = xp_reward * 0.5  # 50% bonus for 1st place
second_bonus = xp_reward * 0.25  # 25% bonus for 2nd place
third_bonus = xp_reward * 0.1  # 10% bonus for 3rd place
```

**Example:**
- Skill: Multiplication (difficulty 1.5)
- Target: 20 questions @ 90% accuracy
- Base XP: 50 * 1.5 * 2.0 * 0.9 = 135 XP
- Winner gets: 135 + 67 = 202 XP

---

## Notifications

**Challenge Created:**
- "Alex challenged you to Multiplication Mastery! 🎯"
- Action: Accept or Decline

**Challenge Accepted:**
- "Sarah accepted your challenge!"

**Challenge Completed:**
- "You completed Multiplication Mastery! +135 XP 🎉"
- "You ranked #2 out of 5 participants!"

**Challenge Won:**
- "You won Multiplication Mastery! +202 XP 🏆"

**Challenge Ending Soon:**
- "Multiplication Mastery ends in 1 hour! ⏰"

---

## Integration Points

### With Friend System (6.2)
- Friend challenges use friend list
- Can only challenge accepted friends
- Friend activity shows challenge invitations

### With Class System (6.3)
- Class challenges use class membership
- Teachers create class-wide challenges
- Class leaderboard shows challenge participation

### With Gamification (5.1)
- Challenge completion awards XP
- XP contributes to level progression
- Challenge wins count toward achievements

### With Learning System (3.x)
- Challenges use existing question bank
- Progress updates skill mastery
- Challenge questions count toward daily practice

---

## User Flows

### Create Friend Challenge
1. Click "🎯 Challenges" → "+ Create Challenge"
2. Enter title and description
3. Select "Friend Challenge"
4. Choose competitive or collaborative mode
5. Select skill from dropdown
6. Set targets (questions, accuracy)
7. Choose duration
8. Select friends to invite
9. Click "Create Challenge"
10. Friends receive invitations

### Accept and Complete Challenge
1. Receive notification: "Alex challenged you!"
2. Click notification → View challenge details
3. Click "Accept Challenge"
4. Click "Start Challenge"
5. Answer questions (same UI as practice)
6. Progress updates in real-time
7. Complete target questions
8. View results and ranking
9. Receive XP reward

### Teacher Creates Class Challenge
1. Go to class page
2. Click "Create Challenge" button
3. Fill challenge form (same as friend challenge)
4. Select "Class Challenge"
5. All class members auto-invited
6. Monitor class progress on leaderboard

---

## Technical Implementation

### Backend Files

**New Files:**
1. `backend/src/models/shared_challenge.py` - Challenge models
2. `backend/src/services/challenge_service.py` - Challenge business logic
3. `backend/src/routes/challenge_routes.py` - Challenge API endpoints

**Modified Files:**
1. `backend/src/main.py` - Register challenge routes
2. `backend/src/models/__init__.py` - Export challenge models

### Frontend Files

**New Files:**
1. `frontend/src/components/ChallengesPage.jsx` - Main challenges page
2. `frontend/src/components/ChallengesPage.css` - Challenges styling
3. `frontend/src/components/CreateChallengeModal.jsx` - Challenge creation
4. `frontend/src/components/CreateChallengeModal.css` - Modal styling
5. `frontend/src/components/ChallengeCard.jsx` - Challenge card component
6. `frontend/src/components/ChallengeCard.css` - Card styling
7. `frontend/src/components/ChallengeDetailPage.jsx` - Challenge detail view
8. `frontend/src/components/ChallengeDetailPage.css` - Detail styling

**Modified Files:**
1. `frontend/src/App.jsx` - Add challenges route
2. `frontend/src/components/LearningSession.jsx` - Track challenge progress

### Testing

**Test File:** `backend/test_challenge_system.py`

**Test Cases:**
1. Create friend challenge
2. Create class challenge (teacher only)
3. Accept challenge invitation
4. Decline challenge invitation
5. Update challenge progress
6. Complete challenge (meet criteria)
7. Get challenge leaderboard
8. Award XP to winners
9. Expire old challenges
10. Delete challenge (creator only)

---

## Success Metrics

**Engagement:**
- 40% of students participate in challenges weekly
- Average 3 challenges per active student per week
- 80% acceptance rate for friend challenges

**Learning Impact:**
- Challenge participants practice 2x more questions
- 15% higher skill mastery rates
- Improved retention through social accountability

**Social Impact:**
- Increased friend interactions
- Higher class participation rates
- Stronger learning community

---

## Future Enhancements

1. **Team Challenges** - Multi-student teams competing
2. **Tournament Mode** - Bracket-style competitions
3. **Custom Question Sets** - Teachers create custom challenge questions
4. **Challenge Templates** - Pre-made challenges for common skills
5. **Challenge Replays** - Review challenge questions and answers
6. **Challenge Badges** - Special achievements for challenge wins
7. **Challenge Streaks** - Consecutive challenge completions
8. **Challenge Chat** - In-challenge messaging between participants

---

## Implementation Checklist

### Phase 1: Backend (Models + Service)
- [ ] Create SharedChallenge model
- [ ] Create ChallengeParticipant model
- [ ] Implement ChallengeService with 12 methods
- [ ] Add database migrations

### Phase 2: Backend (API)
- [ ] Create challenge_routes.py with 8 endpoints
- [ ] Register routes in main.py
- [ ] Add authentication/authorization checks
- [ ] Implement error handling

### Phase 3: Frontend (Components)
- [ ] Create ChallengesPage with tabs
- [ ] Create CreateChallengeModal with form
- [ ] Create ChallengeCard component
- [ ] Create ChallengeDetailPage
- [ ] Add challenges route to App.jsx

### Phase 4: Integration
- [ ] Integrate with LearningSession for progress tracking
- [ ] Connect with friend system for participant selection
- [ ] Connect with class system for class challenges
- [ ] Add XP rewards to gamification system

### Phase 5: Testing
- [ ] Write 10 comprehensive tests
- [ ] Test all API endpoints
- [ ] Test frontend components
- [ ] Integration testing

---

**Status:** Ready for implementation! 🚀

