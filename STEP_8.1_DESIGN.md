# Step 8.1: Parent Accounts - Design Document

## Overview

Parent accounts enable parents to access the platform, link to their children's accounts, and view their progress. This is the foundation for the parent portal, providing authentication, authorization, and child management capabilities.

---

## Goals

1. **Enable parent registration** - Parents can create accounts and link to children
2. **Support multiple children** - One parent account can manage multiple children
3. **Provide secure access** - Parents can only view their own children's data
4. **Enable child linking** - Parents can link to existing student accounts via invite codes
5. **Support notifications** - Foundation for email notifications about child progress

---

## Core Features

### Parent Registration

**Registration Flow:**
1. Parent visits registration page
2. Enters email, password, name
3. Optionally enters child information
4. Creates account
5. Receives verification email (future feature)
6. Logs in to parent portal

**Account Information:**
- Email (unique, used for login)
- Password (hashed)
- Name
- Phone number (optional)
- Notification preferences
- Created date

### Child Linking

**Linking Methods:**

**Method 1: During Registration**
- Parent enters child's name and email during registration
- System searches for existing student account
- If found, sends link request to student
- Student approves link request
- Parent gains access to child's data

**Method 2: Via Invite Code**
- Student generates parent invite code from their account
- Student shares code with parent
- Parent enters code in "Add Child" form
- Link created immediately (pre-approved)
- Parent gains access to child's data

**Method 3: Manual Linking (Admin)**
- School administrator links parent to child
- Used for bulk imports or special cases
- No approval needed

**Link Management:**
- View all linked children
- Remove child link (parent-initiated)
- Approve/reject link requests
- Set primary contact parent

### Authorization

**Access Rules:**
- Parents can only view data for linked children
- Parents cannot modify student data (read-only access)
- Parents cannot view other students' data
- Parents can view teacher information for child's classes
- Parents can send messages to teachers (future feature)

**Privacy Controls:**
- Students can hide specific data from parents (future feature)
- Teachers can control what parents see (future feature)
- Parents can control notification preferences

### Notification Preferences

**Notification Types:**
- Daily progress summary (email)
- Weekly performance report (email)
- Assignment due reminders (email, SMS)
- Low performance alerts (email, SMS)
- Inactivity alerts (email, SMS)
- Achievement notifications (email)

**Preferences:**
- Enable/disable each notification type
- Choose delivery method (email, SMS, both)
- Set frequency (immediate, daily digest, weekly digest)
- Quiet hours (no notifications during certain times)

---

## Backend Implementation

### Database Schema

**Parents Table:**
```sql
CREATE TABLE parents (
    id INTEGER PRIMARY KEY,
    user_id INTEGER UNIQUE NOT NULL REFERENCES users(id),
    name VARCHAR(100) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    phone VARCHAR(20),
    notification_preferences JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Parent-Child Links Table:**
```sql
CREATE TABLE parent_child_links (
    id INTEGER PRIMARY KEY,
    parent_id INTEGER NOT NULL REFERENCES parents(id),
    student_id INTEGER NOT NULL REFERENCES students(id),
    relationship VARCHAR(50) DEFAULT 'parent',
    is_primary_contact BOOLEAN DEFAULT FALSE,
    status VARCHAR(20) DEFAULT 'active',
    linked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(parent_id, student_id)
);
```

**Link Requests Table:**
```sql
CREATE TABLE link_requests (
    id INTEGER PRIMARY KEY,
    parent_id INTEGER NOT NULL REFERENCES parents(id),
    student_id INTEGER NOT NULL REFERENCES students(id),
    request_type VARCHAR(20) NOT NULL,
    status VARCHAR(20) DEFAULT 'pending',
    invite_code VARCHAR(20) UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP,
    approved_at TIMESTAMP,
    rejected_at TIMESTAMP
);
```

### Parent Model

```python
class Parent(db.Model):
    __tablename__ = 'parents'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    phone = db.Column(db.String(20))
    notification_preferences = db.Column(db.JSON)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref='parent_profile')
    children = db.relationship('ParentChildLink', back_populates='parent')
```

### ParentService Methods

1. **`create_parent_account(user_id, name, email, phone, notification_prefs)`**
   - Create parent profile
   - Set default notification preferences
   - Return parent object

2. **`link_child_by_code(parent_id, invite_code)`**
   - Validate invite code
   - Check if code is expired
   - Create parent-child link
   - Return link object

3. **`request_child_link(parent_id, student_email)`**
   - Find student by email
   - Create link request
   - Notify student of request
   - Return request object

4. **`approve_link_request(request_id, student_id)`**
   - Validate request belongs to student
   - Create parent-child link
   - Update request status
   - Notify parent of approval

5. **`reject_link_request(request_id, student_id)`**
   - Validate request belongs to student
   - Update request status
   - Notify parent of rejection

6. **`get_linked_children(parent_id)`**
   - Get all active child links
   - Return list of student objects

7. **`remove_child_link(parent_id, student_id)`**
   - Validate link exists
   - Update link status to 'removed'
   - Return success

8. **`generate_invite_code(student_id)`**
   - Generate unique 8-character code
   - Create link request with code
   - Set expiration (7 days)
   - Return invite code

9. **`update_notification_preferences(parent_id, preferences)`**
   - Validate preferences
   - Update parent record
   - Return updated parent

10. **`get_parent_by_user_id(user_id)`**
    - Get parent profile by user ID
    - Return parent object

---

## API Endpoints

### Parent Management
- `POST /api/parents/register` - Create parent account
- `GET /api/parents/profile` - Get parent profile
- `PUT /api/parents/profile` - Update parent profile
- `PUT /api/parents/notifications` - Update notification preferences

### Child Linking
- `POST /api/parents/link-child` - Link child by invite code
- `POST /api/parents/request-link` - Request link to child by email
- `GET /api/parents/children` - Get all linked children
- `DELETE /api/parents/children/<id>` - Remove child link

### Link Requests
- `GET /api/parents/link-requests` - Get pending link requests (for students)
- `POST /api/parents/link-requests/<id>/approve` - Approve link request
- `POST /api/parents/link-requests/<id>/reject` - Reject link request
- `POST /api/parents/generate-invite` - Generate parent invite code (for students)

---

## User Flows

### Parent Registers and Links Child

1. Parent visits parent registration page
2. Enters:
   - Name: "Jane Smith"
   - Email: "jane@email.com"
   - Password: "********"
   - Phone: "555-1234" (optional)
3. Clicks "Create Account"
4. Account created with role='parent'
5. Redirected to "Link Children" page
6. Sees two options:
   - "I have an invite code from my child"
   - "Request link by entering my child's email"
7. Parent selects "I have an invite code"
8. Enters code: "ABC123XY"
9. System validates code
10. Shows: "Link to Student Name?"
11. Parent clicks "Yes, Link Account"
12. Link created
13. Parent redirected to parent dashboard
14. Sees child's progress overview

### Student Generates Invite Code for Parent

1. Student logs in
2. Navigates to Settings
3. Clicks "Parent Access"
4. Sees "Generate Parent Invite Code" button
5. Clicks button
6. System generates code: "ABC123XY"
7. Shows code with instructions:
   - "Share this code with your parent"
   - "Code expires in 7 days"
   - "Your parent will be able to view your progress"
8. Student copies code
9. Shares with parent via text/email
10. Parent uses code to link account

### Parent Requests Link by Email

1. Parent logs in
2. Clicks "Add Child"
3. Selects "Request link by email"
4. Enters child's email: "student@email.com"
5. Clicks "Send Request"
6. System finds student account
7. Creates link request
8. Student receives notification:
   - "Jane Smith (jane@email.com) wants to link to your account"
   - "Approve" or "Reject" buttons
9. Student clicks "Approve"
10. Link created
11. Parent receives notification: "Link request approved"
12. Parent can now view child's progress

---

## Business Logic

### Invite Code Generation

```python
def generate_invite_code(student_id):
    # Generate random 8-character code
    code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
    
    # Check if code already exists
    while LinkRequest.query.filter_by(invite_code=code).first():
        code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
    
    # Create link request
    request = LinkRequest(
        student_id=student_id,
        request_type='invite_code',
        invite_code=code,
        expires_at=datetime.utcnow() + timedelta(days=7),
        status='pending'
    )
    db.session.add(request)
    db.session.commit()
    
    return code
```

### Link Child by Code

```python
def link_child_by_code(parent_id, invite_code):
    # Find link request
    request = LinkRequest.query.filter_by(
        invite_code=invite_code,
        status='pending'
    ).first()
    
    if not request:
        return {'error': 'Invalid or expired code'}, 404
    
    # Check expiration
    if request.expires_at < datetime.utcnow():
        return {'error': 'Code has expired'}, 400
    
    # Create link
    link = ParentChildLink(
        parent_id=parent_id,
        student_id=request.student_id,
        status='active'
    )
    db.session.add(link)
    
    # Update request
    request.status = 'approved'
    request.approved_at = datetime.utcnow()
    request.parent_id = parent_id
    
    db.session.commit()
    
    return {'success': True, 'link': link.to_dict()}, 201
```

### Default Notification Preferences

```python
DEFAULT_NOTIFICATION_PREFS = {
    'daily_summary': {'enabled': True, 'method': 'email'},
    'weekly_report': {'enabled': True, 'method': 'email'},
    'assignment_due': {'enabled': True, 'method': 'email'},
    'low_performance': {'enabled': True, 'method': 'email'},
    'inactivity_alert': {'enabled': True, 'method': 'email'},
    'achievements': {'enabled': False, 'method': 'email'},
    'quiet_hours': {'start': '22:00', 'end': '08:00'}
}
```

---

## Integration Points

### With User Authentication (Week 1)
- Parent accounts use existing User model
- Role='parent' added to User
- Login/logout uses existing auth system
- Password reset uses existing system

### With Student Accounts (Week 2)
- Parents link to existing student accounts
- Student data remains in student tables
- Parents have read-only access to student data

### With Teacher Tools (Week 7)
- Parents can view teachers for child's classes
- Parents can see teacher messages to child (future)
- Parents can send messages to teachers (future)

### Foundation for Future Features
- Child progress view (Step 8.2)
- Activity reports (Step 8.3)
- Parent-teacher communication (Step 8.4)
- Goal setting (Step 8.5)

---

## Expected Impact

**Parent Benefits:**
- Visibility into child's learning progress
- Receive alerts about performance issues
- Stay informed about assignments and deadlines
- Support child's learning at home

**Student Benefits:**
- Parental support and encouragement
- Accountability through parent visibility
- Recognition for achievements
- Help when struggling

**Platform Metrics:**
- 60% of students have parent accounts linked
- 40% of parents check progress weekly
- 80% of parents have notifications enabled
- 25% increase in student engagement with parent involvement

---

## Success Metrics

- **Registration Rate:** 60% of students have parent linked within 1 month
- **Engagement Rate:** 40% of parents log in weekly
- **Notification Opt-in:** 80% of parents enable at least one notification
- **Link Approval Rate:** 90% of link requests approved within 24 hours
- **Retention Impact:** 20% higher student retention with parent involvement

---

This implementation provides the foundation for parent engagement, with secure account management, flexible child linking, and notification preferences that enable parents to stay informed about their child's learning journey!

