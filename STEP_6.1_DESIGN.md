# Step 6.1: Student Profiles - Design Document

**Date:** October 17, 2025  
**Week:** 6 - Collaboration & Social Features  
**Step:** 6.1 of 6.5

---

## Overview

The Student Profile system creates comprehensive, viewable profiles that showcase each student's learning journey, achievements, and personality. This enables social features and allows students to express their identity.

---

## Goals

1. **Showcase Progress:** Display stats, achievements, badges
2. **Express Identity:** Avatar, bio, favorite subjects
3. **Enable Social Features:** Public profiles for friends/classmates
4. **Privacy Control:** Settings for what to share
5. **Motivation:** Visible accomplishments create pride

---

## Profile Components

### Basic Information
- Name
- Grade level
- Avatar (emoji or uploaded image)
- Bio (short description)
- Join date

### Statistics
- Current level and XP
- Total questions answered
- Skills mastered
- Current streaks
- Best streaks
- Achievements unlocked

### Achievements Display
- Featured badges (top 3-6)
- Total achievement count
- Rarest achievements highlighted

### Activity
- Recent practice sessions
- Recent achievements
- Streak milestones

---

## Database Schema

### Profile Settings (extend Student model)
```
bio: Text (short description)
avatar: String (emoji or image URL)
profile_visibility: String (public, friends, private)
show_stats: Boolean
show_achievements: Boolean
show_activity: Boolean
```

---

## API Endpoints

### GET /api/profiles/:student_id
Get public profile for a student

### PUT /api/profiles/me
Update own profile settings

### GET /api/profiles/me/stats
Get detailed stats for own profile

---

## Frontend Components

### ProfilePage
- Full profile view with all sections
- Responsive design
- Tab-based navigation (Stats, Achievements, Activity)

### ProfileCard (Mini)
- Compact profile display
- Used in leaderboards, friend lists
- Shows avatar, name, level, top badge

---

## Privacy Settings

**Profile Visibility:**
- Public: Anyone can view
- Friends: Only friends can view
- Private: Only self can view

**Stat Visibility:**
- Toggle for showing detailed stats
- Toggle for showing achievements
- Toggle for showing activity

---

## Implementation Strategy

**Streamlined Approach:**
- Extend existing Student model
- Focus on essential profile features
- Clean, professional UI
- Privacy-first design

This enables Week 6 social features! 🎉

