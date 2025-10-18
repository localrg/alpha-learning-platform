# Step 5.3: Leaderboards & Competition - Design Document

**Date:** October 17, 2025  
**Week:** 5 - Engagement & Motivation  
**Step:** 5.3 of 5.5

---

## Overview

The Leaderboards & Competition system creates healthy, motivating competition through rankings, challenges, and social comparison. This system leverages social comparison theory and competitive motivation while maintaining a supportive, growth-oriented environment.

---

## Design Goals

1. **Healthy Competition:** Motivate through friendly rivalry, not anxiety
2. **Multiple Leaderboards:** Recognize different types of achievement
3. **Fair Comparison:** Compare students at similar levels
4. **Privacy Options:** Allow students to opt-in/out of public rankings
5. **Positive Framing:** Celebrate improvement and effort, not just winning
6. **Accessibility:** Ensure all students can participate and succeed

---

## Leaderboard Types

### 1. Global XP Leaderboard
Ranks all students by total XP earned.

**Scope:** All students platform-wide  
**Metric:** Total XP  
**Update:** Real-time  
**Display:** Top 100, student's rank, nearby students

### 2. Grade-Level Leaderboard
Ranks students within the same grade level.

**Scope:** Students in same grade (e.g., Grade 5)  
**Metric:** Total XP  
**Update:** Real-time  
**Display:** Top 50, student's rank, nearby students

### 3. Weekly Leaderboard
Ranks students by XP earned in current week.

**Scope:** All students or grade-level  
**Metric:** XP earned this week  
**Reset:** Every Monday 00:00  
**Display:** Top 50, student's rank

### 4. Monthly Leaderboard
Ranks students by XP earned in current month.

**Scope:** All students or grade-level  
**Metric:** XP earned this month  
**Reset:** First day of each month  
**Display:** Top 50, student's rank

### 5. Skills Mastered Leaderboard
Ranks students by number of skills mastered.

**Scope:** All students or grade-level  
**Metric:** Total skills mastered  
**Update:** Real-time  
**Display:** Top 50, student's rank

### 6. Achievement Leaderboard
Ranks students by number of achievements unlocked.

**Scope:** All students or grade-level  
**Metric:** Total achievements unlocked  
**Update:** Real-time  
**Display:** Top 50, student's rank

### 7. Streak Leaderboard
Ranks students by current login/practice streak.

**Scope:** All students or grade-level  
**Metric:** Current streak (days)  
**Update:** Daily  
**Display:** Top 50, student's rank

---

## Ranking Mechanics

### Tie-Breaking Rules

When students have equal metrics:
1. **Secondary metric:** Time of achievement (earlier = higher rank)
2. **Tertiary metric:** Student ID (lower = higher rank)

### Rank Calculation

**Position:** 1, 2, 3, 4, ...  
**Percentile:** Top 1%, Top 5%, Top 10%, Top 25%, Top 50%  
**Tier:** Champion, Master, Expert, Intermediate, Beginner

### Privacy Settings

Students can choose:
- **Public:** Show on all leaderboards with full name
- **Anonymous:** Show on leaderboards as "Student #[ID]"
- **Private:** Don't show on public leaderboards (can still see own rank)

---

## Competition Features

### 1. Head-to-Head Challenges

Students can challenge friends to XP races.

**Duration:** 1 hour, 1 day, 1 week  
**Goal:** Earn more XP than opponent  
**Rewards:** Winner gets bonus XP and badge  
**Notifications:** Challenge sent, accepted, completed

### 2. Class Competitions

Teachers can create class-wide competitions.

**Types:** Most XP, Most skills mastered, Highest accuracy  
**Duration:** 1 day to 1 month  
**Prizes:** Virtual trophies, special badges  
**Display:** Class leaderboard

### 3. Daily Tournaments

Automated daily competitions for all students.

**Format:** Earn XP during specific time window  
**Tiers:** Bronze, Silver, Gold, Platinum (by current level)  
**Rewards:** XP multipliers for next day  
**Reset:** Daily at midnight

---

## Database Schema

### leaderboard_entries table (materialized view)
```sql
id                  INTEGER PRIMARY KEY
student_id          INTEGER FOREIGN KEY
leaderboard_type    VARCHAR(50)  -- 'global_xp', 'grade_xp', 'weekly_xp', etc.
metric_value        INTEGER      -- XP, skills, achievements, streak
rank                INTEGER      -- 1, 2, 3, ...
percentile          FLOAT        -- 0.01 = top 1%
tier                VARCHAR(20)  -- 'champion', 'master', 'expert', etc.
updated_at          DATETIME
```

### challenges table
```sql
id                  INTEGER PRIMARY KEY
challenger_id       INTEGER FOREIGN KEY
challenged_id       INTEGER FOREIGN KEY
challenge_type      VARCHAR(50)  -- 'xp_race', 'skill_race', 'accuracy_battle'
duration_hours      INTEGER
start_time          DATETIME
end_time            DATETIME
status              VARCHAR(20)  -- 'pending', 'active', 'completed', 'declined'
winner_id           INTEGER FOREIGN KEY NULL
challenger_score    INTEGER
challenged_score    INTEGER
created_at          DATETIME
```

### competitions table
```sql
id                  INTEGER PRIMARY KEY
name                VARCHAR(100)
description         VARCHAR(200)
competition_type    VARCHAR(50)  -- 'class', 'tournament', 'event'
metric_type         VARCHAR(50)  -- 'xp', 'skills', 'accuracy'
start_time          DATETIME
end_time            DATETIME
is_active           BOOLEAN
created_by          INTEGER FOREIGN KEY  -- Teacher ID
created_at          DATETIME
```

### competition_participants table
```sql
id                  INTEGER PRIMARY KEY
competition_id      INTEGER FOREIGN KEY
student_id          INTEGER FOREIGN KEY
score               INTEGER
rank                INTEGER
joined_at           DATETIME
```

---

## Backend Architecture

### Services

**LeaderboardService:**
- `get_global_leaderboard(limit, offset)` - Get global XP rankings
- `get_grade_leaderboard(grade, limit, offset)` - Get grade-level rankings
- `get_weekly_leaderboard(limit, offset)` - Get weekly XP rankings
- `get_monthly_leaderboard(limit, offset)` - Get monthly XP rankings
- `get_skills_leaderboard(limit, offset)` - Get skills mastered rankings
- `get_achievements_leaderboard(limit, offset)` - Get achievements rankings
- `get_streak_leaderboard(limit, offset)` - Get streak rankings
- `get_student_rank(student_id, leaderboard_type)` - Get specific student's rank
- `get_nearby_students(student_id, leaderboard_type, range)` - Get students near rank
- `refresh_leaderboards()` - Recalculate all leaderboard positions

**ChallengeService:**
- `create_challenge(challenger_id, challenged_id, type, duration)` - Create challenge
- `accept_challenge(challenge_id)` - Accept challenge
- `decline_challenge(challenge_id)` - Decline challenge
- `get_active_challenges(student_id)` - Get student's active challenges
- `update_challenge_scores(challenge_id)` - Update scores during challenge
- `complete_challenge(challenge_id)` - Finalize challenge and determine winner
- `get_challenge_history(student_id)` - Get past challenges

**CompetitionService:**
- `create_competition(name, type, metric, start, end)` - Create competition
- `join_competition(competition_id, student_id)` - Join competition
- `leave_competition(competition_id, student_id)` - Leave competition
- `update_competition_scores(competition_id)` - Update all participant scores
- `get_competition_leaderboard(competition_id)` - Get competition rankings
- `complete_competition(competition_id)` - Finalize and award prizes

### API Endpoints

**Leaderboards:**
- `GET /api/leaderboards/global` - Global XP leaderboard
- `GET /api/leaderboards/grade/:grade` - Grade-level leaderboard
- `GET /api/leaderboards/weekly` - Weekly leaderboard
- `GET /api/leaderboards/monthly` - Monthly leaderboard
- `GET /api/leaderboards/skills` - Skills mastered leaderboard
- `GET /api/leaderboards/achievements` - Achievements leaderboard
- `GET /api/leaderboards/streaks` - Streak leaderboard
- `GET /api/leaderboards/my-rank/:type` - Student's rank in specific leaderboard
- `GET /api/leaderboards/nearby/:type` - Students near student's rank

**Challenges:**
- `POST /api/challenges` - Create challenge
- `POST /api/challenges/:id/accept` - Accept challenge
- `POST /api/challenges/:id/decline` - Decline challenge
- `GET /api/challenges/active` - Get active challenges
- `GET /api/challenges/history` - Get challenge history
- `GET /api/challenges/:id` - Get challenge details

**Competitions:**
- `GET /api/competitions` - Get active competitions
- `POST /api/competitions/:id/join` - Join competition
- `POST /api/competitions/:id/leave` - Leave competition
- `GET /api/competitions/:id/leaderboard` - Get competition leaderboard

---

## Frontend Architecture

### Components

**1. LeaderboardPage Component**
- Tab navigation for different leaderboard types
- Top 50 list with ranks, names, scores
- Student's own rank highlighted
- "Nearby students" section
- Filter by grade level
- Refresh button

**2. LeaderboardCard Component**
- Rank badge (1st 🥇, 2nd 🥈, 3rd 🥉, others #)
- Student name/avatar
- Score (XP, skills, achievements, etc.)
- Trend indicator (↑↓→)
- View profile button

**3. MyRankWidget Component**
- Compact widget showing student's rank
- Multiple leaderboards in tabs
- Quick stats (rank, percentile, tier)
- "View Full Leaderboard" link

**4. ChallengesPage Component**
- Active challenges list
- Challenge creation form
- Challenge history
- Accept/decline buttons
- Live score tracking

**5. ChallengeCard Component**
- Opponent info
- Challenge type and duration
- Current scores
- Time remaining
- Status (pending, active, won, lost)

**6. CompetitionsPage Component**
- Active competitions list
- Join/leave buttons
- Competition leaderboards
- Prize information

---

## UI/UX Design

### Leaderboard Layout

```
┌─────────────────────────────────────────────┐
│  🏆 Leaderboards                            │
│                                             │
│  [Global] [Grade 5] [Weekly] [Monthly] ... │
│                                             │
│  ┌─────────────────────────────────────┐   │
│  │ 🥇 #1  Alice Smith      12,450 XP   │   │
│  │ 🥈 #2  Bob Johnson      11,890 XP   │   │
│  │ 🥉 #3  Carol Lee        10,234 XP   │   │
│  │ 👤 #4  David Chen        9,876 XP   │   │
│  │ 👤 #5  Emma Wilson       9,234 XP   │   │
│  │ ...                                  │   │
│  │ 👤 #47 YOU             2,345 XP ⭐   │   │
│  │ ...                                  │   │
│  └─────────────────────────────────────┘   │
│                                             │
│  Your Rank: #47 (Top 25%)                  │
│  Tier: Expert                               │
└─────────────────────────────────────────────┘
```

### Challenge Card

```
┌─────────────────────────────────────┐
│  ⚔️ XP Race Challenge               │
│                                     │
│  YOU          vs      Bob Johnson   │
│  1,234 XP             1,456 XP      │
│                                     │
│  Time Remaining: 2h 34m             │
│                                     │
│  [────────────────────] 65%         │
│                                     │
│  Status: You're behind! Keep going! │
└─────────────────────────────────────┘
```

### Rank Badges

**1st Place:** 🥇 Gold medal  
**2nd Place:** 🥈 Silver medal  
**3rd Place:** 🥉 Bronze medal  
**Top 10:** ⭐ Star  
**Top 25%:** 💎 Diamond  
**Top 50%:** 🔷 Blue diamond  
**Others:** 👤 Person icon

### Tier Badges

**Champion:** 👑 (Top 1%)  
**Master:** ⚡ (Top 5%)  
**Expert:** 💎 (Top 10%)  
**Intermediate:** 🔷 (Top 25%)  
**Beginner:** 🔹 (Everyone else)

---

## Gamification Psychology

### Social Comparison Theory

**Upward Comparison:** Seeing higher-ranked students motivates improvement.

**Downward Comparison:** Seeing lower-ranked students boosts confidence.

**Similar-Rank Comparison:** Nearby students create achievable goals.

### Competitive Motivation

**Mastery-Oriented:** Focus on personal improvement, not just beating others.

**Performance-Oriented:** Recognize achievement and ranking.

**Cooperative Competition:** Challenges can be friendly, not hostile.

### Mitigating Negative Effects

**Privacy Options:** Students can hide from public leaderboards.

**Multiple Leaderboards:** Success in different areas (not just XP).

**Time-Limited:** Weekly/monthly resets give everyone fresh starts.

**Tier System:** Compare within similar skill levels.

**Positive Messaging:** "Great progress!" not "You're losing!"

---

## Privacy & Safety

### Privacy Settings

Students can choose their visibility level:
- **Public:** Full name and avatar on leaderboards
- **Anonymous:** "Student #12345" on leaderboards
- **Private:** Not shown on public leaderboards

### Safety Measures

**No Direct Messaging:** Challenges don't include chat.

**Teacher Oversight:** Teachers can view all class competitions.

**Reporting:** Students can report inappropriate challenge requests.

**Age-Appropriate:** Different features for different age groups.

---

## Performance Considerations

### Caching Strategy

**Leaderboard Cache:**
- Cache top 100 for each leaderboard type
- Refresh every 5 minutes
- Invalidate on major XP changes

**Rank Cache:**
- Cache individual student ranks
- Refresh every 10 minutes
- Invalidate on student XP change

### Database Optimization

**Indexes:**
- Index on (leaderboard_type, rank)
- Index on (student_id, leaderboard_type)
- Index on (metric_value DESC)

**Materialized Views:**
- Pre-calculate leaderboard positions
- Refresh hourly or on-demand

**Pagination:**
- Limit queries to 50-100 results
- Use offset/limit for scrolling

---

## Success Metrics

**Engagement:**
- % of students who view leaderboards
- Average time spent on leaderboard page
- % of students who participate in challenges

**Motivation:**
- Correlation between leaderboard viewing and XP earning
- Challenge acceptance rate
- Competition participation rate

**Retention:**
- % of students who return after viewing leaderboard
- Impact of challenges on daily active users

---

## Future Enhancements

1. **Team Leaderboards** - Class vs. class competitions
2. **Skill-Specific Leaderboards** - Best at multiplication, fractions, etc.
3. **Achievement Showcases** - Display rare achievements
4. **Historical Rankings** - Track rank changes over time
5. **Prediction Leagues** - Predict who will win competitions
6. **Seasonal Leaderboards** - Special events and themes
7. **Custom Challenges** - Students create custom challenge types
8. **Spectator Mode** - Watch ongoing challenges

---

## Implementation Plan

### Phase 1: Backend (Current)
- Create leaderboard calculation service
- Implement ranking algorithms
- Build API endpoints
- Add caching layer

### Phase 2: Frontend
- Build leaderboard page
- Create rank widgets
- Implement challenge UI
- Add competition displays

### Phase 3: Integration
- Connect to XP system
- Add leaderboard links
- Implement notifications
- Test ranking accuracy

### Phase 4: Testing
- Test ranking calculations
- Verify tie-breaking
- Test privacy settings
- Load test with many students

---

This design creates a comprehensive leaderboard and competition system that motivates through healthy competition while maintaining a supportive, growth-oriented learning environment.

