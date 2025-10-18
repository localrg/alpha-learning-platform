# Step 6.2: Friend System - Design Document

## Overview

The Friend System enables students to connect with peers, view friend profiles, compare progress, and engage in social learning. This system builds on the profile system (Step 6.1) and enables collaborative features in subsequent steps.

---

## Core Features

### 1. Friend Requests
- Send friend requests to other students
- Accept or reject incoming requests
- View pending requests (sent and received)
- Cancel sent requests
- Request notifications

### 2. Friends List
- View all accepted friends
- Search/filter friends
- Remove friends
- Friend count display
- Online status (future enhancement)

### 3. Friend Profiles
- View friend profiles (using "friends" visibility from Step 6.1)
- See friend stats, achievements, activity
- Compare progress with friends
- Friend leaderboards

### 4. Friend Discovery
- Search students by name
- Browse suggested friends (same grade, similar level)
- View mutual friends
- Friend recommendations

---

## Database Schema

### Friendship Table
```sql
CREATE TABLE friendships (
    id INTEGER PRIMARY KEY,
    requester_id INTEGER NOT NULL,  -- Student who sent request
    addressee_id INTEGER NOT NULL,  -- Student who received request
    status VARCHAR(20) NOT NULL,    -- 'pending', 'accepted', 'rejected', 'blocked'
    created_at DATETIME NOT NULL,
    updated_at DATETIME NOT NULL,
    FOREIGN KEY (requester_id) REFERENCES students(id),
    FOREIGN KEY (addressee_id) REFERENCES students(id),
    UNIQUE(requester_id, addressee_id)
);
```

### Status Values
- **pending** - Request sent, awaiting response
- **accepted** - Friends (mutual connection)
- **rejected** - Request declined
- **blocked** - User blocked (future enhancement)

---

## API Endpoints

### Friend Requests
- `POST /api/friends/request/<student_id>` - Send friend request
- `GET /api/friends/requests/received` - Get received requests
- `GET /api/friends/requests/sent` - Get sent requests
- `PUT /api/friends/request/<friendship_id>/accept` - Accept request
- `PUT /api/friends/request/<friendship_id>/reject` - Reject request
- `DELETE /api/friends/request/<friendship_id>` - Cancel sent request

### Friends Management
- `GET /api/friends` - Get all friends
- `DELETE /api/friends/<student_id>` - Remove friend
- `GET /api/friends/search?q=<query>` - Search for students
- `GET /api/friends/suggestions` - Get friend suggestions

### Friend Features
- `GET /api/friends/leaderboard` - Friend-only leaderboard
- `GET /api/friends/<student_id>/profile` - View friend profile

---

## Business Logic

### Friend Request Flow
1. Student A sends request to Student B
2. Friendship record created: (A → B, status='pending')
3. Student B receives notification
4. Student B can accept or reject
5. If accepted: status='accepted', both can view each other's profiles
6. If rejected: status='rejected', request disappears

### Friendship Rules
- Cannot send duplicate requests
- Cannot send request to self
- Friendship is bidirectional (one record serves both directions)
- Removing friend deletes the friendship record
- Privacy: "friends" visibility now works with this system

### Friend Discovery
- **Search:** By name (first_name or last_name contains query)
- **Suggestions:** Same grade + not already friends + similar level (±3)
- **Limit:** Max 50 suggestions to prevent overwhelming

---

## Frontend Components

### FriendsPage
- Tabs: Friends List | Requests | Find Friends
- Friend cards with avatar, name, level, stats
- Request/Accept/Reject buttons
- Remove friend confirmation

### Friend Request Notification
- Badge on Friends nav button showing pending count
- Toast notifications for new requests
- Request list with accept/reject actions

### Friend Profile View
- Uses existing ProfilePage component
- Shows friend data (respects "friends" visibility)
- Compare stats side-by-side (future enhancement)

### Friend Search
- Search bar with real-time results
- Student cards with "Add Friend" button
- Filter by grade (optional)
- Suggested friends section

---

## Integration Points

### With Profile System (Step 6.1)
- Profile visibility "friends" now functional
- Friend profiles viewable through profile API
- Privacy settings respected

### With Leaderboards (Step 5.3)
- New friend-only leaderboard
- Compare XP, skills, achievements with friends
- Friend rankings

### Future Steps
- **Class Groups (6.3):** Friends can be added to groups
- **Shared Challenges (6.4):** Challenge friends directly
- **Social Feed (6.5):** See friend activity

---

## User Experience

### Sending Friend Request
1. Search for student or browse suggestions
2. Click "Add Friend" button
3. Button changes to "Request Sent"
4. Notification sent to recipient

### Receiving Friend Request
1. Badge appears on Friends button
2. Navigate to Friends → Requests tab
3. See requester profile preview
4. Click Accept or Reject
5. If accepted, friend added to list

### Viewing Friends
1. Navigate to Friends page
2. See all friends in grid layout
3. Click friend card to view profile
4. Remove friend if desired

---

## Privacy & Safety

### Privacy Controls
- Students can only send requests to visible profiles
- "Private" profiles cannot receive friend requests
- Friends can only see what privacy settings allow

### Safety Features
- No messaging (prevents inappropriate contact)
- Block feature (future enhancement)
- Report feature (future enhancement)
- Teacher/parent monitoring (Week 7/8)

---

## Performance Considerations

### Database Queries
- Index on (requester_id, addressee_id) for fast lookups
- Index on status for filtering
- Limit friend suggestions to 50 results
- Cache friend counts

### Scalability
- Friendship table grows as O(n²) worst case
- Typical student has 10-50 friends
- 1000 students = ~25,000 friendships max
- Easily handles expected load

---

## Success Metrics

### Engagement
- Friend request acceptance rate > 70%
- Average friends per student: 10-30
- Friend profile views per session: 2-5

### Social Features
- % students with at least 1 friend: > 60%
- Friend leaderboard usage: > 40% of students
- Friend comparison feature usage: > 30%

---

## Implementation Priority

**Phase 1 (Essential):**
- Friendship model and database
- Send/accept/reject requests
- Friends list
- Friend search

**Phase 2 (Important):**
- Friend suggestions
- Friend leaderboard
- Friend profile viewing
- Request notifications

**Phase 3 (Nice-to-have):**
- Mutual friends display
- Online status
- Block feature
- Advanced search filters

---

## Testing Strategy

### Unit Tests
- Send friend request
- Accept/reject request
- Remove friend
- Search students
- Friend suggestions
- Duplicate request prevention
- Self-request prevention

### Integration Tests
- Friend request flow end-to-end
- Profile visibility with friends
- Friend leaderboard accuracy
- Privacy settings enforcement

---

## Technical Notes

### Bidirectional Friendship
- Single record represents friendship
- Query both directions: WHERE (requester_id=X OR addressee_id=X) AND status='accepted'
- Simpler than two-record approach
- Consistent with social network best practices

### Status Transitions
- pending → accepted (accept)
- pending → rejected (reject)
- accepted → deleted (remove friend)
- pending → deleted (cancel request)

### Notification System
- Simple count badge for now
- Full notification system in future step
- Toast notifications for real-time updates

---

This design provides a complete, production-ready friend system that enables social learning while maintaining privacy and safety.

