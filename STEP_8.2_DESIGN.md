# Step 8.2: Child Progress View - Design Document

## Overview

The Child Progress View enables parents to view comprehensive progress information for their linked children, including performance metrics, skill mastery, recent activity, assignments, and achievements. This provides parents with visibility into their child's learning journey and helps them support their child's education at home.

---

## Goals

1. **Provide comprehensive progress overview** - Parents see overall performance at a glance
2. **Show skill-level details** - Parents understand which skills child has mastered
3. **Display recent activity** - Parents see what child has been practicing
4. **Track assignments** - Parents monitor assignment completion and due dates
5. **Highlight achievements** - Parents celebrate child's accomplishments
6. **Enable comparison** - Parents see how child compares to class average (optional)

---

## Core Features

### Progress Dashboard

**Overview Cards:**
- Overall accuracy (last 30 days)
- Questions answered (last 30 days)
- Time spent learning (last 30 days)
- Current level and XP
- Skills mastered / total skills
- Current streak
- Assignments completed / total

**Quick Stats:**
- Last practice session (date and time)
- Most practiced skill (last 7 days)
- Biggest improvement (skill with highest accuracy gain)
- Next assignment due (if any)

### Skill Progress View

**Skill List:**
- Skill name
- Current accuracy
- Mastery status (not started, in progress, mastered)
- Questions answered
- Progress bar
- Last practiced date

**Skill Details (Click to Expand):**
- Accuracy trend (last 30 days)
- Questions correct / total
- Time spent on skill
- Mastery date (if mastered)
- Recommended next steps

**Filters:**
- All skills
- In progress
- Mastered
- Needs practice (accuracy < 70%)

### Recent Activity Feed

**Activity Types:**
- Practice sessions (skill, questions, accuracy, time)
- Assignments completed (title, score, completion date)
- Skills mastered (skill name, mastery date)
- Achievements earned (achievement name, date)
- Level ups (new level, date)
- Streaks achieved (streak length, date)

**Activity Details:**
- Date and time
- Duration (for practice sessions)
- Performance metrics
- XP earned

**Filters:**
- Last 7 days
- Last 30 days
- All time

### Assignment Tracking

**Assignment List:**
- Assignment title
- Due date
- Status (not started, in progress, completed, overdue)
- Score (if completed)
- Questions answered / total
- Time spent

**Assignment Details:**
- Skills covered
- Question count and difficulty
- Start date
- Completion date (if completed)
- Accuracy and score
- Teacher name

**Filters:**
- Active (not started + in progress)
- Completed
- Overdue

### Achievement Showcase

**Achievement Display:**
- Achievement icon and name
- Description
- Earned date
- Rarity (common, rare, epic, legendary)
- Progress toward next achievement

**Categories:**
- Skill mastery
- Practice consistency
- Performance excellence
- Social engagement

### Performance Trends

**Trend Charts:**
- Accuracy over time (line chart)
- Questions answered per day (bar chart)
- Time spent per day (bar chart)
- Skills mastered over time (cumulative line chart)

**Time Ranges:**
- Last 7 days
- Last 30 days
- Last 90 days
- All time

---

## Backend Implementation

### ParentViewService Methods

1. **`get_child_overview(parent_id, student_id)`**
   - Verify parent-child link
   - Get overall metrics (accuracy, questions, time, level, XP)
   - Get skill summary (mastered, in progress, total)
   - Get streak information
   - Get assignment summary
   - Return overview dict

2. **`get_child_skills(parent_id, student_id, filter='all')`**
   - Verify parent-child link
   - Get all learning paths for student
   - Filter by status if specified
   - Sort by mastery status and accuracy
   - Return skill list

3. **`get_child_activity(parent_id, student_id, days=30)`**
   - Verify parent-child link
   - Get practice sessions
   - Get assignment completions
   - Get achievements earned
   - Get level ups
   - Get skills mastered
   - Combine and sort by date
   - Return activity feed

4. **`get_child_assignments(parent_id, student_id, filter='all')`**
   - Verify parent-child link
   - Get assignments for student
   - Filter by status if specified
   - Sort by due date
   - Return assignment list

5. **`get_child_achievements(parent_id, student_id)`**
   - Verify parent-child link
   - Get earned achievements
   - Get progress toward next achievements
   - Return achievement list

6. **`get_child_trends(parent_id, student_id, metric, days=30)`**
   - Verify parent-child link
   - Get trend data for specified metric
   - Aggregate by day
   - Return time-series data

7. **`verify_parent_child_link(parent_id, student_id)`**
   - Check if active link exists
   - Return boolean

---

## API Endpoints

### Progress Overview
- `GET /api/parents/children/<id>/overview` - Get child overview dashboard
- `GET /api/parents/children/<id>/skills` - Get child skill progress
- `GET /api/parents/children/<id>/activity` - Get child activity feed
- `GET /api/parents/children/<id>/assignments` - Get child assignments
- `GET /api/parents/children/<id>/achievements` - Get child achievements
- `GET /api/parents/children/<id>/trends` - Get child performance trends

---

## User Flows

### Parent Views Child Progress

1. Parent logs in
2. Sees dashboard with all linked children
3. Clicks on "Student One"
4. Child progress page loads showing:
   - **Overview Section:**
     - Overall accuracy: 85%
     - Questions answered: 450 (last 30 days)
     - Time spent: 12 hours
     - Level 8 (1,250 XP)
     - Skills: 15 mastered / 20 total
     - Current streak: 7 days
     - Assignments: 8 completed / 10 total
   - **Quick Stats:**
     - Last practice: Today at 3:45 PM
     - Most practiced: Multiplication (45 questions)
     - Biggest improvement: Fractions (+15% accuracy)
     - Next due: Division Practice (Tomorrow)
5. Parent scrolls to see more details

### Parent Explores Skill Progress

1. Parent clicks "View All Skills" tab
2. Sees skill list:
   - **Mastered (15):**
     - Addition (95% accuracy, 120 questions)
     - Subtraction (92% accuracy, 100 questions)
     - ...
   - **In Progress (3):**
     - Multiplication (85% accuracy, 80 questions)
     - Division (78% accuracy, 60 questions)
     - Fractions (65% accuracy, 40 questions)
   - **Not Started (2):**
     - Decimals
     - Percentages
3. Parent clicks on "Fractions" to see details:
   - Accuracy trend chart (showing improvement from 50% to 65%)
   - Questions: 26 correct / 40 total
   - Time spent: 2.5 hours
   - Last practiced: Yesterday
   - Status: Needs more practice
4. Parent understands child needs help with fractions

### Parent Checks Recent Activity

1. Parent clicks "Activity" tab
2. Sees recent activity feed:
   - **Today, 3:45 PM** - Practice Session
     - Skill: Multiplication
     - Questions: 15 (13 correct)
     - Accuracy: 87%
     - Time: 12 minutes
     - XP earned: 65
   - **Today, 2:30 PM** - Assignment Completed
     - Title: "Division Practice"
     - Score: 18/20 (90%)
     - Time: 18 minutes
     - XP earned: 120 (with bonus)
   - **Yesterday** - Skill Mastered
     - Skill: Subtraction
     - Accuracy: 92%
     - XP earned: 100
   - **2 days ago** - Achievement Earned
     - Achievement: "Week Warrior"
     - Description: Practice 7 days in a row
     - XP earned: 50
3. Parent sees child is actively practicing and making progress

### Parent Monitors Assignments

1. Parent clicks "Assignments" tab
2. Sees assignment list:
   - **Active (2):**
     - "Fractions Review" - Due tomorrow (Not started)
     - "Mixed Operations" - Due in 3 days (In progress: 5/15 questions)
   - **Completed (8):**
     - "Division Practice" - 90% (Completed today)
     - "Multiplication Quiz" - 85% (Completed 2 days ago)
     - ...
   - **Overdue (0):**
3. Parent clicks on "Fractions Review":
   - Due: Tomorrow at 11:59 PM
   - Skills: Fractions (adding, subtracting)
   - Questions: 20
   - Difficulty: Medium
   - Assigned by: Ms. Johnson
   - Status: Not started
4. Parent reminds child to complete assignment

### Parent Celebrates Achievements

1. Parent clicks "Achievements" tab
2. Sees achievement showcase:
   - **Recently Earned:**
     - Week Warrior (7-day streak)
     - Quick Learner (10 questions in 5 minutes)
     - Accuracy Ace (95%+ on 3 skills)
   - **In Progress:**
     - Master Mathematician (15/20 skills mastered)
     - Dedicated Student (45/50 practice sessions)
     - Speed Demon (80/100 questions under 30 seconds)
3. Parent praises child for achievements
4. Parent encourages child to reach next milestones

---

## Business Logic

### Get Child Overview

```python
def get_child_overview(parent_id, student_id):
    # Verify link
    if not verify_parent_child_link(parent_id, student_id):
        return {'error': 'Unauthorized'}, 403
    
    # Get student
    student = Student.query.get(student_id)
    
    # Get sessions (last 30 days)
    cutoff = datetime.utcnow() - timedelta(days=30)
    sessions = StudentSession.query.filter(
        StudentSession.student_id == student_id,
        StudentSession.started_at >= cutoff
    ).all()
    
    # Calculate metrics
    total_questions = sum(s.questions_answered for s in sessions)
    total_correct = sum(s.questions_correct for s in sessions)
    accuracy = total_correct / total_questions if total_questions > 0 else 0
    
    total_time = sum(
        (s.ended_at - s.started_at).total_seconds() / 3600
        for s in sessions if s.ended_at
    )
    
    # Get skill summary
    paths = LearningPath.query.filter_by(student_id=student_id).all()
    skills_mastered = sum(1 for p in paths if p.mastery_achieved)
    total_skills = len(paths)
    
    # Get streak
    streak = StreakTracking.query.filter_by(student_id=student_id).first()
    current_streak = streak.current_streak if streak else 0
    
    # Get assignments
    assignments = AssignmentStudent.query.filter_by(student_id=student_id).all()
    completed_assignments = sum(1 for a in assignments if a.status == 'completed')
    total_assignments = len(assignments)
    
    # Get gamification
    progress = StudentProgress.query.filter_by(student_id=student_id).first()
    
    return {
        'student': student.to_dict(),
        'metrics': {
            'accuracy': accuracy,
            'questions_answered': total_questions,
            'time_spent_hours': round(total_time, 1),
            'level': progress.current_level if progress else 1,
            'xp': progress.total_xp if progress else 0,
            'skills_mastered': skills_mastered,
            'total_skills': total_skills,
            'current_streak': current_streak,
            'assignments_completed': completed_assignments,
            'total_assignments': total_assignments
        },
        'last_activity': sessions[-1].started_at if sessions else None
    }
```

### Get Child Activity Feed

```python
def get_child_activity(parent_id, student_id, days=30):
    # Verify link
    if not verify_parent_child_link(parent_id, student_id):
        return {'error': 'Unauthorized'}, 403
    
    cutoff = datetime.utcnow() - timedelta(days=days)
    activities = []
    
    # Practice sessions
    sessions = StudentSession.query.filter(
        StudentSession.student_id == student_id,
        StudentSession.started_at >= cutoff
    ).all()
    
    for session in sessions:
        activities.append({
            'type': 'practice_session',
            'date': session.started_at,
            'skill_name': session.skill.name if session.skill else 'Unknown',
            'questions': session.questions_answered,
            'correct': session.questions_correct,
            'accuracy': session.accuracy,
            'duration_minutes': (
                (session.ended_at - session.started_at).total_seconds() / 60
                if session.ended_at else 0
            )
        })
    
    # Assignment completions
    assignments = AssignmentStudent.query.filter(
        AssignmentStudent.student_id == student_id,
        AssignmentStudent.completed_at >= cutoff,
        AssignmentStudent.status == 'completed'
    ).all()
    
    for assignment in assignments:
        activities.append({
            'type': 'assignment_completed',
            'date': assignment.completed_at,
            'title': assignment.assignment.title,
            'score': assignment.score,
            'accuracy': assignment.accuracy
        })
    
    # Skills mastered
    paths = LearningPath.query.filter(
        LearningPath.student_id == student_id,
        LearningPath.mastery_achieved == True,
        LearningPath.mastered_at >= cutoff
    ).all()
    
    for path in paths:
        activities.append({
            'type': 'skill_mastered',
            'date': path.mastered_at,
            'skill_name': path.skill.name,
            'accuracy': path.current_accuracy
        })
    
    # Sort by date (most recent first)
    activities.sort(key=lambda x: x['date'], reverse=True)
    
    return {'activities': activities}
```

---

## Expected Impact

**Parent Benefits:**
- Complete visibility into child's learning progress
- Understand which skills child has mastered
- Identify areas where child needs help
- Monitor assignment completion
- Celebrate achievements with child
- Support learning at home

**Student Benefits:**
- Parental support and encouragement
- Accountability through parent visibility
- Recognition for achievements
- Help with difficult skills
- Motivation from parent involvement

**Platform Metrics:**
- 40% of parents check progress weekly
- 60% of parents with progress view are more engaged
- 25% increase in student engagement when parents are active
- 30% faster skill mastery with parent support
- 20% higher assignment completion with parent monitoring

---

## Success Metrics

- **View Rate:** 40% of parents view child progress weekly
- **Engagement Impact:** 25% increase in student practice when parents view progress
- **Assignment Completion:** 20% higher completion rate when parents monitor
- **Parent Satisfaction:** 85% of parents find progress view helpful
- **Retention:** 30% higher student retention with active parent involvement

---

This implementation provides parents with comprehensive visibility into their child's learning journey, enabling them to support, encourage, and celebrate their child's progress!

