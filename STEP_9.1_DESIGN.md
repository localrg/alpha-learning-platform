# Step 9.1: Learning Analytics Dashboard - Design Document

## Overview

Step 9.1 implements a comprehensive learning analytics dashboard that provides visual insights into learning patterns, performance trends, and engagement metrics for students, teachers, and administrators.

## Goals

1. Provide visual analytics for learning data
2. Enable trend analysis and pattern detection
3. Support data-driven decision making
4. Offer comparative analytics (student vs cohort)
5. Create actionable insights from raw data

## Features

### 1. Student Analytics Dashboard
**Metrics:**
- Learning velocity (skills mastered per week)
- Practice consistency (sessions per week)
- Performance trends (accuracy over time)
- Time investment (total practice time)
- Engagement score (composite metric)

**Visualizations:**
- Practice time chart (last 30 days)
- Accuracy trend line (last 30 days)
- Skills mastered timeline
- Subject area distribution (pie chart)
- Session length distribution (histogram)

### 2. Teacher Analytics Dashboard
**Class-Level Metrics:**
- Average class performance
- Student distribution (on-track, needs-practice, struggling)
- Assignment completion rates
- Engagement trends
- At-risk student count

**Visualizations:**
- Class performance heatmap (students x skills)
- Engagement trend (last 8 weeks)
- Assignment completion funnel
- Student status distribution (pie chart)
- Top/bottom performers comparison

### 3. Comparative Analytics
**Comparisons:**
- Student vs class average
- Student vs grade level average
- Class vs other classes (same grade)
- Current period vs previous period
- Actual vs expected performance

### 4. Engagement Analytics
**Metrics:**
- Daily active users (DAU)
- Weekly active users (WAU)
- Session frequency
- Session duration
- Feature usage (which features used most)
- Retention rate

## Technical Design

### Analytics Service

**AnalyticsDashboardService:**
- `get_student_dashboard(student_id, days=30)` - Student analytics
- `get_teacher_dashboard(teacher_id, class_id=None)` - Teacher analytics
- `get_comparative_analytics(student_id, comparison_type)` - Comparisons
- `get_engagement_metrics(entity_type, entity_id, days=30)` - Engagement
- `calculate_learning_velocity(student_id, days=30)` - Skills/week
- `calculate_engagement_score(student_id, days=30)` - Composite score
- `get_performance_distribution(class_id)` - Student distribution
- `get_skill_heatmap(class_id)` - Class x skill heatmap

### API Endpoints

**Student Analytics:**
- `GET /api/analytics/student/<id>/dashboard` - Student dashboard
- `GET /api/analytics/student/<id>/trends` - Trend data
- `GET /api/analytics/student/<id>/comparative` - Comparisons

**Teacher Analytics:**
- `GET /api/analytics/teacher/<id>/dashboard` - Teacher dashboard
- `GET /api/analytics/class/<id>/performance` - Class performance
- `GET /api/analytics/class/<id>/heatmap` - Skill heatmap

**Engagement Analytics:**
- `GET /api/analytics/engagement/student/<id>` - Student engagement
- `GET /api/analytics/engagement/class/<id>` - Class engagement
- `GET /api/analytics/platform/metrics` - Platform-wide metrics

### Data Aggregation

**Metrics Calculation:**
- Learning velocity: skills mastered / weeks
- Engagement score: weighted average of (sessions, time, accuracy, streak)
- Performance trend: linear regression on accuracy over time
- Consistency score: days with practice / total days
- At-risk detection: accuracy < 60% OR no practice in 7 days

**Aggregation Periods:**
- Last 7 days (week)
- Last 30 days (month)
- Last 90 days (quarter)
- Custom date range

## Implementation Plan

1. Create AnalyticsDashboardService with metric calculations
2. Implement trend analysis algorithms
3. Create API routes for analytics endpoints
4. Add comparative analytics logic
5. Test all analytics calculations

## Success Metrics

- 80% of teachers use analytics dashboard weekly
- 60% of students view their own analytics
- 90% find analytics insights useful
- Average time on analytics: 5 minutes per session
- Analytics-driven interventions increase 40%

---

**Next Step:** Implement service and routes, then create tests.

