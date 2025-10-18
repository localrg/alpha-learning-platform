# Step 5.5: Streak Tracking & Rewards - Design Document

**Date:** October 17, 2025  
**Week:** 5 - Engagement & Motivation  
**Step:** 5.5 of 5.5 (Final Step of Week 5!)

---

## Overview

The Streak Tracking system tracks **login streaks** and **practice streaks** to encourage daily engagement and consistency. This is the final piece of the engagement and motivation puzzle, completing Week 5.

---

## Goals

1. **Track Login Streaks:** Consecutive days of logging in
2. **Track Practice Streaks:** Consecutive days of practicing
3. **Reward Consistency:** Bonus XP for streak milestones
4. **Prevent Loss:** Streak freeze/recovery mechanics
5. **Motivate Daily Use:** Visual streak display and celebrations

---

## Streak Types

### 1. Login Streak
**Definition:** Consecutive days with at least one login  
**Tracking:** Update on each login  
**Reset:** Breaks if no login for 24+ hours  

### 2. Practice Streak
**Definition:** Consecutive days with at least 1 question answered correctly  
**Tracking:** Update on each correct answer  
**Reset:** Breaks if no practice for 24+ hours  

---

## Database Schema

### StreakTracking Table
```
id: Integer (PK)
student_id: Integer (FK → students.id)
login_streak: Integer (current login streak)
login_streak_best: Integer (longest ever login streak)
last_login_date: Date (last login day)
practice_streak: Integer (current practice streak)
practice_streak_best: Integer (longest ever practice streak)
last_practice_date: Date (last practice day)
streak_freezes_available: Integer (number of freeze tokens)
created_at: DateTime
updated_at: DateTime
```

---

## Streak Milestones & Rewards

### Login Streak Milestones
- **3 days:** +25 XP
- **7 days:** +75 XP
- **14 days:** +150 XP
- **30 days:** +300 XP
- **100 days:** +1000 XP

### Practice Streak Milestones
- **3 days:** +50 XP
- **7 days:** +100 XP
- **14 days:** +200 XP
- **30 days:** +500 XP
- **100 days:** +1500 XP

---

## API Endpoints

### GET /api/streaks/current
Get current streak status for student

### POST /api/streaks/update-login
Update login streak (called on login)

### POST /api/streaks/update-practice
Update practice streak (called on correct answer)

### GET /api/streaks/stats
Get streak statistics and history

---

## Frontend Components

### StreakDisplay
- Shows current login and practice streaks
- Fire emoji animation (🔥)
- Milestone progress bars
- Best streak display

### StreakCelebration Modal
- Triggers on milestone achievement
- Confetti animation
- XP reward display

---

## Implementation Strategy

**Streamlined Approach:**
- Focus on core streak tracking
- Simple milestone rewards
- Clean UI display
- Essential API endpoints

This completes Week 5! 🎉

