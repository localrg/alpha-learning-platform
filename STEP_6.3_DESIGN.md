# Step 6.3: Class Groups - Design Document

## Overview

The Class Groups system enables teachers to organize students into classes and allows students to collaborate through group activities, shared progress tracking, and group leaderboards.

## Core Features (Streamlined)

### 1. Class Model
- **Class/Group entity** with name, description, teacher, grade level
- **Membership tracking** with join dates and roles
- **Group statistics** (member count, average progress, total XP)

### 2. Membership Management
- **Teacher creates class** with name and description
- **Students join via invite code** (6-character alphanumeric)
- **Teacher can remove members** if needed
- **Students can leave class** voluntarily

### 3. Group Features
- **Class leaderboard** showing member rankings
- **Group progress dashboard** with aggregate stats
- **Member list** with individual stats
- **Activity feed** showing recent class achievements

## Database Schema

### ClassGroup Table
```
id: Integer (PK)
name: String(100) - "Mrs. Smith's 5th Grade Math"
description: Text - Optional class description
teacher_id: Integer (FK to users) - Class creator/owner
grade_level: Integer - Target grade (3-8)
invite_code: String(6) - Unique join code
created_at: DateTime
updated_at: DateTime
```

### ClassMembership Table
```
id: Integer (PK)
class_id: Integer (FK to class_groups)
student_id: Integer (FK to students)
role: String(20) - 'teacher' or 'student'
joined_at: DateTime
```

## API Endpoints (Streamlined)

### Class Management
- `POST /api/classes` - Create new class (teacher only)
- `GET /api/classes` - Get user's classes
- `GET /api/classes/<id>` - Get class details
- `PUT /api/classes/<id>` - Update class (teacher only)
- `DELETE /api/classes/<id>` - Delete class (teacher only)

### Membership
- `POST /api/classes/join` - Join class via invite code
- `DELETE /api/classes/<id>/leave` - Leave class
- `DELETE /api/classes/<id>/members/<student_id>` - Remove member (teacher)
- `GET /api/classes/<id>/members` - Get class members

### Group Stats
- `GET /api/classes/<id>/leaderboard` - Class leaderboard
- `GET /api/classes/<id>/stats` - Aggregate class statistics

## Frontend Components

### ClassesPage
- **My Classes tab** - List of joined classes
- **Join Class tab** - Enter invite code to join
- **Create Class tab** - For teachers to create classes

### ClassDetailPage
- **Class header** with name, description, member count
- **Tabs:** Members | Leaderboard | Stats
- **Invite code display** for teachers
- **Leave/manage buttons** based on role

## User Roles

### Teacher Role
- Create classes
- Generate invite codes
- Remove members
- View all class stats
- Cannot be removed from own class

### Student Role
- Join classes via invite code
- View class leaderboard and stats
- Leave class voluntarily
- See other members' progress

## Business Rules

1. **Invite codes** are unique, 6-character alphanumeric
2. **Students can join multiple classes** (no limit)
3. **Teachers own their classes** (creator = owner)
4. **Class deletion** removes all memberships
5. **Leaving class** removes membership but preserves student data
6. **Class leaderboard** shows only class members
7. **Privacy respected** - only show data allowed by profile settings

## Integration Points

### With Profile System (6.1)
- Member cards show profile avatars and bios
- Privacy settings control what's visible to classmates

### With Friend System (6.2)
- Classmates can send friend requests
- Friend status shown on member cards

### With Gamification (5.1-5.3)
- Class leaderboard uses XP and levels
- Group XP total displayed
- Class achievements possible

### Future Steps
- **Shared Challenges (6.4):** Class-wide challenges
- **Social Feed (6.5):** Class activity feed

## Success Metrics

- **Engagement:** % of students in at least 1 class > 70%
- **Collaboration:** Average class size 15-30 students
- **Retention:** Students in classes have 20% higher retention
- **Usage:** Class leaderboard viewed 2-3x per week per student

## Implementation Notes

### Invite Code Generation
```python
import random
import string

def generate_invite_code():
    """Generate unique 6-character code."""
    while True:
        code = ''.join(random.choices(
            string.ascii_uppercase + string.digits, 
            k=6
        ))
        if not ClassGroup.query.filter_by(invite_code=code).first():
            return code
```

### Class Leaderboard Query
```python
# Get all members with their progress
members = db.session.query(
    Student, StudentProgress
).join(
    ClassMembership, ClassMembership.student_id == Student.id
).outerjoin(
    StudentProgress, StudentProgress.student_id == Student.id
).filter(
    ClassMembership.class_id == class_id
).order_by(
    StudentProgress.total_xp.desc()
).all()
```

## Simplified Scope

To maintain velocity, this implementation focuses on:
- ✅ Core class creation and membership
- ✅ Invite code system
- ✅ Class leaderboard
- ✅ Basic member management
- ❌ Advanced permissions (defer to later)
- ❌ Class announcements (defer to social feed)
- ❌ Class-specific content (defer to later)

This provides essential group functionality while keeping implementation lean and efficient.

