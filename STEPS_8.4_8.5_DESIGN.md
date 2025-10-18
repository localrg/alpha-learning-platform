# Steps 8.4 & 8.5: Communication Tools & Goal Setting - Design Document

## Overview

Steps 8.4 and 8.5 implement the final features of the Parent Portal: communication tools for parent-teacher messaging and goal-setting capabilities for collaborative learning objectives. These features complete the parent engagement ecosystem.

## Goals

1. Enable direct parent-teacher communication
2. Support goal-setting between parents and students
3. Track goal progress and completion
4. Facilitate collaborative learning planning
5. Maintain communication history and context

## Step 8.4: Communication Tools

### Features

#### 1. Parent-Teacher Messaging
**Purpose:** Direct communication channel between parents and teachers

**Capabilities:**
- Send message to child's teacher
- View message history
- Reply to teacher messages
- Mark messages as read/unread
- Message threading (conversations)

**Message Types:**
- General question
- Progress inquiry
- Concern/issue
- Meeting request
- Thank you/appreciation

#### 2. Message Management
**Features:**
- Inbox view (all messages)
- Sent messages view
- Unread count badge
- Search and filter
- Archive messages

### Technical Design

#### Database Models

**ParentTeacherMessage Model:**
```python
class ParentTeacherMessage(db.Model):
    id: int (PK)
    parent_id: int (FK -> parents.id)
    teacher_id: int (FK -> users.id)
    student_id: int (FK -> students.id)  # Context
    subject: str
    message: text
    message_type: str  # question, inquiry, concern, meeting, appreciation
    parent_read: bool
    teacher_read: bool
    replied_to_id: int (FK -> parent_teacher_messages.id, nullable)
    created_at: datetime
    updated_at: datetime
```

#### API Endpoints

**Parent Endpoints:**
- `POST /api/parent/messages` - Send message to teacher
- `GET /api/parent/messages` - Get all messages (inbox + sent)
- `GET /api/parent/messages/<id>` - Get specific message
- `PUT /api/parent/messages/<id>/read` - Mark as read
- `GET /api/parent/messages/unread-count` - Get unread count

**Teacher Endpoints** (reuse existing teacher message system):
- Teachers receive parent messages in their existing inbox
- Can reply using existing intervention/messaging tools

## Step 8.5: Goal Setting

### Features

#### 1. Goal Creation
**Who Can Create:**
- Parents (for their children)
- Students (for themselves)
- Teachers (for students, via assignments)

**Goal Types:**
- Skill mastery (master specific skill)
- Practice time (X minutes per week)
- Accuracy target (achieve X% accuracy)
- Assignment completion (complete X assignments)
- Streak maintenance (maintain X-day streak)
- Custom (free-form goal)

#### 2. Goal Tracking
**Automatic Progress:**
- System tracks progress based on goal type
- Updates progress percentage
- Marks as complete when achieved
- Sends notifications on milestones

**Manual Updates:**
- Parents can add notes/encouragement
- Students can update custom goals
- Teachers can provide feedback

#### 3. Goal Management
**Features:**
- View active goals
- View completed goals
- Edit goal (before completion)
- Delete goal
- Goal history

### Technical Design

#### Database Models

**Goal Model:**
```python
class Goal(db.Model):
    id: int (PK)
    student_id: int (FK -> students.id)
    created_by_id: int (FK -> users.id)  # Parent, student, or teacher
    created_by_type: str  # parent, student, teacher
    goal_type: str  # skill_mastery, practice_time, accuracy, assignments, streak, custom
    title: str
    description: text
    target_value: float  # Depends on goal_type
    current_value: float
    progress_percent: float
    status: str  # active, completed, abandoned
    due_date: datetime (nullable)
    completed_at: datetime (nullable)
    created_at: datetime
    updated_at: datetime
```

**GoalNote Model:**
```python
class GoalNote(db.Model):
    id: int (PK)
    goal_id: int (FK -> goals.id)
    user_id: int (FK -> users.id)
    user_type: str  # parent, student, teacher
    note: text
    created_at: datetime
```

**GoalProgress Model:**
```python
class GoalProgress(db.Model):
    id: int (PK)
    goal_id: int (FK -> goals.id)
    value: float
    progress_percent: float
    note: text (nullable)
    recorded_at: datetime
```

#### API Endpoints

**Goal Management:**
- `POST /api/goals` - Create goal
- `GET /api/goals/student/<id>` - Get student's goals
- `GET /api/goals/<id>` - Get specific goal
- `PUT /api/goals/<id>` - Update goal
- `DELETE /api/goals/<id>` - Delete goal
- `POST /api/goals/<id>/complete` - Mark as complete

**Goal Progress:**
- `GET /api/goals/<id>/progress` - Get progress history
- `POST /api/goals/<id>/progress` - Add progress update (manual)
- `POST /api/goals/<id>/notes` - Add note/encouragement
- `GET /api/goals/<id>/notes` - Get all notes

**Goal Tracking (Background):**
- Automatic progress updates based on student activity
- Triggered by learning sessions, assignments, etc.

### Goal Type Specifications

#### 1. Skill Mastery Goal
**Target:** Master specific skill (achieve 90%+ accuracy)
**Tracking:** Automatic via LearningPath.mastery_achieved
**Progress:** Current accuracy / 90%

#### 2. Practice Time Goal
**Target:** Practice X minutes per week/month
**Tracking:** Automatic via StudentSession time
**Progress:** Current time / Target time

#### 3. Accuracy Target Goal
**Target:** Achieve X% overall accuracy
**Tracking:** Automatic via StudentProgress
**Progress:** Current accuracy / Target accuracy

#### 4. Assignment Completion Goal
**Target:** Complete X assignments
**Tracking:** Automatic via AssignmentStudent.status
**Progress:** Completed count / Target count

#### 5. Streak Maintenance Goal
**Target:** Maintain X-day practice streak
**Tracking:** Automatic via StreakTracking
**Progress:** Current streak / Target streak

#### 6. Custom Goal
**Target:** Free-form (parent/student defined)
**Tracking:** Manual updates only
**Progress:** User-reported percentage

## Implementation Plan

### Phase 1: Communication Tools
1. Create ParentTeacherMessage model
2. Create CommunicationService with messaging logic
3. Create API routes for parent messaging
4. Integrate with existing teacher message system
5. Test messaging functionality

### Phase 2: Goal Setting
1. Create Goal, GoalNote, GoalProgress models
2. Create GoalService with CRUD and tracking logic
3. Create API routes for goal management
4. Implement automatic progress tracking
5. Test goal creation and tracking

### Phase 3: Integration
1. Connect goals to reports (show in parent view)
2. Connect messages to student context
3. Add notifications for goal milestones
4. Test end-to-end workflows

## Success Metrics

### Communication Tools
- 40% of parents send at least one message per semester
- 90% of teacher messages receive parent reply
- 85% of parents find messaging useful (survey)
- Average response time < 24 hours

### Goal Setting
- 60% of parents set at least one goal for child
- 50% of students set their own goals
- 70% goal completion rate
- 80% of parents find goals motivating (survey)

## Testing Strategy

### Communication Tests
- Send message from parent to teacher
- Reply to message (threading)
- Mark as read/unread
- Unread count accuracy
- Authorization (parent can only message child's teachers)
- Message history retrieval

### Goal Tests
- Create goals of each type
- Automatic progress tracking
- Manual progress updates
- Goal completion detection
- Add notes/encouragement
- Goal editing and deletion
- Authorization (parent can only create goals for their children)

## Notes

- Communication tools leverage existing teacher message infrastructure
- Goal tracking is automatic for most goal types
- Parents can see goals in child progress view
- Teachers can see parent-created goals in student monitoring
- Goals integrate with existing gamification (XP rewards for completion)

---

**Next Step:** Implement models, services, and API routes for both features, then create comprehensive tests.

