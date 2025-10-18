# Step 7.1: Teacher Dashboard - Design Document

## Overview

Implement a comprehensive teacher dashboard that provides educators with a centralized view of their classes, student performance, and key metrics. The dashboard will enable teachers to quickly identify struggling students, monitor class progress, and make data-driven instructional decisions.

---

## Goals

1. **Class Overview** - Display all classes with key metrics at a glance
2. **Student Performance** - Show individual and aggregate student data
3. **Quick Actions** - Enable common tasks (create assignment, view student, message class)
4. **Data Visualization** - Present data through charts and graphs
5. **Alerts & Notifications** - Highlight students who need attention
6. **Responsive Design** - Work seamlessly on desktop and tablet

---

## User Roles

### Teacher Role

Teachers need a separate user role and authentication flow. Currently, the system only has student accounts.

**New User Model Field:**
```python
role = db.Column(db.String(20), nullable=False, default='student')  # 'student', 'teacher', 'admin'
```

**Teacher Profile:**
```python
class Teacher(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    school = db.Column(db.String(200))
    subject = db.Column(db.String(100))
    grade_levels = db.Column(db.String(50))  # e.g., "3,4,5"
    bio = db.Column(db.Text)
    avatar = db.Column(db.String(200), default='👨‍🏫')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
```

---

## Database Schema

### Teacher Model (New)

```python
class Teacher(db.Model):
    __tablename__ = 'teachers'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    school = db.Column(db.String(200))
    subject = db.Column(db.String(100))
    grade_levels = db.Column(db.String(50))
    bio = db.Column(db.Text)
    avatar = db.Column(db.String(200), default='👨‍🏫')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref=db.backref('teacher', uselist=False))
    classes = db.relationship('ClassGroup', backref='teacher', foreign_keys='ClassGroup.teacher_id')
```

### Update User Model

```python
# Add role field to User model
role = db.Column(db.String(20), nullable=False, default='student')
```

### Update ClassGroup Model

```python
# Change teacher_id to reference teachers table instead of users
teacher_id = db.Column(db.Integer, db.ForeignKey('teachers.id'), nullable=False)
```

---

## Backend Implementation

### TeacherService

**Core Methods:**

1. **`get_dashboard_data(teacher_id)`**
   - Get all classes for teacher
   - Calculate aggregate metrics
   - Identify students needing attention
   - Return dashboard summary

2. **`get_class_overview(class_id, teacher_id)`**
   - Verify teacher owns class
   - Get class details and student list
   - Calculate class performance metrics
   - Return class overview

3. **`get_student_summary(student_id, teacher_id)`**
   - Verify teacher has access to student
   - Get student progress data
   - Get recent activity
   - Return student summary

4. **`get_class_metrics(class_id)`**
   - Average accuracy per skill
   - Average questions answered
   - Average time spent
   - Mastery distribution
   - Engagement metrics

5. **`get_struggling_students(class_id, threshold=0.7)`**
   - Identify students below threshold
   - Sort by urgency
   - Return student list with issues

6. **`get_top_performers(class_id, limit=5)`**
   - Get students with highest performance
   - Sort by multiple metrics
   - Return top student list

7. **`get_class_activity_timeline(class_id, days=7)`**
   - Get daily activity counts
   - Get daily practice volume
   - Return timeline data

8. **`get_teacher_stats(teacher_id)`**
   - Total students across all classes
   - Total classes
   - Average class performance
   - Total practice questions answered

---

## API Endpoints

### Teacher Dashboard

**GET `/api/teacher/dashboard`** - Get teacher dashboard data
```
Response:
{
  "success": true,
  "teacher": {
    "id": 1,
    "name": "Ms. Johnson",
    "email": "johnson@school.edu",
    "avatar": "👩‍🏫"
  },
  "stats": {
    "total_students": 87,
    "total_classes": 3,
    "avg_class_performance": 0.78,
    "total_questions_answered": 12450
  },
  "classes": [
    {
      "id": 1,
      "name": "Math 5A",
      "student_count": 28,
      "avg_accuracy": 0.82,
      "active_students": 24,
      "struggling_students": 3,
      "recent_activity": 156
    }
  ],
  "alerts": [
    {
      "type": "struggling_student",
      "student_name": "Alex",
      "class_name": "Math 5A",
      "issue": "Low accuracy (65%) on multiplication",
      "severity": "medium"
    }
  ]
}
```

**GET `/api/teacher/class/<class_id>/overview`** - Get class overview
```
Response:
{
  "success": true,
  "class": {
    "id": 1,
    "name": "Math 5A",
    "student_count": 28,
    "grade_level": 5
  },
  "metrics": {
    "avg_accuracy": 0.82,
    "avg_questions_per_student": 45,
    "mastery_rate": 0.65,
    "engagement_rate": 0.86
  },
  "students": [
    {
      "id": 1,
      "name": "Alex",
      "level": 5,
      "total_xp": 1200,
      "avg_accuracy": 0.88,
      "questions_answered": 67,
      "last_active": "2 hours ago",
      "status": "on_track"
    }
  ],
  "skill_performance": [
    {
      "skill_name": "Multiplication",
      "avg_accuracy": 0.85,
      "students_mastered": 22,
      "students_struggling": 3
    }
  ]
}
```

**GET `/api/teacher/student/<student_id>/summary`** - Get student summary
```
Response:
{
  "success": true,
  "student": {
    "id": 1,
    "name": "Alex",
    "grade": 5,
    "level": 5,
    "total_xp": 1200
  },
  "performance": {
    "avg_accuracy": 0.88,
    "questions_answered": 67,
    "skills_mastered": 8,
    "current_streak": 5
  },
  "recent_activity": [
    {
      "date": "2024-12-20",
      "questions": 15,
      "accuracy": 0.93,
      "skills_practiced": ["Multiplication", "Division"]
    }
  ],
  "struggling_skills": [
    {
      "skill_name": "Fractions",
      "accuracy": 0.65,
      "attempts": 12
    }
  ]
}
```

**GET `/api/teacher/class/<class_id>/metrics`** - Get class metrics
**GET `/api/teacher/stats`** - Get teacher statistics

---

## Frontend Implementation

### TeacherDashboard Component

**Layout:**
```
┌─────────────────────────────────────────────────────────┐
│  👩‍🏫 Teacher Dashboard - Ms. Johnson                     │
├─────────────────────────────────────────────────────────┤
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐  │
│  │ 87       │ │ 3        │ │ 78%      │ │ 12,450   │  │
│  │ Students │ │ Classes  │ │ Avg Perf │ │ Questions│  │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘  │
├─────────────────────────────────────────────────────────┤
│  📢 Alerts & Notifications                              │
│  ⚠️ 3 students need attention in Math 5A                │
│  ✅ Math 5B completed weekly challenge                  │
├─────────────────────────────────────────────────────────┤
│  📚 My Classes                                          │
│  ┌───────────────────────────────────────────────────┐ │
│  │ Math 5A                          28 students      │ │
│  │ Avg Accuracy: 82%  |  Active: 24/28              │ │
│  │ [View Details] [Create Assignment] [Message]     │ │
│  └───────────────────────────────────────────────────┘ │
│  ┌───────────────────────────────────────────────────┐ │
│  │ Math 5B                          30 students      │ │
│  │ Avg Accuracy: 85%  |  Active: 28/30              │ │
│  │ [View Details] [Create Assignment] [Message]     │ │
│  └───────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
```

**Features:**
- Summary stats cards (students, classes, performance, questions)
- Alerts section highlighting issues
- Class list with quick metrics
- Quick action buttons
- Responsive grid layout

### ClassOverview Component

**Layout:**
```
┌─────────────────────────────────────────────────────────┐
│  Math 5A - Class Overview                               │
│  28 students  |  Grade 5  |  Created: Sep 2024         │
├─────────────────────────────────────────────────────────┤
│  Class Performance                                      │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐  │
│  │ 82%      │ │ 65%      │ │ 86%      │ │ 45       │  │
│  │ Accuracy │ │ Mastery  │ │ Active   │ │ Qs/Student│ │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘  │
├─────────────────────────────────────────────────────────┤
│  📊 Skill Performance                                   │
│  Multiplication    ████████░░ 85%  (22 mastered)       │
│  Division          ███████░░░ 78%  (18 mastered)       │
│  Fractions         █████░░░░░ 62%  (12 mastered)       │
├─────────────────────────────────────────────────────────┤
│  👥 Students                    [Sort: Performance ▼]   │
│  ┌─────────────────────────────────────────────────┐   │
│  │ 😊 Alex Smith         Level 5  |  88%  |  67 Qs │   │
│  │ Status: On Track      Last active: 2 hours ago  │   │
│  │ [View Profile] [Message]                        │   │
│  └─────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────┐   │
│  │ 😊 Sarah Johnson      Level 4  |  65%  |  34 Qs │   │
│  │ Status: ⚠️ Needs Help  Last active: 2 days ago   │   │
│  │ [View Profile] [Message]                        │   │
│  └─────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
```

**Features:**
- Class metrics overview
- Skill performance bars
- Student list with status indicators
- Sorting options (performance, activity, name)
- Quick actions per student

### StudentSummary Component

**Modal/Page showing detailed student view:**
```
┌─────────────────────────────────────────────────────────┐
│  😊 Alex Smith - Student Summary                        │
│  Grade 5  |  Level 5  |  1,200 XP  |  5-day streak     │
├─────────────────────────────────────────────────────────┤
│  Overall Performance                                    │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐  │
│  │ 88%      │ │ 67       │ │ 8        │ │ 5 days   │  │
│  │ Accuracy │ │ Questions│ │ Mastered │ │ Streak   │  │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘  │
├─────────────────────────────────────────────────────────┤
│  📈 Recent Activity (Last 7 Days)                       │
│  [Line chart showing daily questions and accuracy]      │
├─────────────────────────────────────────────────────────┤
│  ⚠️ Struggling Skills                                   │
│  • Fractions - 65% accuracy (12 attempts)               │
│  • Word Problems - 70% accuracy (8 attempts)            │
├─────────────────────────────────────────────────────────┤
│  ✅ Mastered Skills                                     │
│  • Multiplication (1-digit) - 95%                       │
│  • Addition (2-digit) - 92%                             │
│  • Subtraction (2-digit) - 90%                          │
└─────────────────────────────────────────────────────────┘
```

---

## Data Visualization

### Charts & Graphs

**Class Performance Chart:**
- Bar chart showing average accuracy per skill
- Color coding: Green (>80%), Yellow (70-80%), Red (<70%)

**Activity Timeline:**
- Line chart showing daily practice volume
- 7-day or 30-day view
- Shows questions answered and active students

**Student Progress Chart:**
- Line chart showing individual student accuracy over time
- Multiple skills on same chart

**Mastery Distribution:**
- Pie chart showing % of students: Mastered, On Track, Struggling

---

## Alert System

### Alert Types

**Struggling Student:**
- Trigger: Accuracy < 70% on any skill
- Severity: Medium
- Action: Review student, create intervention

**Inactive Student:**
- Trigger: No activity for 3+ days
- Severity: High
- Action: Send message, check in

**Low Engagement:**
- Trigger: < 10 questions per week
- Severity: Medium
- Action: Motivate, assign practice

**Skill Gap:**
- Trigger: Entire class struggling on skill (avg < 70%)
- Severity: High
- Action: Re-teach concept, create assignment

**Achievement:**
- Trigger: Student reaches milestone
- Severity: Low (positive)
- Action: Celebrate, share with class

---

## User Flows

### Teacher Login & Dashboard View

1. Teacher logs in with credentials
2. System checks role = 'teacher'
3. Redirects to teacher dashboard
4. Loads all classes and metrics
5. Displays alerts and notifications
6. Shows class list with quick stats

### Viewing Class Details

1. Teacher clicks "View Details" on class card
2. System loads class overview
3. Displays class metrics and charts
4. Shows student list with performance
5. Highlights struggling students
6. Provides quick actions

### Viewing Student Summary

1. Teacher clicks student name
2. System loads student data
3. Displays performance metrics
4. Shows recent activity chart
5. Lists struggling and mastered skills
6. Provides intervention options

---

## Technical Implementation

### Backend Files

**New Files:**
1. `backend/src/models/teacher.py` - Teacher model
2. `backend/src/services/teacher_service.py` - Teacher business logic
3. `backend/src/routes/teacher_routes.py` - Teacher API endpoints

**Modified Files:**
1. `backend/src/models/user.py` - Add role field
2. `backend/src/models/class_group.py` - Update teacher_id foreign key
3. `backend/src/main.py` - Register teacher routes

### Frontend Files

**New Files:**
1. `frontend/src/components/TeacherDashboard.jsx` - Main dashboard
2. `frontend/src/components/TeacherDashboard.css` - Dashboard styling
3. `frontend/src/components/ClassOverview.jsx` - Class detail view
4. `frontend/src/components/ClassOverview.css` - Class styling
5. `frontend/src/components/StudentSummary.jsx` - Student detail modal
6. `frontend/src/components/StudentSummary.css` - Student styling
7. `frontend/src/components/TeacherNav.jsx` - Teacher navigation

**Modified Files:**
1. `frontend/src/App.jsx` - Add teacher routes
2. `frontend/src/contexts/AuthContext.jsx` - Handle teacher role

### Testing

**Test File:** `backend/test_teacher_dashboard.py`

**Test Cases:**
1. Create teacher account
2. Get dashboard data
3. Get class overview
4. Get student summary
5. Get class metrics
6. Get struggling students
7. Get top performers
8. Get activity timeline
9. Get teacher stats
10. Verify teacher-only access

---

## Success Metrics

**Adoption:**
- 80% of teachers log in weekly
- Average 3 dashboard views per login
- 60% use class overview regularly

**Efficiency:**
- Reduce time to identify struggling students by 70%
- Increase intervention speed by 50%
- Save 2 hours per week on progress monitoring

**Impact:**
- 30% increase in teacher-student interactions
- 25% improvement in struggling student outcomes
- Higher teacher satisfaction with platform

---

## Future Enhancements

1. **Custom Reports** - Generate PDF reports for parents/admin
2. **Comparison Views** - Compare classes or time periods
3. **Goal Setting** - Set class goals and track progress
4. **Predictive Analytics** - Predict which students will struggle
5. **Messaging** - Direct messaging to students/parents
6. **Announcements** - Post announcements to class
7. **Calendar Integration** - Sync with school calendar
8. **Export Data** - Export to CSV/Excel

---

## Implementation Checklist

### Phase 1: Teacher Role & Authentication
- [ ] Add role field to User model
- [ ] Create Teacher model
- [ ] Update authentication to handle roles
- [ ] Create teacher registration flow

### Phase 2: Backend Services
- [ ] Create TeacherService with 8 methods
- [ ] Implement dashboard data aggregation
- [ ] Implement class metrics calculation
- [ ] Implement student summary generation

### Phase 3: API Endpoints
- [ ] Create teacher_routes.py with 5 endpoints
- [ ] Register routes in main.py
- [ ] Add teacher-only authentication
- [ ] Test all endpoints

### Phase 4: Frontend Dashboard
- [ ] Create TeacherDashboard component
- [ ] Create summary stats cards
- [ ] Create alerts section
- [ ] Create class list
- [ ] Add navigation

### Phase 5: Class Overview
- [ ] Create ClassOverview component
- [ ] Implement metrics display
- [ ] Create student list
- [ ] Add sorting and filtering
- [ ] Implement charts

### Phase 6: Student Summary
- [ ] Create StudentSummary component
- [ ] Display performance metrics
- [ ] Show activity timeline
- [ ] List struggling/mastered skills
- [ ] Add quick actions

### Phase 7: Testing
- [ ] Write 10 comprehensive tests
- [ ] Test teacher authentication
- [ ] Test data aggregation
- [ ] Test frontend components
- [ ] Integration testing

---

**Status:** Ready for implementation! 🚀

