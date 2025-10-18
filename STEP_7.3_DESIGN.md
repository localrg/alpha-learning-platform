# Step 7.3: Student Monitoring - Design Document

## Overview

Provide teachers with real-time monitoring tools to track student activity, identify struggling students, and intervene when needed. This system enables proactive teaching by alerting teachers to students who need help before they fall too far behind.

---

## Goals

1. **Real-time activity monitoring** - See what students are working on now
2. **Identify struggling students** - Automatic detection based on performance
3. **Track inactive students** - Alert when students haven't practiced recently
4. **Provide intervention tools** - Quick actions to help students
5. **Monitor assignment completion** - Track who's completing assignments on time

---

## Core Features

### Real-Time Activity Dashboard

Teachers can see:
- **Active Students** - Students currently practicing (last 5 minutes)
- **What They're Working On** - Current skill, question number, accuracy
- **Session Duration** - How long they've been practicing
- **Recent Activity** - Last 24 hours of student activity

### Student Status Categories

**On Track:**
- Accuracy ≥ 80%
- Active in last 3 days
- Assignments completed on time
- Status: Green indicator

**Needs Practice:**
- Accuracy 70-79%
- Active in last 7 days
- Some assignments incomplete
- Status: Yellow indicator

**Needs Help:**
- Accuracy < 70%
- Inactive > 7 days
- Multiple assignments overdue
- Status: Red indicator

**Inactive:**
- No activity in 14+ days
- Status: Gray indicator

### Monitoring Metrics

**Per Student:**
- Last active timestamp
- Current session duration
- Questions answered today/week
- Current accuracy
- Struggling skills (< 70%)
- Assignment completion rate
- Streak status

**Per Class:**
- Active students count
- Average session duration
- Questions answered (total)
- Average accuracy
- Struggling students count
- Assignment completion rate

### Alert System

**High Priority Alerts:**
- Student inactive for 7+ days
- Student accuracy dropped below 60%
- Student has 3+ overdue assignments
- Student struggling on 5+ skills

**Medium Priority Alerts:**
- Student inactive for 3-7 days
- Student accuracy 60-70%
- Student has 1-2 overdue assignments
- Student struggling on 2-4 skills

**Low Priority Alerts:**
- Student hasn't started new assignment
- Student's streak about to break
- Student hasn't practiced today

### Intervention Tools

**Quick Actions:**
- Send message to student
- Create targeted assignment
- Schedule one-on-one meeting
- Notify parent (future)
- Assign peer tutor (future)

---

## Backend Implementation

### MonitoringService Methods

1. **`get_active_students(class_id)`**
   - Get students active in last 5 minutes
   - Include current skill, accuracy, session duration
   - Return list of active students

2. **`get_student_status(student_id)`**
   - Calculate student status (on_track, needs_practice, needs_help, inactive)
   - Based on accuracy, activity, assignments
   - Return status and metrics

3. **`get_class_monitoring_data(class_id, teacher_id)`**
   - Get comprehensive monitoring data for class
   - Include all students with status
   - Include active students
   - Include alerts
   - Return monitoring dashboard data

4. **`get_struggling_students(class_id, threshold=0.7)`**
   - Get students with accuracy below threshold
   - Include struggling skills
   - Include recent activity
   - Return list of struggling students

5. **`get_inactive_students(class_id, days=7)`**
   - Get students inactive for X days
   - Include last active timestamp
   - Include contact info
   - Return list of inactive students

6. **`get_student_activity_timeline(student_id, days=7)`**
   - Get student's activity for last X days
   - Include sessions, questions, accuracy
   - Group by day
   - Return timeline data

7. **`get_student_current_session(student_id)`**
   - Get student's current active session
   - Include skill, questions, accuracy, duration
   - Return session data or None

8. **`get_class_alerts(class_id, teacher_id)`**
   - Generate alerts for class
   - Prioritize by severity
   - Include actionable recommendations
   - Return list of alerts

9. **`track_session_activity(student_id, skill_id, question_id, correct)`**
   - Track real-time student activity
   - Update session metrics
   - Used for live monitoring
   - Return success

10. **`get_assignment_compliance(class_id)`**
    - Get assignment completion rates
    - Identify students with overdue assignments
    - Calculate on-time completion rate
    - Return compliance data

### Database Schema

**StudentSession Table (for real-time tracking):**

```sql
CREATE TABLE student_sessions (
    id INTEGER PRIMARY KEY,
    student_id INTEGER NOT NULL REFERENCES students(id),
    skill_id INTEGER REFERENCES skills(id),
    started_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    last_activity_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    questions_answered INTEGER DEFAULT 0,
    questions_correct INTEGER DEFAULT 0,
    accuracy FLOAT DEFAULT 0.0,
    is_active BOOLEAN DEFAULT TRUE,
    ended_at TIMESTAMP
);
```

**Indexes:**
```sql
CREATE INDEX idx_session_student ON student_sessions(student_id);
CREATE INDEX idx_session_active ON student_sessions(is_active);
CREATE INDEX idx_session_last_activity ON student_sessions(last_activity_at);
```

### API Endpoints

1. **`GET /api/monitoring/class/<class_id>`**
   - Get class monitoring dashboard
   - Returns: active students, status breakdown, alerts

2. **`GET /api/monitoring/student/<student_id>`**
   - Get student monitoring details
   - Returns: status, metrics, activity timeline

3. **`GET /api/monitoring/class/<class_id>/active`**
   - Get currently active students
   - Returns: list of active students with current activity

4. **`GET /api/monitoring/class/<class_id>/struggling`**
   - Get struggling students
   - Returns: list with struggling skills

5. **`GET /api/monitoring/class/<class_id>/inactive`**
   - Get inactive students
   - Returns: list with last active dates

6. **`GET /api/monitoring/class/<class_id>/alerts`**
   - Get class alerts
   - Returns: prioritized list of alerts

7. **`POST /api/monitoring/session/start`**
   - Start tracking student session
   - Body: `{ student_id, skill_id }`
   - Returns: session_id

8. **`POST /api/monitoring/session/activity`**
   - Track session activity
   - Body: `{ session_id, question_id, correct }`
   - Returns: updated session

9. **`POST /api/monitoring/session/end`**
   - End student session
   - Body: `{ session_id }`
   - Returns: session summary

---

## Frontend Implementation

### Components

**MonitoringDashboard (Teacher View):**
- Class selector dropdown
- Active students section (live updates every 30s)
- Status breakdown (pie chart or bars)
- Alerts panel
- Student list with filters
- Quick action buttons

**ActiveStudentsPanel:**
- List of currently active students
- Shows: name, current skill, progress, accuracy
- Live indicator (green dot)
- Auto-refresh every 30 seconds

**StudentStatusList:**
- Filterable student list
- Tabs: All, On Track, Needs Practice, Needs Help, Inactive
- Each student card shows:
  - Name, avatar
  - Status indicator
  - Last active
  - Current accuracy
  - Struggling skills count
  - Quick actions
- Sort by: status, last active, accuracy, name

**StudentMonitoringDetail:**
- Student header (name, status, last active)
- Activity timeline (7 days)
- Performance metrics
- Struggling skills list
- Assignment compliance
- Intervention recommendations
- Action buttons

**AlertsPanel:**
- Prioritized list of alerts
- Color-coded by severity
- Click to view student
- Dismiss or take action
- Filter by priority

---

## User Flows

### Teacher Monitors Class Activity

1. Teacher navigates to "Monitor" tab
2. Selects class from dropdown
3. Sees active students panel:
   - "3 students active now"
   - Student 1: Multiplication (Q 8/10, 90%)
   - Student 2: Division (Q 3/10, 67%)
   - Student 3: Fractions (Q 15/20, 85%)
4. Sees status breakdown:
   - On Track: 15 students (60%)
   - Needs Practice: 7 students (28%)
   - Needs Help: 2 students (8%)
   - Inactive: 1 student (4%)
5. Sees alerts:
   - [High] Student 5 inactive for 10 days
   - [Medium] Student 12 has 2 overdue assignments
   - [Low] Student 8's streak about to break
6. Clicks on Student 2 (struggling)
7. Sees detailed view with intervention options

### Teacher Intervenes with Struggling Student

1. Teacher sees alert: "Student 2 struggling with Division (55% accuracy)"
2. Clicks on alert to view student details
3. Sees:
   - Last active: 2 hours ago
   - Current accuracy: 55%
   - Struggling skills: Division (55%), Fractions (62%)
   - Assignment status: 1 overdue
4. Reviews activity timeline (shows declining performance)
5. Clicks "Create Targeted Assignment"
6. Modal opens with Division pre-selected
7. Creates 10-question easy assignment due tomorrow
8. Clicks "Send Message"
9. Writes: "I noticed you're working hard on division. I created a practice assignment to help. Let me know if you need help!"
10. Student receives assignment and message
11. Teacher monitors progress

### Student Practices (Tracked in Real-Time)

1. Student starts practice session
2. System creates StudentSession record
3. Student answers questions
4. Each answer updates session:
   - questions_answered++
   - questions_correct++ (if correct)
   - accuracy recalculated
   - last_activity_at updated
5. Teacher sees student in "Active Students" panel
6. Teacher can see live progress
7. Student finishes session
8. System marks session as ended
9. Student disappears from "Active Students"

---

## Business Logic

### Status Determination

```python
def get_student_status(student_id):
    # Get metrics
    accuracy = get_avg_accuracy(student_id)
    last_active = get_last_active(student_id)
    days_inactive = (datetime.utcnow() - last_active).days
    overdue_assignments = get_overdue_assignments(student_id)
    
    # Determine status
    if days_inactive > 14:
        return 'inactive'
    elif accuracy < 0.7 or days_inactive > 7 or len(overdue_assignments) >= 3:
        return 'needs_help'
    elif accuracy < 0.8 or days_inactive > 3 or len(overdue_assignments) > 0:
        return 'needs_practice'
    else:
        return 'on_track'
```

### Alert Generation

```python
def generate_alerts(class_id):
    alerts = []
    students = get_class_students(class_id)
    
    for student in students:
        # Inactivity alerts
        days_inactive = get_days_inactive(student.id)
        if days_inactive >= 7:
            alerts.append({
                'severity': 'high',
                'type': 'inactive',
                'student_id': student.id,
                'message': f'{student.name} inactive for {days_inactive} days',
                'action': 'Send reminder'
            })
        
        # Performance alerts
        accuracy = get_avg_accuracy(student.id)
        if accuracy < 0.6:
            alerts.append({
                'severity': 'high',
                'type': 'low_performance',
                'student_id': student.id,
                'message': f'{student.name} accuracy dropped to {accuracy:.0%}',
                'action': 'Create targeted assignment'
            })
        
        # Assignment alerts
        overdue = get_overdue_assignments(student.id)
        if len(overdue) >= 3:
            alerts.append({
                'severity': 'high',
                'type': 'overdue_assignments',
                'student_id': student.id,
                'message': f'{student.name} has {len(overdue)} overdue assignments',
                'action': 'Message student'
            })
    
    # Sort by severity
    priority_order = {'high': 0, 'medium': 1, 'low': 2}
    alerts.sort(key=lambda x: priority_order[x['severity']])
    
    return alerts
```

### Session Tracking

```python
def track_session_activity(student_id, skill_id, question_id, correct):
    # Get or create active session
    session = StudentSession.query.filter_by(
        student_id=student_id,
        is_active=True
    ).first()
    
    if not session:
        session = StudentSession(
            student_id=student_id,
            skill_id=skill_id
        )
        db.session.add(session)
    
    # Update session
    session.questions_answered += 1
    if correct:
        session.questions_correct += 1
    session.accuracy = session.questions_correct / session.questions_answered
    session.last_activity_at = datetime.utcnow()
    
    db.session.commit()
    return session
```

---

## Integration Points

### With Teacher Dashboard (7.1)
- Dashboard shows monitoring alerts
- Quick link to monitoring page
- Student cards link to monitoring detail

### With Assignment System (7.2)
- Monitor assignment completion
- Identify overdue assignments
- Create targeted assignments from monitoring

### With Learning Path System (3.1)
- Track skill practice in real-time
- Identify struggling skills
- Monitor skill mastery progress

### With Gamification (5.1-5.5)
- Track streak status
- Monitor XP earning rate
- Identify low-engagement students

### With Class System (6.3)
- Monitor class-level metrics
- Compare student performance
- Track class engagement

---

## Expected Impact

**Teacher Benefits:**
- Identify struggling students 50% faster
- Reduce student dropout by 30%
- Increase intervention effectiveness by 40%
- Save 3 hours per week on monitoring
- Proactive rather than reactive teaching

**Student Benefits:**
- Get help before falling too far behind
- Increased teacher attention when needed
- Higher success rates
- Better outcomes

**Platform Metrics:**
- 25% reduction in inactive students
- 35% improvement in struggling student outcomes
- 80% of teachers use monitoring weekly
- Average 5 interventions per week per teacher

---

## Success Metrics

- **Adoption:** 70% of teachers use monitoring weekly
- **Intervention Rate:** Average 5 interventions per week
- **Response Time:** Teachers intervene within 24 hours of alert
- **Effectiveness:** 60% of struggling students improve after intervention
- **Retention:** 30% reduction in student inactivity

---

## Future Enhancements

- **Predictive Analytics** - Predict which students will struggle
- **Automated Interventions** - Auto-create assignments for struggling students
- **Parent Notifications** - Alert parents of inactivity or low performance
- **Peer Tutoring** - Match struggling students with high performers
- **Video Conferencing** - Built-in video chat for one-on-one help
- **Smart Recommendations** - AI-powered intervention suggestions
- **Cohort Analysis** - Compare classes and identify trends

---

This design provides comprehensive real-time monitoring tools that enable teachers to identify and help struggling students before they fall behind, leading to better outcomes for all students!

