# Step 5.4: Daily Challenges - Design Document

**Date:** October 17, 2025  
**Week:** 5 - Engagement & Motivation  
**Step:** 5.4 of 5.5

---

## Overview

The Daily Challenges system creates **time-limited practice challenges** that refresh every 24 hours, providing bonus XP and rewards for completing focused practice sessions. This feature adds **urgency**, **routine**, and **variety** to the learning experience.

---

## Goals

1. **Create Daily Routine:** Encourage students to log in and practice every day
2. **Add Urgency:** Time-limited challenges create FOMO (fear of missing out)
3. **Provide Variety:** Different challenge types keep practice interesting
4. **Reward Consistency:** Bonus XP for completing daily challenges
5. **Track Progress:** Challenge history and completion statistics

---

## Challenge Types

### 1. Question Marathon
**Description:** Answer X questions correctly  
**Difficulty Scaling:** Easy (5), Medium (10), Hard (15)  
**Bonus XP:** 50 / 100 / 150  
**Example:** "Answer 10 questions correctly today!"

### 2. Skill Focus
**Description:** Practice a specific skill  
**Difficulty Scaling:** Easy (3 questions), Medium (5), Hard (10)  
**Bonus XP:** 75 / 125 / 200  
**Example:** "Master multiplication today! Answer 5 multiplication questions."

### 3. Perfect Streak
**Description:** Get X questions correct in a row  
**Difficulty Scaling:** Easy (3), Medium (5), Hard (10)  
**Bonus XP:** 100 / 150 / 250  
**Example:** "Get 5 questions correct in a row without mistakes!"

### 4. Speed Challenge
**Description:** Answer X questions in Y minutes  
**Difficulty Scaling:** Easy (5 in 10min), Medium (10 in 15min), Hard (15 in 20min)  
**Bonus XP:** 75 / 125 / 200  
**Example:** "Answer 10 questions in 15 minutes!"

### 5. Review Master
**Description:** Complete X review sessions  
**Difficulty Scaling:** Easy (1), Medium (2), Hard (3)  
**Bonus XP:** 50 / 100 / 150  
**Example:** "Complete 2 review sessions today!"

### 6. Resource Explorer
**Description:** Watch videos or view resources  
**Difficulty Scaling:** Easy (1), Medium (2), Hard (3)  
**Bonus XP:** 30 / 60 / 100  
**Example:** "Watch 2 tutorial videos today!"

---

## Challenge Generation Algorithm

### Daily Reset
**Time:** Midnight in student's timezone (or UTC if not set)  
**Frequency:** Once per 24 hours  
**Generation:** Automatic when student logs in after reset

### Difficulty Selection
```
Student Level → Challenge Difficulty
Level 1-3:     60% Easy, 30% Medium, 10% Hard
Level 4-7:     30% Easy, 50% Medium, 20% Hard
Level 8-12:    10% Easy, 40% Medium, 50% Hard
Level 13+:     5% Easy, 30% Medium, 65% Hard
```

### Challenge Selection
**Daily Challenges:** 3 challenges per day  
**Types:** Random selection from 6 types (no duplicates)  
**Variety:** Ensure mix of challenge types

**Example Daily Set:**
- Challenge 1: Question Marathon (Medium) - 100 XP
- Challenge 2: Skill Focus (Easy) - 75 XP
- Challenge 3: Perfect Streak (Hard) - 250 XP
- **Total Possible:** 425 bonus XP per day

---

## Database Schema

### DailyChallenge Table
```
id: Integer (PK)
student_id: Integer (FK → students.id)
challenge_type: String (question_marathon, skill_focus, perfect_streak, speed_challenge, review_master, resource_explorer)
difficulty: String (easy, medium, hard)
target_value: Integer (number to achieve, e.g., 10 questions)
target_skill_id: Integer (FK → skills.id, nullable, for skill_focus type)
time_limit_minutes: Integer (nullable, for speed_challenge)
bonus_xp: Integer (reward amount)
status: String (active, completed, expired)
progress: Integer (current progress toward target)
created_at: DateTime
expires_at: DateTime (24 hours from creation)
completed_at: DateTime (nullable)
```

### Indexes
- `student_id, status, expires_at` - Fast active challenge lookup
- `student_id, created_at` - Challenge history queries

---

## API Endpoints

### GET /api/challenges/daily
**Description:** Get today's active challenges for student  
**Response:**
```json
{
  "challenges": [
    {
      "id": 1,
      "type": "question_marathon",
      "difficulty": "medium",
      "description": "Answer 10 questions correctly today!",
      "target": 10,
      "progress": 3,
      "bonus_xp": 100,
      "status": "active",
      "expires_at": "2025-10-18T00:00:00Z",
      "time_remaining": "14h 23m"
    }
  ]
}
```

### POST /api/challenges/generate
**Description:** Generate new daily challenges (called automatically after midnight)  
**Response:**
```json
{
  "success": true,
  "challenges": [...],
  "message": "3 new challenges generated!"
}
```

### POST /api/challenges/:id/progress
**Description:** Update challenge progress  
**Body:**
```json
{
  "increment": 1
}
```
**Response:**
```json
{
  "success": true,
  "challenge": {...},
  "completed": false,
  "xp_awarded": 0
}
```

### GET /api/challenges/history
**Description:** Get challenge completion history  
**Query Params:** `limit`, `offset`, `status`  
**Response:**
```json
{
  "history": [
    {
      "date": "2025-10-17",
      "completed": 2,
      "total": 3,
      "xp_earned": 175
    }
  ],
  "stats": {
    "total_completed": 45,
    "total_xp_earned": 8250,
    "completion_rate": 0.75,
    "current_streak": 7
  }
}
```

### GET /api/challenges/stats
**Description:** Get challenge statistics  
**Response:**
```json
{
  "total_completed": 45,
  "total_xp_earned": 8250,
  "completion_rate": 0.75,
  "favorite_type": "question_marathon",
  "current_streak": 7,
  "longest_streak": 14
}
```

---

## Frontend Components

### DailyChallengesCard
**Location:** Dashboard (prominent placement)  
**Display:**
- 3 challenge cards with progress bars
- Time remaining until reset
- Bonus XP amounts
- Completion checkmarks
- "View All" button

**Visual Design:**
```
┌─────────────────────────────────────┐
│  🎯 Daily Challenges                │
│  Resets in: 14h 23m                 │
├─────────────────────────────────────┤
│  ✅ Answer 10 Questions  [10/10]   │
│     +100 XP  COMPLETED!             │
├─────────────────────────────────────┤
│  📚 Skill Focus: Multiplication     │
│     [3/5] ▓▓▓▓▓░░░░░  60%          │
│     +75 XP                          │
├─────────────────────────────────────┤
│  🔥 Perfect Streak: 5 in a row      │
│     [0/5] ░░░░░░░░░░  0%           │
│     +150 XP                         │
└─────────────────────────────────────┘
```

### ChallengeModal
**Trigger:** Click on challenge card  
**Display:**
- Full challenge details
- Progress visualization
- Tips for completion
- "Start Practicing" button
- Time remaining

### ChallengeCompletionModal
**Trigger:** Challenge completion  
**Display:**
- Celebration animation (confetti)
- Challenge name and difficulty
- XP awarded
- "Next Challenge" button

### ChallengeHistoryPage
**Navigation:** From dashboard  
**Display:**
- Calendar view of past challenges
- Completion statistics
- XP earned over time
- Streak tracking

---

## Challenge Progress Tracking

### Automatic Progress Updates

**Question Marathon:**
- Increment on each correct answer
- Track via SkillPractice component

**Skill Focus:**
- Increment on correct answers for specific skill
- Filter by skill_id

**Perfect Streak:**
- Track consecutive correct answers
- Reset on wrong answer
- Complete when target reached

**Speed Challenge:**
- Track questions answered within time limit
- Start timer on first question
- Complete if target reached before time expires

**Review Master:**
- Increment on review session completion
- Track via ReviewSession component

**Resource Explorer:**
- Increment on video watch completion
- Increment on resource download

### Integration Points

**SkillPractice.jsx:**
```javascript
// After correct answer
if (dailyChallenges.active) {
  updateChallengeProgress('question_marathon', 1);
  if (currentSkill.id === challenge.target_skill_id) {
    updateChallengeProgress('skill_focus', 1);
  }
}
```

**ReviewSession.jsx:**
```javascript
// After review completion
updateChallengeProgress('review_master', 1);
```

**VideoPlayer.jsx:**
```javascript
// On video completion
updateChallengeProgress('resource_explorer', 1);
```

---

## Expiration & Reset Logic

### Challenge Lifecycle

**Creation:** Midnight UTC (or student timezone)  
**Active Period:** 24 hours  
**Expiration:** Automatic status change to 'expired'  
**Cleanup:** Archive expired challenges after 30 days

### Reset Process

1. **Check Time:** Is it past midnight since last generation?
2. **Expire Old:** Mark yesterday's challenges as 'expired'
3. **Generate New:** Create 3 new challenges
4. **Notify Student:** Show "New challenges available!" notification

### Timezone Handling

**Default:** UTC  
**Custom:** Student timezone (if set in profile)  
**Calculation:** Use student's local midnight for reset

---

## Bonus XP Rewards

### XP Amounts by Difficulty

| Challenge Type | Easy | Medium | Hard |
|---------------|------|--------|------|
| Question Marathon | 50 | 100 | 150 |
| Skill Focus | 75 | 125 | 200 |
| Perfect Streak | 100 | 150 | 250 |
| Speed Challenge | 75 | 125 | 200 |
| Review Master | 50 | 100 | 150 |
| Resource Explorer | 30 | 60 | 100 |

**Daily Maximum:** ~425 XP (if all 3 completed at medium difficulty)  
**Monthly Maximum:** ~12,750 XP (30 days × 425 XP)

### XP Award Timing

**Immediate:** XP awarded instantly upon challenge completion  
**Notification:** XP notification shows "+100 XP (Daily Challenge!)"  
**Tracking:** Separate XP transaction type: 'daily_challenge'

---

## Streak Tracking

### Challenge Completion Streaks

**Definition:** Consecutive days with at least 1 challenge completed  
**Tracking:** Separate from login streaks (Step 5.5)  
**Display:** "🔥 7-day challenge streak!"

**Streak Bonuses:**
- 7 days: +50 XP bonus
- 14 days: +100 XP bonus
- 30 days: +250 XP bonus

---

## Notifications

### Challenge Available
**Trigger:** New challenges generated  
**Message:** "🎯 3 new daily challenges available! Earn up to 425 XP today!"

### Challenge Completed
**Trigger:** Challenge completion  
**Message:** "✅ Challenge completed! +100 XP earned!"

### Challenge Expiring Soon
**Trigger:** 2 hours before expiration  
**Message:** "⏰ Daily challenges expire in 2 hours! Complete them now!"

### All Challenges Completed
**Trigger:** All 3 challenges done  
**Message:** "🎉 All daily challenges completed! You earned 425 XP today!"

---

## Gamification Integration

### Achievement Triggers

**"Challenge Accepted":** Complete 1 daily challenge (Bronze, 25 XP)  
**"Daily Grind":** Complete 10 daily challenges (Silver, 50 XP)  
**"Challenge Master":** Complete 50 daily challenges (Gold, 100 XP)  
**"Perfect Day":** Complete all 3 challenges in one day (Silver, 75 XP)  
**"Week Warrior":** Complete challenges 7 days in a row (Gold, 150 XP)

### Leaderboard Addition

**Daily Challenge Leaderboard:**
- Rank by total challenges completed
- Rank by current challenge streak
- Weekly challenge completion race

---

## User Experience Flow

### Morning Login

1. Student logs in
2. System checks: Has it been 24 hours since last challenges?
3. If yes: Generate 3 new challenges
4. Show notification: "New challenges available!"
5. Display challenges on dashboard

### During Practice

1. Student practices skills
2. Progress automatically tracked
3. Progress bar updates in real-time
4. Completion triggers celebration modal
5. XP awarded immediately

### Evening Check

1. Student checks dashboard
2. Sees 2/3 challenges completed
3. Sees "Expires in 3h 15m"
4. Motivated to complete last challenge
5. Completes all 3, earns full bonus XP

---

## Technical Implementation

### Backend Service

**ChallengeService:**
- `generate_daily_challenges(student_id)` - Create 3 new challenges
- `get_active_challenges(student_id)` - Get today's challenges
- `update_progress(challenge_id, increment)` - Update progress
- `check_completion(challenge_id)` - Check if complete, award XP
- `expire_old_challenges()` - Cleanup expired challenges
- `get_challenge_stats(student_id)` - Get statistics

### Automatic Generation

**Cron Job (Optional):**
- Run at midnight UTC
- Generate challenges for all active students
- Alternative: Generate on-demand when student logs in

**On-Demand (Recommended):**
- Check on student login
- Generate if >24 hours since last generation
- More efficient, no wasted challenges

---

## Success Metrics

**Engagement:**
- Daily active users increase
- Average session length increase
- Return rate increase

**Completion:**
- 60%+ of students complete at least 1 challenge daily
- 30%+ complete all 3 challenges
- 15%+ maintain 7+ day streaks

**XP Impact:**
- 10-20% of daily XP from challenges
- Consistent daily practice increase

---

## Future Enhancements

1. **Weekly Challenges:** Longer-term challenges with bigger rewards
2. **Special Event Challenges:** Holiday or themed challenges
3. **Team Challenges:** Collaborative class challenges
4. **Challenge Customization:** Students choose difficulty
5. **Challenge Trading:** Swap challenges with friends
6. **Bonus Multipliers:** Double XP weekends
7. **Challenge Achievements:** Meta-achievements for challenge completion
8. **Challenge Leaderboards:** Compete on challenge completion

---

## Conclusion

The Daily Challenges system adds **urgency**, **routine**, and **variety** to the Alpha Learning Platform. By providing time-limited goals with bonus rewards, we create a compelling reason for students to log in and practice every day.

This feature leverages **loss aversion** (don't miss out on bonus XP!), **goal-setting theory** (clear, achievable targets), and **variable rewards** (different challenges each day) to maximize engagement and motivation.

---

**Next:** Implementation of backend challenge generation and tracking system.

