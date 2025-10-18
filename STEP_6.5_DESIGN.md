# Step 6.5: Social Feed - Design Document

## Overview

Implement a social activity feed that displays real-time updates about friend and classmate activities, creating an engaging social learning environment that motivates students through visibility of peer progress and achievements.

---

## Goals

1. **Activity Visibility** - Show friend and class member activities in real-time
2. **Social Engagement** - Keep students connected and motivated through peer updates
3. **Achievement Celebration** - Highlight accomplishments and milestones
4. **Filtered Views** - Allow students to filter by activity type and source
5. **Interactive Feed** - Enable reactions and interactions with activities

---

## Database Schema

### ActivityFeed Model

```python
class ActivityFeed(db.Model):
    __tablename__ = 'activity_feed'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    
    # Activity details
    activity_type = db.Column(db.String(50), nullable=False)
    # Types: 'skill_mastery', 'level_up', 'achievement_unlock', 'challenge_complete',
    #        'streak_milestone', 'friend_added', 'class_joined', 'practice_session'
    
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    
    # Related entities (optional, depends on activity type)
    skill_id = db.Column(db.Integer)
    achievement_id = db.Column(db.Integer)
    challenge_id = db.Column(db.Integer)
    class_id = db.Column(db.Integer)
    
    # Metadata
    xp_earned = db.Column(db.Integer, default=0)
    level_reached = db.Column(db.Integer)
    streak_days = db.Column(db.Integer)
    
    # Visibility
    visibility = db.Column(db.String(20), default='friends')  # 'public', 'friends', 'class', 'private'
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    student = db.relationship('Student', backref='activities')
```

### ActivityReaction Model (Optional Enhancement)

```python
class ActivityReaction(db.Model):
    __tablename__ = 'activity_reactions'
    
    id = db.Column(db.Integer, primary_key=True)
    activity_id = db.Column(db.Integer, db.ForeignKey('activity_feed.id'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    
    reaction_type = db.Column(db.String(20), nullable=False)  # 'like', 'celebrate', 'support'
    
    created_at = db.Column(db.Integer, default=datetime.utcnow)
    
    # Unique constraint
    __table_args__ = (db.UniqueConstraint('activity_id', 'student_id'),)
```

---

## Backend Implementation

### ActivityFeedService

**Core Methods:**

1. **`create_activity(student_id, activity_type, data)`**
   - Create new activity entry
   - Set visibility based on student preferences
   - Return activity object

2. **`get_feed(student_id, filter_type=None, limit=50)`**
   - Get personalized feed for student
   - Include friend activities
   - Include class member activities
   - Apply filters (activity type, time range)
   - Sort by created_at (newest first)
   - Respect privacy settings

3. **`get_student_activities(student_id, limit=20)`**
   - Get specific student's activities
   - Respect privacy settings
   - Return public/friends-only based on relationship

4. **`delete_activity(activity_id, student_id)`**
   - Delete activity (owner only)
   - Cascade delete reactions

5. **`get_activity_stats(student_id)`**
   - Count activities by type
   - Total XP from activities
   - Most active day/week

**Helper Methods:**

6. **`_get_friend_ids(student_id)`**
   - Get list of accepted friend IDs

7. **`_get_class_member_ids(student_id)`**
   - Get list of classmate IDs

8. **`_filter_by_visibility(activities, viewer_id)`**
   - Filter activities based on privacy settings
   - Check friend/class relationships

**Activity Creation Triggers:**

9. **`on_skill_mastery(student_id, skill_id)`**
   - Create activity when skill reaches 90%+

10. **`on_level_up(student_id, new_level)`**
    - Create activity when student levels up

11. **`on_achievement_unlock(student_id, achievement_id)`**
    - Create activity when achievement unlocked

12. **`on_challenge_complete(student_id, challenge_id)`**
    - Create activity when challenge completed

13. **`on_streak_milestone(student_id, streak_days)`**
    - Create activity for streak milestones (7, 14, 30, 60, 100 days)

---

## API Endpoints

### Feed Management

**GET `/api/feed`** - Get personalized activity feed
```
Query params:
  - type: Filter by activity type (optional)
  - limit: Number of activities (default 50)
  - offset: Pagination offset (default 0)

Response:
{
  "success": true,
  "activities": [
    {
      "id": 1,
      "student": {
        "id": 2,
        "name": "Alex",
        "avatar": "😊",
        "level": 5
      },
      "activity_type": "level_up",
      "title": "Alex reached Level 5!",
      "description": "Awesome progress!",
      "level_reached": 5,
      "xp_earned": 0,
      "created_at": "2024-12-20T10:00:00Z",
      "time_ago": "2 hours ago"
    }
  ],
  "has_more": false
}
```

**GET `/api/feed/student/<student_id>`** - Get specific student's activities
```
Response: List of public/visible activities
```

**DELETE `/api/feed/<activity_id>`** - Delete activity (owner only)

**GET `/api/feed/stats`** - Get feed statistics
```
Response:
{
  "total_activities": 45,
  "by_type": {
    "level_up": 5,
    "achievement_unlock": 12,
    "skill_mastery": 20,
    "challenge_complete": 8
  },
  "total_xp_shown": 5000
}
```

---

## Frontend Implementation

### SocialFeedPage Component

**Layout:**
```
┌─────────────────────────────────────────┐
│  📰 Activity Feed                       │
├─────────────────────────────────────────┤
│  [All] [Friends] [Classes] [Me]         │
├─────────────────────────────────────────┤
│  ┌───────────────────────────────────┐  │
│  │ 😊 Alex                           │  │
│  │ Level 5 • 2 hours ago             │  │
│  │                                   │  │
│  │ 🎉 Reached Level 5!               │  │
│  │ Awesome progress!                 │  │
│  │                                   │  │
│  │ [👍 5 likes]                      │  │
│  └───────────────────────────────────┘  │
│                                         │
│  ┌───────────────────────────────────┐  │
│  │ 🎓 Sarah                          │  │
│  │ Level 3 • 5 hours ago             │  │
│  │                                   │  │
│  │ ✅ Mastered Multiplication!       │  │
│  │ 95% accuracy on 50 questions      │  │
│  │ +150 XP                           │  │
│  │                                   │  │
│  │ [👍 12 likes] [🎉 3 celebrates]   │  │
│  └───────────────────────────────────┘  │
└─────────────────────────────────────────┘
```

**Features:**
- Four tabs: All, Friends, Classes, Me
- Infinite scroll loading
- Real-time updates (poll every 30s)
- Activity cards with icons
- Time ago formatting
- Reaction buttons (optional)
- Pull to refresh

### ActivityCard Component

**Card Types by Activity:**

1. **Skill Mastery**
   - Icon: ✅
   - Title: "Mastered [Skill Name]!"
   - Details: Accuracy, questions answered, XP earned
   - Color: Green

2. **Level Up**
   - Icon: 🎉
   - Title: "Reached Level [X]!"
   - Details: New level title, total XP
   - Color: Purple

3. **Achievement Unlock**
   - Icon: 🏆
   - Title: "Unlocked [Achievement Name]!"
   - Details: Achievement description, XP earned
   - Color: Gold

4. **Challenge Complete**
   - Icon: 🎯
   - Title: "Completed [Challenge Name]!"
   - Details: Rank, accuracy, XP earned
   - Color: Blue

5. **Streak Milestone**
   - Icon: 🔥
   - Title: "[X] Day Streak!"
   - Details: Streak count, consistency message
   - Color: Orange

6. **Friend Added**
   - Icon: 👥
   - Title: "Became friends with [Name]!"
   - Color: Light blue

7. **Class Joined**
   - Icon: 🎓
   - Title: "Joined [Class Name]!"
   - Color: Navy

8. **Practice Session**
   - Icon: 📝
   - Title: "Practiced [Skill Name]"
   - Details: Questions answered, accuracy
   - Color: Gray

---

## Activity Types & Triggers

### Automatic Activity Creation

| Activity Type | Trigger | Visibility | Data |
|--------------|---------|------------|------|
| skill_mastery | Skill reaches 90%+ | friends | skill_id, accuracy, xp_earned |
| level_up | Student levels up | friends | level_reached, total_xp |
| achievement_unlock | Achievement unlocked | friends | achievement_id, xp_earned |
| challenge_complete | Challenge completed | friends | challenge_id, rank, xp_earned |
| streak_milestone | Streak hits 7/14/30/60/100 | friends | streak_days |
| friend_added | Friendship accepted | friends | friend_id |
| class_joined | Joined class | class | class_id |
| practice_session | Completed practice (10+ questions) | private | skill_id, questions, accuracy |

---

## Integration Points

### With Gamification (5.1-5.5)
- Level-up events create activities
- Achievement unlocks create activities
- Streak milestones create activities
- XP gains shown in activities

### With Friend System (6.2)
- Friend activities appear in feed
- New friendships create activities
- Privacy settings respected

### With Class System (6.3)
- Class member activities shown
- Class-specific feed tab
- Class join events

### With Shared Challenges (6.4)
- Challenge completions create activities
- Challenge wins highlighted
- Leaderboard updates

### With Profile System (6.1)
- Profile privacy controls feed visibility
- Avatar and name displayed
- Link to profile from activities

---

## Privacy & Visibility

**Visibility Levels:**
- **Public** - Visible to all students
- **Friends** - Visible to accepted friends only
- **Class** - Visible to class members only
- **Private** - Not shown in feed

**Privacy Rules:**
- Respect student profile privacy settings
- Friends-only activities only shown to friends
- Class activities only shown to class members
- Private activities never shown

**Default Visibility by Type:**
- Skill mastery: Friends
- Level up: Friends
- Achievement unlock: Friends
- Challenge complete: Friends
- Streak milestone: Friends
- Friend added: Friends
- Class joined: Class
- Practice session: Private

---

## User Flows

### Viewing Feed
1. Click "📰 Feed" in navigation
2. See latest activities from friends/classes
3. Scroll to load more
4. Filter by tab (All/Friends/Classes/Me)
5. Click activity to view details
6. Click student name to view profile

### Activity Creation (Automatic)
1. Student completes skill mastery
2. System creates activity entry
3. Activity appears in friend feeds
4. Friends see update in real-time
5. Student sees in "Me" tab

### Reacting to Activity (Optional)
1. See friend's achievement
2. Click "👍 Like" button
3. Reaction count updates
4. Friend sees notification (future)

---

## Technical Implementation

### Backend Files

**New Files:**
1. `backend/src/models/activity_feed.py` - Activity models
2. `backend/src/services/activity_feed_service.py` - Feed business logic
3. `backend/src/routes/activity_feed_routes.py` - Feed API endpoints

**Modified Files:**
1. `backend/src/main.py` - Register activity routes
2. `backend/src/services/gamification_service.py` - Add activity creation on level up
3. `backend/src/services/achievement_service.py` - Add activity creation on unlock
4. `backend/src/services/shared_challenge_service.py` - Add activity on completion

### Frontend Files

**New Files:**
1. `frontend/src/components/SocialFeedPage.jsx` - Main feed page
2. `frontend/src/components/SocialFeedPage.css` - Feed styling
3. `frontend/src/components/ActivityCard.jsx` - Individual activity card
4. `frontend/src/components/ActivityCard.css` - Card styling

**Modified Files:**
1. `frontend/src/App.jsx` - Add feed route

### Testing

**Test File:** `backend/test_activity_feed_system.py`

**Test Cases:**
1. Create activity (various types)
2. Get personalized feed (with friends/classes)
3. Filter feed by activity type
4. Get student activities (with privacy)
5. Delete activity (owner only)
6. Respect privacy settings
7. Friend activities shown
8. Class activities shown
9. Private activities hidden
10. Activity stats calculation

---

## Performance Considerations

**Optimization Strategies:**
1. **Indexing** - Index on student_id, created_at, activity_type
2. **Pagination** - Limit results, use offset for infinite scroll
3. **Caching** - Cache friend/class lists
4. **Eager Loading** - Load student data with activities
5. **Selective Queries** - Only load visible activities

**Query Example:**
```python
# Get feed for student with friends [2, 3, 4] and classes [1, 2]
activities = ActivityFeed.query.filter(
    db.or_(
        # Friend activities
        db.and_(
            ActivityFeed.student_id.in_([2, 3, 4]),
            ActivityFeed.visibility.in_(['public', 'friends'])
        ),
        # Class activities
        db.and_(
            ActivityFeed.student_id.in_([...class_members]),
            ActivityFeed.visibility.in_(['public', 'class'])
        ),
        # Own activities
        ActivityFeed.student_id == student_id
    )
).order_by(ActivityFeed.created_at.desc()).limit(50).all()
```

---

## Success Metrics

**Engagement:**
- 60% of students check feed daily
- Average 5 minutes per session
- 80% of students have feed-visible activities

**Social Impact:**
- Increased friend connections
- Higher class participation
- More challenge participation
- Improved retention through social accountability

**Activity Volume:**
- Average 10 activities per student per week
- 50+ feed views per student per week
- High engagement with achievement/level-up activities

---

## Future Enhancements

1. **Comments** - Allow students to comment on activities
2. **Notifications** - Push notifications for friend activities
3. **Activity Sharing** - Share activities outside platform
4. **Trending** - Show trending skills/achievements
5. **Filters** - More granular filtering options
6. **Search** - Search activities by keyword
7. **Highlights** - Weekly/monthly activity highlights
8. **Groups** - Activity feeds for study groups

---

## Implementation Checklist

### Phase 1: Backend (Models + Service)
- [ ] Create ActivityFeed model
- [ ] Create ActivityFeedService with 13 methods
- [ ] Add database migrations

### Phase 2: Backend (API)
- [ ] Create activity_feed_routes.py with 4 endpoints
- [ ] Register routes in main.py
- [ ] Add authentication/authorization
- [ ] Implement privacy filtering

### Phase 3: Integration
- [ ] Add activity creation to gamification service
- [ ] Add activity creation to achievement service
- [ ] Add activity creation to challenge service
- [ ] Add activity creation to streak service

### Phase 4: Frontend (Components)
- [ ] Create SocialFeedPage with tabs
- [ ] Create ActivityCard component
- [ ] Add feed route to App.jsx
- [ ] Implement infinite scroll
- [ ] Add real-time updates

### Phase 5: Testing
- [ ] Write 10 comprehensive tests
- [ ] Test all API endpoints
- [ ] Test frontend components
- [ ] Integration testing

---

**Status:** Ready for implementation! 🚀

