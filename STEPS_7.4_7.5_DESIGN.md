# Steps 7.4 & 7.5: Performance Analytics + Intervention Tools - Design Document

## Overview

These final two steps of Week 7 complete the teacher toolset by adding detailed performance analytics and quick intervention capabilities. They are combined into a single implementation as they work together: analytics identify issues, and intervention tools provide solutions.

---

## Goals

1. **Provide detailed performance insights** - Help teachers understand student progress through data and visualizations
2. **Enable trend analysis** - Show progress over time to identify improving or declining students
3. **Support data-driven decisions** - Give teachers the information needed to make instructional choices
4. **Enable quick interventions** - Provide one-click actions to help struggling students
5. **Track intervention effectiveness** - Monitor which interventions work

---

## Step 7.4: Performance Analytics

### Core Features

**Student Performance Reports:**
- Overall performance summary (accuracy, questions answered, time spent)
- Skill-by-skill breakdown with mastery status
- Progress over time (daily/weekly/monthly views)
- Comparison to class average
- Strengths and weaknesses identification
- Recent activity summary

**Class Performance Reports:**
- Class-wide metrics (average accuracy, engagement rate, completion rate)
- Student ranking and distribution
- Skill mastery heatmap (which skills the class struggles with)
- Progress trends over time
- Comparison to other classes (if multiple classes)
- Top performers and struggling students

**Trend Analysis:**
- Accuracy trend over time (line chart)
- Questions answered per week (bar chart)
- Skill mastery progress (progress bars)
- Engagement trends (active days per week)
- Assignment completion trends
- XP earning rate over time

**Skill Analytics:**
- Skill mastery distribution across class
- Average accuracy per skill
- Time to mastery per skill
- Students struggling with each skill
- Skill prerequisite analysis
- Recommended focus skills

**Export Capabilities:**
- Export reports to PDF
- Export data to CSV
- Print-friendly report layouts
- Share reports with parents (future)
- Email reports to administrators (future)

### Analytics Service Methods

1. **`get_student_performance_report(student_id, date_range)`**
   - Comprehensive performance summary
   - Skill breakdown
   - Trend data
   - Return detailed report

2. **`get_class_performance_report(class_id, date_range)`**
   - Class-wide metrics
   - Student distribution
   - Skill heatmap
   - Return class report

3. **`get_student_trend_data(student_id, metric, days)`**
   - Get trend data for specific metric
   - Metrics: accuracy, questions, time, xp
   - Return time-series data

4. **`get_class_trend_data(class_id, metric, days)`**
   - Get class-wide trend data
   - Aggregate student metrics
   - Return time-series data

5. **`get_skill_analytics(class_id, skill_id)`**
   - Skill-specific analytics
   - Student performance on skill
   - Mastery distribution
   - Return skill analytics

6. **`get_student_comparison(student_id, class_id)`**
   - Compare student to class average
   - Percentile ranking
   - Relative strengths/weaknesses
   - Return comparison data

7. **`export_report_pdf(report_data, report_type)`**
   - Generate PDF report
   - Format for printing
   - Return PDF file

---

## Step 7.5: Intervention Tools

### Core Features

**Quick Actions:**

**1. Send Message**
- Pre-filled message templates for common situations
- Custom message composition
- Message history tracking
- Delivery confirmation
- Student notification

**2. Create Targeted Assignment**
- Pre-filled with struggling skills
- Recommended question count and difficulty
- Suggested due date
- One-click creation
- Automatic student assignment

**3. Schedule Meeting**
- Calendar integration
- Meeting type selection (one-on-one, parent conference, group)
- Time slot selection
- Email invitation
- Meeting reminders

**4. Notify Parent**
- Email notification to parent
- Performance summary included
- Specific concerns highlighted
- Suggested actions
- Response tracking

**5. Assign Peer Tutor**
- Match struggling student with high performer
- Create peer tutoring assignment
- Track tutoring sessions
- Monitor improvement

**6. Mark Alert as Resolved**
- Track intervention taken
- Record resolution notes
- Monitor effectiveness
- Re-alert if issue persists

**Message Templates:**

**For Inactive Students:**
- "Hi [Student], I noticed you haven't practiced in [X] days. Is everything okay? Let me know if you need help!"
- "Hey [Student], we miss you! Can you hop on and practice for a few minutes today?"
- "Hi [Student], your class is working on [Skill]. Can you practice 10 questions today?"

**For Struggling Students:**
- "Hi [Student], I see you're working hard on [Skill]. I created an easier assignment to help you build confidence."
- "Hey [Student], [Skill] can be tricky! Let's meet tomorrow to go over it together."
- "Hi [Student], I noticed you're struggling with [Skill]. Try watching the video tutorial first, then practice."

**For Overdue Assignments:**
- "Hi [Student], the [Assignment] is due soon. Can you complete it today?"
- "Hey [Student], I see you haven't started [Assignment] yet. Do you need help getting started?"
- "Hi [Student], [Assignment] was due yesterday. Please complete it as soon as possible."

**For Encouragement:**
- "Great job on [Assignment], [Student]! Keep up the excellent work!"
- "Wow, [Student]! Your accuracy on [Skill] improved to [X]%. Awesome progress!"
- "Hi [Student], you're on a [X]-day streak! Keep it going!"

### Intervention Service Methods

1. **`send_message(teacher_id, student_id, message, template_id)`**
   - Send message to student
   - Track message history
   - Notify student
   - Return success

2. **`create_targeted_assignment(teacher_id, student_id, auto_fill=True)`**
   - Create assignment for struggling student
   - Auto-fill with struggling skills
   - Set recommended difficulty
   - Return assignment

3. **`schedule_meeting(teacher_id, student_id, meeting_type, datetime)`**
   - Schedule meeting
   - Send invitations
   - Create calendar event
   - Return meeting

4. **`notify_parent(teacher_id, student_id, concern_type, message)`**
   - Send email to parent
   - Include performance summary
   - Track notification
   - Return success

5. **`assign_peer_tutor(teacher_id, student_id, tutor_id)`**
   - Match student with tutor
   - Create tutoring assignment
   - Track sessions
   - Return tutoring record

6. **`mark_alert_resolved(teacher_id, alert_id, resolution_notes, action_taken)`**
   - Mark alert as resolved
   - Record intervention
   - Track effectiveness
   - Return success

7. **`get_intervention_history(teacher_id, student_id)`**
   - Get all interventions for student
   - Show effectiveness
   - Identify patterns
   - Return history

8. **`get_message_templates(category)`**
   - Get pre-written message templates
   - Categories: inactive, struggling, overdue, encouragement
   - Return templates

---

## Backend Implementation

### Database Schema

**Messages Table:**
```sql
CREATE TABLE teacher_messages (
    id INTEGER PRIMARY KEY,
    teacher_id INTEGER NOT NULL REFERENCES users(id),
    student_id INTEGER NOT NULL REFERENCES students(id),
    message TEXT NOT NULL,
    template_id INTEGER REFERENCES message_templates(id),
    sent_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    read_at TIMESTAMP,
    is_read BOOLEAN DEFAULT FALSE
);
```

**Message Templates Table:**
```sql
CREATE TABLE message_templates (
    id INTEGER PRIMARY KEY,
    category VARCHAR(50) NOT NULL,
    title VARCHAR(200) NOT NULL,
    content TEXT NOT NULL,
    variables JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Interventions Table:**
```sql
CREATE TABLE interventions (
    id INTEGER PRIMARY KEY,
    teacher_id INTEGER NOT NULL REFERENCES users(id),
    student_id INTEGER NOT NULL REFERENCES students(id),
    alert_id INTEGER REFERENCES alerts(id),
    intervention_type VARCHAR(50) NOT NULL,
    action_taken TEXT NOT NULL,
    resolution_notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    resolved_at TIMESTAMP,
    is_resolved BOOLEAN DEFAULT FALSE,
    effectiveness_rating INTEGER
);
```

**Meetings Table:**
```sql
CREATE TABLE meetings (
    id INTEGER PRIMARY KEY,
    teacher_id INTEGER NOT NULL REFERENCES users(id),
    student_id INTEGER NOT NULL REFERENCES students(id),
    meeting_type VARCHAR(50) NOT NULL,
    scheduled_at TIMESTAMP NOT NULL,
    duration_minutes INTEGER DEFAULT 30,
    location VARCHAR(200),
    notes TEXT,
    status VARCHAR(20) DEFAULT 'scheduled',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### API Endpoints

**Analytics Endpoints:**
- `GET /api/analytics/student/<id>/report` - Student performance report
- `GET /api/analytics/class/<id>/report` - Class performance report
- `GET /api/analytics/student/<id>/trends` - Student trend data
- `GET /api/analytics/class/<id>/trends` - Class trend data
- `GET /api/analytics/skill/<id>` - Skill analytics
- `GET /api/analytics/student/<id>/comparison` - Student vs class comparison
- `POST /api/analytics/export/pdf` - Export report to PDF

**Intervention Endpoints:**
- `POST /api/interventions/message` - Send message to student
- `POST /api/interventions/assignment` - Create targeted assignment
- `POST /api/interventions/meeting` - Schedule meeting
- `POST /api/interventions/notify-parent` - Notify parent
- `POST /api/interventions/peer-tutor` - Assign peer tutor
- `PUT /api/interventions/<id>/resolve` - Mark intervention resolved
- `GET /api/interventions/student/<id>` - Get intervention history
- `GET /api/interventions/templates` - Get message templates

---

## Frontend Implementation

### Components

**PerformanceReportPage:**
- Report type selector (student/class)
- Date range picker
- Performance metrics cards
- Trend charts (line, bar, pie)
- Skill breakdown table
- Export buttons

**StudentReportView:**
- Student header with photo and status
- Overall metrics (accuracy, questions, time)
- Skill mastery progress bars
- Trend charts
- Recent activity timeline
- Comparison to class average
- Quick intervention buttons

**ClassReportView:**
- Class header with student count
- Class-wide metrics
- Student distribution chart
- Skill heatmap
- Top performers list
- Struggling students list
- Trend charts

**InterventionModal:**
- Action selector (message, assignment, meeting, etc.)
- Context-aware pre-filling
- Template selector (for messages)
- Custom input fields
- Preview before sending
- Confirmation and tracking

**MessageComposer:**
- Template dropdown
- Variable replacement (student name, skill, etc.)
- Rich text editor
- Character count
- Send button
- Message history

**MeetingScheduler:**
- Calendar view
- Time slot selector
- Meeting type dropdown
- Location input
- Notes field
- Send invitation button

---

## User Flows

### Teacher Views Student Performance Report

1. Teacher clicks on student in monitoring dashboard
2. Clicks "View Performance Report" button
3. Performance report page opens
4. Sees overall metrics:
   - Accuracy: 75%
   - Questions answered: 450
   - Time spent: 12 hours
   - Skills mastered: 8/15
5. Sees trend chart showing accuracy improving from 65% to 75% over 4 weeks
6. Sees skill breakdown:
   - Multiplication: 90% (Mastered)
   - Division: 75% (In Progress)
   - Fractions: 60% (Needs Work)
7. Sees comparison: "Student is at 50th percentile in class"
8. Clicks "Export PDF" to save report for parent conference

### Teacher Sends Message to Inactive Student

1. Teacher sees alert: "[HIGH] Student 5 inactive for 10 days"
2. Clicks "Take Action" button
3. Intervention modal opens
4. Selects "Send Message" action
5. Selects template: "Inactive - Check In"
6. Message pre-fills: "Hi Student 5, I noticed you haven't practiced in 10 days. Is everything okay? Let me know if you need help!"
7. Teacher customizes: Adds "We're working on fractions this week - it would be great to see you!"
8. Clicks "Send Message"
9. Message sent to student
10. Alert marked with "Message sent" tag
11. Student receives notification
12. Student replies: "Sorry, I was sick. I'll practice today!"
13. Teacher sees reply in message history

### Teacher Creates Targeted Assignment

1. Teacher views Student 3's performance report
2. Sees struggling skills: Division (60%), Fractions (55%)
3. Clicks "Create Targeted Assignment" button
4. Assignment creation modal opens with:
   - Skills: Division, Fractions (pre-selected)
   - Question count: 15 (recommended)
   - Difficulty: Easy (recommended based on accuracy)
   - Due date: 3 days from now (suggested)
5. Teacher adjusts title: "Division & Fractions Practice"
6. Clicks "Create Assignment"
7. Assignment created and assigned to Student 3
8. Student receives notification
9. Teacher tracks completion in monitoring dashboard

---

## Business Logic

### Performance Report Generation

```python
def get_student_performance_report(student_id, date_range):
    # Get all sessions in date range
    sessions = get_sessions(student_id, date_range)
    
    # Calculate overall metrics
    total_questions = sum(s.questions_answered for s in sessions)
    total_correct = sum(s.questions_correct for s in sessions)
    total_time = sum(s.duration for s in sessions)
    avg_accuracy = total_correct / total_questions if total_questions > 0 else 0
    
    # Get skill breakdown
    skills = get_student_skills(student_id)
    skill_breakdown = []
    for skill in skills:
        skill_sessions = [s for s in sessions if s.skill_id == skill.id]
        skill_accuracy = calculate_accuracy(skill_sessions)
        skill_mastery = determine_mastery(skill_accuracy, skill_sessions)
        skill_breakdown.append({
            'skill': skill.name,
            'accuracy': skill_accuracy,
            'mastery': skill_mastery,
            'questions': sum(s.questions_answered for s in skill_sessions)
        })
    
    # Get trend data
    trend_data = get_trend_data(student_id, 'accuracy', 30)
    
    # Get class comparison
    class_avg = get_class_average_accuracy(student_id)
    percentile = calculate_percentile(student_id, avg_accuracy)
    
    return {
        'overall': {
            'accuracy': avg_accuracy,
            'questions': total_questions,
            'time': total_time,
            'skills_mastered': sum(1 for s in skill_breakdown if s['mastery'] == 'mastered')
        },
        'skills': skill_breakdown,
        'trends': trend_data,
        'comparison': {
            'class_average': class_avg,
            'percentile': percentile
        }
    }
```

### Targeted Assignment Creation

```python
def create_targeted_assignment(teacher_id, student_id, auto_fill=True):
    if auto_fill:
        # Get struggling skills
        struggling_skills = get_struggling_skills(student_id, threshold=0.7)
        skill_ids = [s['skill_id'] for s in struggling_skills[:3]]  # Top 3
        
        # Determine difficulty
        avg_accuracy = get_avg_accuracy(student_id)
        if avg_accuracy < 0.6:
            difficulty = 'easy'
        elif avg_accuracy < 0.75:
            difficulty = 'medium'
        else:
            difficulty = 'hard'
        
        # Set question count
        question_count = 15  # Standard for targeted practice
        
        # Set due date (3 days from now)
        due_date = datetime.utcnow() + timedelta(days=3)
        
        # Create assignment
        assignment_data = {
            'title': f'Targeted Practice - {", ".join(s["skill_name"] for s in struggling_skills[:3])}',
            'description': 'Practice assignment to help improve your skills',
            'student_ids': [student_id],
            'skill_ids': skill_ids,
            'question_count': question_count,
            'difficulty': difficulty,
            'due_date': due_date.isoformat()
        }
        
        return AssignmentService.create_assignment(teacher_id, assignment_data)
```

---

## Integration Points

### With Monitoring System (7.3)
- Analytics use session data from monitoring
- Interventions triggered from monitoring alerts
- Alert resolution tracked in interventions

### With Assignment System (7.2)
- Analytics show assignment completion trends
- Targeted assignments created from analytics
- Assignment performance included in reports

### With Learning Path System (3.1)
- Skill analytics based on learning path data
- Mastery status from learning paths
- Skill recommendations use path data

### With Gamification (5.1-5.5)
- XP trends included in analytics
- Achievement progress in reports
- Leaderboard position in comparison

---

## Expected Impact

**Teacher Benefits:**
- Make data-driven instructional decisions
- Identify trends and patterns in student performance
- Intervene quickly with one-click actions
- Track intervention effectiveness
- Save time with pre-written message templates
- Export reports for parent conferences

**Student Benefits:**
- Receive timely help when struggling
- Get personalized practice assignments
- Feel supported by teacher attention
- Improve faster with targeted interventions
- Stay engaged through teacher communication

**Platform Metrics:**
- 80% of teachers use analytics weekly
- Average 5 interventions per week per teacher
- 60% of interventions result in improvement
- 40% reduction in time from problem to intervention
- 90% of teachers use message templates

---

## Success Metrics

- **Analytics Adoption:** 80% of teachers view reports weekly
- **Intervention Rate:** Average 5 interventions per week
- **Response Time:** Teachers intervene within 24 hours
- **Effectiveness:** 60% of struggling students improve after intervention
- **Template Usage:** 70% of messages use templates
- **Export Usage:** 50% of teachers export reports monthly

---

This combined implementation completes the teacher toolset with powerful analytics for understanding student performance and quick intervention tools for helping struggling students!

