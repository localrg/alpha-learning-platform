# Step 5.2: Achievements & Badges - Design Document

**Date:** October 17, 2025  
**Week:** 5 - Engagement & Motivation  
**Step:** 5.2 of 5.5

---

## Overview

The Achievements & Badges system provides students with specific, measurable goals to work toward beyond XP and levels. Achievements recognize accomplishments across different aspects of learning (quantity, quality, consistency, exploration), while badges serve as visible trophies that students can collect and display.

---

## Design Goals

1. **Clear Goals:** Provide specific targets that guide student behavior
2. **Multiple Paths:** Recognize different types of success (not just completion)
3. **Progressive Difficulty:** Achievements range from beginner to expert
4. **Visible Progress:** Show how close students are to unlocking achievements
5. **Celebration:** Make unlocking achievements feel rewarding
6. **Collection:** Enable students to view and showcase their badges

---

## Achievement Categories

### 1. Practice Achievements (Quantity)
Focus on consistent practice and question completion.

**Achievements:**
- **First Steps** - Answer 10 questions (Bronze)
- **Dedicated Learner** - Answer 100 questions (Silver)
- **Practice Master** - Answer 500 questions (Gold)
- **Question Champion** - Answer 1,000 questions (Platinum)
- **Practice Legend** - Answer 5,000 questions (Diamond)

### 2. Mastery Achievements (Quality)
Focus on skill mastery and deep understanding.

**Achievements:**
- **First Mastery** - Master 1 skill (Bronze)
- **Skill Collector** - Master 5 skills (Silver)
- **Mastery Expert** - Master 10 skills (Gold)
- **Mastery Champion** - Master 25 skills (Platinum)
- **Complete Mastery** - Master 50 skills (Diamond)

### 3. Accuracy Achievements (Precision)
Focus on getting questions right on the first try.

**Achievements:**
- **Sharp Shooter** - 10 first-try correct answers (Bronze)
- **Precision Expert** - 50 first-try correct answers (Silver)
- **Perfect Aim** - 100 first-try correct answers (Gold)
- **Flawless Performer** - 500 first-try correct answers (Platinum)

### 4. Streak Achievements (Consistency)
Focus on consecutive correct answers.

**Achievements:**
- **Hot Streak** - 5 correct answers in a row (Bronze)
- **On Fire** - 10 correct answers in a row (Silver)
- **Unstoppable** - 25 correct answers in a row (Gold)
- **Perfect Streak** - 50 correct answers in a row (Platinum)

### 5. Review Achievements (Retention)
Focus on spaced repetition and review completion.

**Achievements:**
- **Reviewer** - Complete 5 reviews (Bronze)
- **Review Regular** - Complete 25 reviews (Silver)
- **Review Expert** - Complete 100 reviews (Gold)
- **Perfect Reviewer** - 10 perfect reviews (100% correct) (Platinum)

### 6. Learning Achievements (Exploration)
Focus on using learning resources.

**Achievements:**
- **Video Watcher** - Watch 5 videos (Bronze)
- **Resource Explorer** - Download 10 resources (Bronze)
- **Interactive Learner** - Try 10 interactive examples (Bronze)
- **Hint Seeker** - Use hints 25 times (Bronze)
- **Solution Student** - View 50 worked solutions (Silver)

### 7. Time Achievements (Dedication)
Focus on time spent learning.

**Achievements:**
- **Quick Learner** - 1 hour total practice time (Bronze)
- **Dedicated Student** - 10 hours total practice time (Silver)
- **Time Champion** - 50 hours total practice time (Gold)
- **Lifetime Learner** - 100 hours total practice time (Platinum)

### 8. Speed Achievements (Efficiency)
Focus on answering questions quickly.

**Achievements:**
- **Speed Demon** - Answer 10 questions in under 30 seconds each (Silver)
- **Lightning Fast** - Answer 50 questions in under 20 seconds each (Gold)

### 9. Special Achievements (Milestones)
Focus on major platform milestones.

**Achievements:**
- **Welcome Aboard** - Complete first assessment (Bronze)
- **Early Bird** - Log in before 8 AM (Bronze)
- **Night Owl** - Log in after 10 PM (Bronze)
- **Weekend Warrior** - Practice on Saturday and Sunday (Silver)
- **Daily Dedication** - 7-day login streak (Gold)
- **Monthly Master** - 30-day login streak (Platinum)
- **Completionist** - Reach 100% mastery in one grade level (Diamond)

---

## Badge Tiers

**Bronze** - Beginner achievements (easy to unlock)  
**Silver** - Intermediate achievements (moderate difficulty)  
**Gold** - Advanced achievements (challenging)  
**Platinum** - Expert achievements (very challenging)  
**Diamond** - Legendary achievements (extremely rare)

---

## Database Schema

### achievements table
```sql
id                  INTEGER PRIMARY KEY
name                VARCHAR(100) UNIQUE
description         VARCHAR(200)
category            VARCHAR(50)  -- 'practice', 'mastery', 'accuracy', etc.
tier                VARCHAR(20)  -- 'bronze', 'silver', 'gold', 'platinum', 'diamond'
requirement_type    VARCHAR(50)  -- 'count', 'streak', 'percentage', 'time'
requirement_value   INTEGER      -- Target value to unlock
icon_emoji          VARCHAR(10)  -- Emoji icon
xp_reward           INTEGER      -- XP awarded on unlock
is_active           BOOLEAN DEFAULT TRUE
created_at          DATETIME
```

### student_achievements table
```sql
id                  INTEGER PRIMARY KEY
student_id          INTEGER FOREIGN KEY
achievement_id      INTEGER FOREIGN KEY
progress            INTEGER DEFAULT 0
unlocked_at         DATETIME NULL
is_displayed        BOOLEAN DEFAULT FALSE  -- Show on profile
created_at          DATETIME
updated_at          DATETIME
```

### achievement_progress_log table
```sql
id                  INTEGER PRIMARY KEY
student_id          INTEGER FOREIGN KEY
achievement_id      INTEGER FOREIGN KEY
progress_delta      INTEGER
new_progress        INTEGER
description         VARCHAR(200)
created_at          DATETIME
```

---

## Backend Architecture

### Models

**Achievement Model:**
- Stores achievement definitions
- Methods: check_unlock_criteria(), calculate_progress()
- Properties: is_unlockable, progress_percentage

**StudentAchievement Model:**
- Tracks student progress toward achievements
- Methods: update_progress(), unlock(), display()
- Relationships: student, achievement

**AchievementProgressLog Model:**
- Audit trail of progress changes
- Used for analytics and debugging

### Service Layer

**AchievementService:**

Methods:
- `seed_achievements()` - Create all achievement definitions
- `get_student_achievements(student_id)` - Get all achievements with progress
- `update_progress(student_id, achievement_id, delta)` - Increment progress
- `check_and_unlock(student_id, achievement_id)` - Check if unlockable
- `unlock_achievement(student_id, achievement_id)` - Unlock and award XP
- `get_unlocked_achievements(student_id)` - Get all unlocked
- `get_in_progress_achievements(student_id)` - Get close to unlocking
- `get_displayed_achievements(student_id)` - Get profile-displayed badges
- `track_action(student_id, action_type, metadata)` - Update relevant achievements
- `get_achievement_stats(student_id)` - Get summary statistics

### API Endpoints

**GET /api/achievements** - Get all achievement definitions  
**GET /api/achievements/student** - Get student's achievements with progress  
**GET /api/achievements/unlocked** - Get student's unlocked achievements  
**GET /api/achievements/in-progress** - Get achievements close to unlocking  
**GET /api/achievements/displayed** - Get student's displayed badges  
**POST /api/achievements/:id/display** - Toggle badge display on profile  
**GET /api/achievements/stats** - Get achievement statistics  
**POST /api/achievements/seed** - Seed achievement definitions (admin)

---

## Frontend Architecture

### Components

**1. AchievementGrid Component**
- Grid layout of all achievements
- Filter by category and tier
- Show locked/unlocked state
- Progress bars for in-progress
- Click to view details

**2. AchievementCard Component**
- Large emoji icon
- Achievement name and description
- Progress bar (if in progress)
- Unlock date (if unlocked)
- Tier badge (bronze/silver/gold/etc.)
- XP reward display

**3. AchievementModal Component**
- Full details of achievement
- Requirements breakdown
- Progress history
- Tips for unlocking
- Display toggle button

**4. BadgeDisplay Component**
- Compact badge for profile
- Shows only displayed achievements
- Tooltip with details
- Click to manage

**5. AchievementNotification Component**
- Toast notification on unlock
- Animated badge reveal
- Confetti effect
- XP reward display

**6. AchievementProgress Component**
- Summary widget showing:
  - Total achievements unlocked
  - Percentage complete
  - Next achievement to unlock
  - Recent unlocks

---

## Achievement Tracking Logic

### Automatic Tracking

When a student performs an action, the system automatically:

1. **Identifies relevant achievements** based on action type
2. **Updates progress** for each relevant achievement
3. **Checks unlock criteria** for updated achievements
4. **Unlocks achievement** if criteria met
5. **Awards XP reward** from achievement
6. **Triggers notification** to frontend
7. **Logs progress change** for analytics

### Action → Achievement Mapping

| Action | Relevant Achievements |
|--------|----------------------|
| Answer question | Practice, Accuracy (if first-try), Streak (if correct), Speed |
| Master skill | Mastery |
| Complete review | Review, Perfect Reviewer (if 100%) |
| Watch video | Video Watcher |
| Download resource | Resource Explorer |
| Try example | Interactive Learner |
| Use hint | Hint Seeker |
| View solution | Solution Student |
| Login | Daily Dedication, Early Bird, Night Owl |
| Practice time | Time achievements |

---

## UI/UX Design

### Achievement Grid Layout

```
┌─────────────────────────────────────────────┐
│  Achievements (24/45 unlocked - 53%)        │
│                                             │
│  [All] [Practice] [Mastery] [Accuracy] ... │
│                                             │
│  ┌────────┐ ┌────────┐ ┌────────┐          │
│  │  🏆    │ │  🔒    │ │  ⭐    │          │
│  │ First  │ │ Skill  │ │ Sharp  │          │
│  │ Steps  │ │Collect │ │Shooter │          │
│  │ ✓      │ │ 3/5    │ │ 7/10   │          │
│  │ BRONZE │ │ SILVER │ │ BRONZE │          │
│  └────────┘ └────────┘ └────────┘          │
│                                             │
│  ... more achievements ...                  │
└─────────────────────────────────────────────┘
```

### Achievement Card States

**Locked (Not Started):**
- Grayscale colors
- Lock icon 🔒
- "0/100" progress
- Grayed out description

**In Progress:**
- Partial color
- Progress bar
- "47/100" progress
- Motivational text

**Unlocked:**
- Full color
- Checkmark ✓
- Unlock date
- "Display on Profile" toggle

**Displayed:**
- Full color
- Star icon ⭐
- "Displayed" badge
- Shown on student profile

### Color Scheme

**Bronze:** #CD7F32 (copper brown)  
**Silver:** #C0C0C0 (metallic silver)  
**Gold:** #FFD700 (bright gold)  
**Platinum:** #E5E4E2 (platinum white)  
**Diamond:** #B9F2FF (light blue)

---

## Gamification Psychology

### Goal-Setting Theory

**Specific Goals:** Each achievement has clear, measurable criteria.

**Challenging but Attainable:** Tiered achievements provide goals for all skill levels.

**Feedback:** Progress bars show exactly how close students are to unlocking.

### Collection Mechanics

**Completionism:** Students motivated to "collect them all."

**Rarity:** Diamond achievements are prestigious and rare.

**Display:** Showing badges on profile provides social recognition.

### Progress Principle

**Small Wins:** Bronze achievements unlock quickly for early motivation.

**Visible Progress:** Progress bars make abstract goals concrete.

**Celebration:** Unlock notifications celebrate each achievement.

---

## Integration with Existing Systems

### Gamification System
- Achievements award XP when unlocked
- Achievement unlocks trigger XP notifications
- Leaderboard can show achievement count

### Student Profile
- Display selected badges on profile
- Show achievement statistics
- Achievement showcase section

### Progress Dashboard
- Show recent achievement unlocks
- Display next achievements to unlock
- Achievement progress widgets

---

## Success Metrics

**Engagement:**
- % of students who unlock at least 1 achievement
- Average achievements per student
- Time to first achievement unlock

**Motivation:**
- Increase in practice time after achievement unlock
- % of students actively working toward achievements
- Achievement display rate

**Retention:**
- % of students who return after unlocking achievement
- Correlation between achievements and retention

---

## Future Enhancements

1. **Secret Achievements** - Hidden until unlocked
2. **Seasonal Achievements** - Limited-time special achievements
3. **Social Achievements** - Collaborative achievements
4. **Achievement Chains** - Multi-step progressive achievements
5. **Custom Achievements** - Teachers create custom achievements
6. **Achievement Leaderboard** - Rank by total achievements
7. **Badge Rarity** - Show % of students who have each badge
8. **Achievement Notifications** - Email/push when close to unlocking

---

## Implementation Plan

### Phase 1: Backend (Current)
- Create database models
- Implement achievement service
- Build API endpoints
- Seed achievement definitions
- Add automatic tracking

### Phase 2: Frontend
- Build achievement grid component
- Create achievement cards
- Implement unlock notifications
- Add profile badge display
- Build progress widgets

### Phase 3: Integration
- Connect to existing actions
- Add tracking to all relevant endpoints
- Test unlock flow
- Verify XP awards

### Phase 4: Testing
- Test all achievement types
- Verify progress tracking
- Test unlock criteria
- Check notification flow
- Validate XP rewards

---

## Technical Considerations

**Performance:**
- Index student_achievements on student_id and achievement_id
- Cache achievement definitions
- Batch progress updates
- Async notification delivery

**Scalability:**
- Achievements checked only on relevant actions
- Progress updates use delta increments
- Unlock checks use database queries

**Data Integrity:**
- Prevent duplicate unlocks
- Validate progress values
- Ensure atomic unlock operations

---

This design provides a comprehensive achievement system that motivates students through clear goals, celebrates accomplishments, and creates a sense of progression beyond XP and levels.

