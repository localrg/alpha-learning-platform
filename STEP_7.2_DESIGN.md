# Step 7.2: Assignment Creation - Design Document

## Overview

Enable teachers to create custom practice assignments for students and classes. Assignments specify which skills to practice, how many questions, difficulty level, and due date. This allows teachers to align the platform with classroom curriculum and track student compliance.

---

## Goals

1. **Enable structured practice** - Teachers assign specific skills for practice
2. **Track completion** - Monitor which students complete assignments
3. **Set deadlines** - Create urgency and accountability
4. **Differentiate instruction** - Assign different work to different students
5. **Measure effectiveness** - Track assignment performance vs. regular practice

---

## Database Schema

### Assignment Table

```sql
CREATE TABLE assignments (
    id INTEGER PRIMARY KEY,
    teacher_id INTEGER NOT NULL REFERENCES users(id),
    class_id INTEGER REFERENCES class_groups(id),  -- NULL for individual assignments
    title VARCHAR(200) NOT NULL,
    description TEXT,
    skill_ids JSON NOT NULL,  -- Array of skill IDs to practice
    question_count INTEGER NOT NULL DEFAULT 10,
    difficulty VARCHAR(20) DEFAULT 'adaptive',  -- 'easy', 'medium', 'hard', 'adaptive'
    due_date TIMESTAMP,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
```

### AssignmentStudent Table (Many-to-Many)

```sql
CREATE TABLE assignment_students (
    id INTEGER PRIMARY KEY,
    assignment_id INTEGER NOT NULL REFERENCES assignments(id),
    student_id INTEGER NOT NULL REFERENCES students(id),
    status VARCHAR(20) NOT NULL DEFAULT 'assigned',  -- 'assigned', 'in_progress', 'completed'
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    questions_answered INTEGER DEFAULT 0,
    questions_correct INTEGER DEFAULT 0,
    accuracy FLOAT DEFAULT 0.0,
    time_spent INTEGER DEFAULT 0,  -- seconds
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(assignment_id, student_id)
);
```

---

## Backend Implementation

### Models

**Assignment Model:**
- `id` - Primary key
- `teacher_id` - Creator
- `class_id` - Target class (NULL for individual)
- `title` - Assignment name
- `description` - Instructions
- `skill_ids` - JSON array of skill IDs
- `question_count` - Number of questions
- `difficulty` - Difficulty level
- `due_date` - Deadline
- `created_at`, `updated_at` - Timestamps

**AssignmentStudent Model:**
- `id` - Primary key
- `assignment_id` - Assignment reference
- `student_id` - Student reference
- `status` - Assignment status
- `started_at`, `completed_at` - Timing
- `questions_answered`, `questions_correct` - Progress
- `accuracy` - Performance
- `time_spent` - Time in seconds
- `created_at`, `updated_at` - Timestamps

### AssignmentService Methods

1. **`create_assignment(teacher_id, data)`**
   - Validate teacher owns class (if class assignment)
   - Create assignment record
   - Create AssignmentStudent records for each student
   - Return assignment with student count

2. **`get_assignment(assignment_id, user_id, role)`**
   - Get assignment details
   - Verify authorization (teacher owns or student assigned)
   - Include completion stats for teachers
   - Return assignment data

3. **`get_teacher_assignments(teacher_id, filters)`**
   - Get all assignments created by teacher
   - Filter by class, status, due date
   - Include completion stats
   - Sort by due date or creation date

4. **`get_student_assignments(student_id, filters)`**
   - Get all assignments for student
   - Filter by status, class, due date
   - Include progress data
   - Sort by due date

5. **`update_assignment(assignment_id, teacher_id, data)`**
   - Verify teacher owns assignment
   - Update assignment details
   - Cannot change after students start
   - Return updated assignment

6. **`delete_assignment(assignment_id, teacher_id)`**
   - Verify teacher owns assignment
   - Delete assignment and student records
   - Cannot delete after students complete
   - Return success

7. **`start_assignment(assignment_id, student_id)`**
   - Mark assignment as in_progress
   - Record started_at timestamp
   - Return assignment details and questions

8. **`submit_assignment_answer(assignment_id, student_id, question_id, answer)`**
   - Record answer
   - Update questions_answered, questions_correct
   - Calculate accuracy
   - Track time_spent
   - Return feedback

9. **`complete_assignment(assignment_id, student_id)`**
   - Mark assignment as completed
   - Record completed_at timestamp
   - Calculate final accuracy
   - Award XP based on performance
   - Return completion summary

10. **`get_assignment_stats(assignment_id, teacher_id)`**
    - Verify teacher owns assignment
    - Get completion rate
    - Get average accuracy
    - Get average time
    - Identify struggling students
    - Return stats

11. **`get_class_assignment_summary(class_id, teacher_id)`**
    - Verify teacher owns class
    - Get all assignments for class
    - Get completion rates
    - Get average performance
    - Return summary

12. **`get_student_assignment_progress(assignment_id, student_id)`**
    - Get student's progress on assignment
    - Get questions answered, remaining
    - Get current accuracy
    - Get time spent
    - Return progress data

### API Endpoints

1. **`POST /api/assignments`**
   - Create new assignment
   - Body: `{ title, description, class_id, student_ids, skill_ids, question_count, difficulty, due_date }`
   - Returns: Assignment object

2. **`GET /api/assignments`**
   - Get assignments (filtered by role)
   - Query params: `class_id`, `status`, `due_date_filter`
   - Returns: Array of assignments

3. **`GET /api/assignments/<id>`**
   - Get assignment details
   - Returns: Assignment with stats

4. **`PUT /api/assignments/<id>`**
   - Update assignment
   - Body: `{ title, description, due_date }`
   - Returns: Updated assignment

5. **`DELETE /api/assignments/<id>`**
   - Delete assignment
   - Returns: Success message

6. **`POST /api/assignments/<id>/start`**
   - Start assignment (student)
   - Returns: Assignment details and questions

7. **`POST /api/assignments/<id>/answer`**
   - Submit answer (student)
   - Body: `{ question_id, answer }`
   - Returns: Feedback

8. **`POST /api/assignments/<id>/complete`**
   - Complete assignment (student)
   - Returns: Completion summary with XP

9. **`GET /api/assignments/<id>/stats`**
   - Get assignment statistics (teacher)
   - Returns: Completion rate, avg accuracy, etc.

10. **`GET /api/assignments/<id>/progress`**
    - Get student progress (student)
    - Returns: Questions answered, accuracy, time

---

## Frontend Implementation

### Components

**CreateAssignmentModal:**
- Form to create new assignment
- Class or student selector
- Skill selector (multi-select)
- Question count input
- Difficulty selector
- Due date picker
- Submit button

**AssignmentsPage (Teacher View):**
- Tabs: All, Active, Completed, Overdue
- Assignment list with cards
- Each card shows:
  - Title, description
  - Class name
  - Skills (badges)
  - Due date
  - Completion rate (X/Y students)
  - Average accuracy
  - Actions: View, Edit, Delete
- "Create Assignment" button

**AssignmentDetailPage (Teacher View):**
- Assignment header (title, description, due date)
- Overall stats (completion rate, avg accuracy, avg time)
- Student list with progress:
  - Name, avatar
  - Status (assigned, in_progress, completed)
  - Questions answered
  - Accuracy
  - Time spent
  - Last activity
- Actions: Edit, Delete, Message Students

**AssignmentsPage (Student View):**
- Tabs: To Do, In Progress, Completed
- Assignment list with cards
- Each card shows:
  - Title, description
  - Class name
  - Skills (badges)
  - Due date (with urgency indicator)
  - Progress (X/Y questions)
  - Accuracy
  - Actions: Start, Continue, Review
- Overdue assignments highlighted in red

**AssignmentPracticePage (Student View):**
- Assignment header (title, progress)
- Question display
- Answer input
- Submit button
- Progress bar
- Time tracker
- "Complete Assignment" button when done

**AssignmentResultsPage (Student View):**
- Completion message
- Final stats (accuracy, time, XP earned)
- Skill breakdown
- Correct/incorrect questions
- "Back to Assignments" button

---

## User Flows

### Teacher Creates Class Assignment

1. Teacher clicks "Create Assignment" on dashboard
2. Modal opens with form
3. Teacher fills in:
   - Title: "Fractions Practice"
   - Description: "Practice adding and subtracting fractions"
   - Class: "Math 5A"
   - Skills: Select "Adding Fractions", "Subtracting Fractions"
   - Questions: 15
   - Difficulty: Medium
   - Due: Next Friday
4. Teacher clicks "Create"
5. System creates assignment
6. System creates AssignmentStudent record for each student in class
7. System shows success message
8. Assignment appears in teacher's list
9. Students see assignment in their "To Do" list

### Teacher Creates Individual Assignment

1. Teacher views student profile
2. Clicks "Create Assignment"
3. Modal opens with student pre-selected
4. Teacher fills in details
5. Clicks "Create"
6. System creates assignment for that student only
7. Assignment appears in both teacher and student lists

### Student Starts Assignment

1. Student sees assignment in "To Do" list
2. Clicks "Start Assignment"
3. System marks status as "in_progress"
4. System records started_at timestamp
5. System generates questions based on skills and difficulty
6. Student sees first question
7. Student answers questions one by one
8. System tracks progress, accuracy, time

### Student Completes Assignment

1. Student answers all questions
2. Clicks "Complete Assignment"
3. System marks status as "completed"
4. System records completed_at timestamp
5. System calculates final accuracy
6. System awards XP (base + accuracy bonus)
7. Student sees results page with stats
8. Assignment moves to "Completed" tab
9. Teacher sees updated completion rate

### Teacher Reviews Assignment Results

1. Teacher clicks on assignment
2. Sees overall stats (completion rate, avg accuracy)
3. Sees student list with individual progress
4. Identifies struggling students (low accuracy)
5. Clicks on student to see detailed results
6. Can message student or create follow-up assignment

---

## Business Logic

### Assignment Creation

- Teacher must own class (if class assignment)
- Must select at least 1 skill
- Question count: 5-50
- Due date must be in future (optional)
- If class assignment, creates record for each student
- If individual, creates record for specified students

### Assignment Modification

- Can edit title, description, due date
- Cannot edit skills, questions, difficulty after students start
- Cannot delete after students complete
- Can extend due date

### Assignment Completion

- Student must answer all questions to complete
- Partial completion tracked (questions_answered)
- Can pause and resume
- Accuracy calculated: questions_correct / questions_answered
- Time tracked from start to complete

### XP Rewards

- Base XP: 10 per question
- Accuracy bonus:
  - 90-100%: +50% XP
  - 80-89%: +25% XP
  - 70-79%: +10% XP
- On-time bonus: +20% XP if completed before due date
- Example: 15 questions, 90% accuracy, on-time
  - Base: 15 × 10 = 150 XP
  - Accuracy bonus: 150 × 0.5 = 75 XP
  - On-time bonus: 150 × 0.2 = 30 XP
  - Total: 255 XP

### Status Transitions

```
assigned → in_progress → completed
   ↓           ↓
(never started) (partially done)
```

- **assigned**: Created but not started
- **in_progress**: Started but not all questions answered
- **completed**: All questions answered

---

## Integration Points

### With Teacher Dashboard (7.1)

- Dashboard shows assignment count
- Shows overdue assignments alert
- Shows low completion rate alert
- Quick create assignment from class view

### With Learning Path System (3.1)

- Assignment questions generated from skills
- Difficulty adapts to student level
- Completion updates learning path
- Accuracy contributes to skill mastery

### With Gamification (5.1-5.5)

- XP awarded on completion
- Achievements for assignment completion
- Leaderboard for assignment performance
- Badges for on-time completion

### With Class System (6.3)

- Assignments created for classes
- Class roster determines students
- Class page shows assignments
- Assignment completion tracked per class

### With Assessment System (2.2)

- Questions generated from question bank
- Difficulty filtering applied
- Skill-specific questions
- Answer validation

---

## Expected Impact

**Teacher Benefits:**
- Assign specific practice aligned with curriculum
- Track student compliance and completion
- Identify struggling students early
- Differentiate instruction easily
- Reduce time creating paper assignments

**Student Benefits:**
- Clear expectations and deadlines
- Structured practice with accountability
- Immediate feedback on performance
- XP rewards for completion
- Progress tracking

**Platform Metrics:**
- 40% increase in questions answered
- 60% of teachers create assignments weekly
- 85% assignment completion rate
- 30% improvement in skill mastery
- Higher student engagement

---

## Success Metrics

- **Adoption:** 60% of teachers create assignments
- **Usage:** Average 2 assignments per week per teacher
- **Completion:** 85% of assignments completed on time
- **Performance:** Average 80% accuracy on assignments
- **Satisfaction:** 4.5/5 teacher rating for feature

---

## Future Enhancements

- **Assignment Templates** - Pre-made assignments for common topics
- **Collaborative Assignments** - Group work
- **Auto-Grading** - Automatic grading and feedback
- **Rubrics** - Custom grading criteria
- **Attachments** - Add files, videos, links
- **Comments** - Teacher feedback on submissions
- **Revisions** - Allow students to redo assignments
- **Parent Notifications** - Email parents about assignments
- **Calendar Integration** - Sync with Google Calendar
- **Analytics** - Detailed performance analytics

---

## Technical Considerations

### Performance

- Index on `teacher_id`, `class_id`, `student_id`, `due_date`
- Cache assignment lists for teachers
- Paginate student lists for large classes
- Optimize question generation

### Security

- Verify teacher owns class before creating assignment
- Verify student is assigned before allowing access
- Prevent students from seeing other students' answers
- Rate limit assignment creation

### Scalability

- Support classes up to 100 students
- Support teachers with 10+ classes
- Handle 1000+ concurrent assignments
- Efficient queries for assignment lists

---

## Implementation Plan

1. **Phase 1: Backend**
   - Create database models
   - Implement AssignmentService
   - Create API endpoints
   - Write tests

2. **Phase 2: Frontend (Teacher)**
   - Create assignment modal
   - Assignments list page
   - Assignment detail page
   - Edit/delete functionality

3. **Phase 3: Frontend (Student)**
   - Student assignments list
   - Assignment practice page
   - Results page
   - Progress tracking

4. **Phase 4: Integration**
   - Connect with learning paths
   - Connect with gamification
   - Connect with class system
   - Add to teacher dashboard

5. **Phase 5: Testing**
   - Unit tests for service methods
   - Integration tests for workflows
   - UI testing
   - Performance testing

---

This design provides a comprehensive assignment creation and tracking system that empowers teachers to align platform practice with classroom curriculum while maintaining student engagement through structured accountability!

