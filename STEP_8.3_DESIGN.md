# Step 8.3: Activity Reports - Design Document

## Overview

Step 8.3 implements comprehensive activity reports for parents, providing detailed insights into their child's learning patterns, progress trends, and performance analytics over time. Reports include data visualizations, trend analysis, and export capabilities.

## Goals

1. Provide detailed reports on child learning activity
2. Show trends and patterns over time (weekly, monthly)
3. Generate insights and recommendations
4. Support report export (PDF, CSV)
5. Enable data-driven parent-child conversations

## Features

### 1. Weekly Progress Report
**Purpose:** Summary of the past week's activity

**Metrics:**
- Total practice time
- Questions answered (total, correct, accuracy)
- Skills practiced (count, list)
- Assignments completed
- Achievements earned
- Streak maintenance
- Day-by-day activity breakdown

**Insights:**
- Most active day
- Best performance day (accuracy)
- Improvement areas
- Comparison to previous week

### 2. Monthly Progress Report
**Purpose:** Comprehensive monthly summary

**Metrics:**
- Total practice time and sessions
- Questions answered and accuracy trend
- Skills mastered this month
- Assignment completion rate
- Level/XP gained
- Achievements earned
- Week-by-week breakdown

**Insights:**
- Progress trajectory (improving, stable, declining)
- Consistency score (practice frequency)
- Top skills by time spent
- Areas needing attention

### 3. Skill Performance Report
**Purpose:** Detailed analysis of skill-level performance

**Data:**
- All skills with current accuracy
- Mastery status and dates
- Time spent per skill
- Questions answered per skill
- Progress trend (improving, stable, declining)
- Prerequisite skill completion

**Visualizations:**
- Skill accuracy heatmap
- Mastery timeline
- Time distribution pie chart

### 4. Time Analysis Report
**Purpose:** Understanding practice patterns and habits

**Data:**
- Total time by day of week
- Total time by time of day (morning, afternoon, evening)
- Average session duration
- Session frequency
- Longest/shortest sessions
- Practice consistency score

**Visualizations:**
- Time by day bar chart
- Session duration histogram
- Practice calendar heatmap

### 5. Comparison Report
**Purpose:** Compare current period to previous period

**Comparisons:**
- This week vs last week
- This month vs last month
- Current accuracy vs previous period
- Practice time change
- Skills mastered change

**Metrics:**
- Percentage changes
- Trend indicators (up, down, stable)
- Insights on improvements or declines

## Technical Design

### Backend Components

#### 1. ReportService
**Location:** `backend/src/services/report_service.py`

**Methods:**
```python
class ReportService:
    @staticmethod
    def generate_weekly_report(parent_id, student_id, week_offset=0)
    
    @staticmethod
    def generate_monthly_report(parent_id, student_id, month_offset=0)
    
    @staticmethod
    def generate_skill_report(parent_id, student_id)
    
    @staticmethod
    def generate_time_analysis(parent_id, student_id, days=30)
    
    @staticmethod
    def generate_comparison_report(parent_id, student_id, period='week')
    
    @staticmethod
    def export_report_pdf(report_data, report_type)
    
    @staticmethod
    def export_report_csv(report_data, report_type)
    
    @staticmethod
    def _calculate_insights(data, report_type)
    
    @staticmethod
    def _calculate_trends(current, previous)
    
    @staticmethod
    def _get_date_range(period, offset=0)
```

#### 2. API Routes
**Location:** `backend/src/routes/report_routes.py`

**Endpoints:**
- `GET /api/parent/children/<id>/reports/weekly` - Weekly report
  - Query params: `week_offset` (default: 0 for current week)
- `GET /api/parent/children/<id>/reports/monthly` - Monthly report
  - Query params: `month_offset` (default: 0 for current month)
- `GET /api/parent/children/<id>/reports/skills` - Skill performance report
- `GET /api/parent/children/<id>/reports/time-analysis` - Time analysis
  - Query params: `days` (default: 30)
- `GET /api/parent/children/<id>/reports/comparison` - Comparison report
  - Query params: `period` (week|month)
- `POST /api/parent/children/<id>/reports/export` - Export report
  - Body: `{report_type, format, data}`

### Data Structures

#### Weekly Report Response
```json
{
  "success": true,
  "report": {
    "period": {
      "start_date": "2025-10-14",
      "end_date": "2025-10-20",
      "week_number": 42
    },
    "summary": {
      "total_time_minutes": 180,
      "total_sessions": 12,
      "questions_answered": 150,
      "questions_correct": 135,
      "accuracy": 0.90,
      "skills_practiced": 5,
      "assignments_completed": 2,
      "achievements_earned": 1,
      "streak_maintained": true
    },
    "daily_breakdown": [
      {
        "date": "2025-10-14",
        "time_minutes": 25,
        "sessions": 2,
        "questions": 20,
        "accuracy": 0.85
      }
    ],
    "skills_practiced": [
      {
        "skill_name": "Addition",
        "time_minutes": 45,
        "questions": 50,
        "accuracy": 0.92
      }
    ],
    "insights": {
      "most_active_day": "Monday",
      "best_performance_day": "Wednesday",
      "improvement_areas": ["Fractions"],
      "comparison_to_last_week": {
        "time_change_percent": 15,
        "accuracy_change": 0.03,
        "trend": "improving"
      }
    }
  }
}
```

#### Skill Report Response
```json
{
  "success": true,
  "report": {
    "total_skills": 15,
    "mastered": 8,
    "in_progress": 5,
    "not_started": 2,
    "skills": [
      {
        "skill_name": "Addition",
        "category": "arithmetic",
        "accuracy": 0.95,
        "mastery_status": "mastered",
        "time_spent_minutes": 120,
        "questions_answered": 150,
        "mastered_date": "2025-10-07",
        "trend": "stable"
      }
    ],
    "insights": {
      "top_skills": ["Addition", "Subtraction"],
      "needs_attention": ["Fractions"],
      "recent_mastery": ["Multiplication"],
      "time_distribution": {
        "arithmetic": 60,
        "fractions": 25,
        "geometry": 15
      }
    }
  }
}
```

#### Time Analysis Response
```json
{
  "success": true,
  "report": {
    "period_days": 30,
    "total_time_minutes": 600,
    "total_sessions": 45,
    "average_session_minutes": 13.3,
    "by_day_of_week": {
      "Monday": 120,
      "Tuesday": 90,
      "Wednesday": 100,
      "Thursday": 85,
      "Friday": 95,
      "Saturday": 60,
      "Sunday": 50
    },
    "by_time_of_day": {
      "morning": 180,
      "afternoon": 300,
      "evening": 120
    },
    "session_stats": {
      "longest_session_minutes": 35,
      "shortest_session_minutes": 5,
      "median_session_minutes": 12
    },
    "consistency_score": 0.85,
    "insights": {
      "most_productive_day": "Monday",
      "preferred_time": "afternoon",
      "consistency_rating": "excellent",
      "recommendation": "Current practice schedule is working well"
    }
  }
}
```

## Report Generation Logic

### Weekly Report
1. Get date range (Monday-Sunday for specified week)
2. Query all sessions in date range
3. Aggregate metrics (time, questions, accuracy)
4. Get skills practiced with individual stats
5. Get assignments completed
6. Get achievements earned
7. Check streak maintenance
8. Calculate daily breakdown
9. Generate insights by comparing to previous week
10. Return formatted report

### Monthly Report
1. Get date range (1st to last day of month)
2. Query all sessions in month
3. Aggregate monthly totals
4. Calculate week-by-week breakdown (4-5 weeks)
5. Get skills mastered this month
6. Get level/XP gained
7. Calculate assignment completion rate
8. Generate trend analysis (improving/stable/declining)
9. Calculate consistency score
10. Return formatted report

### Skill Report
1. Get all learning paths for student
2. For each skill, calculate:
   - Current accuracy
   - Total time spent
   - Questions answered
   - Mastery status and date
   - Trend (compare recent vs overall accuracy)
3. Group by category
4. Calculate time distribution
5. Identify top skills and needs attention
6. Return formatted report

### Time Analysis
1. Get all sessions in specified period
2. Group by day of week and sum time
3. Group by time of day (morning/afternoon/evening)
4. Calculate session statistics (avg, min, max, median)
5. Calculate consistency score based on:
   - Practice frequency (days with practice / total days)
   - Session regularity (variance in session times)
6. Generate insights and recommendations
7. Return formatted report

### Comparison Report
1. Get current period data (week or month)
2. Get previous period data
3. Calculate changes:
   - Time change (absolute and percentage)
   - Accuracy change
   - Skills mastered change
   - Assignment completion change
4. Determine trend (improving/stable/declining)
5. Generate insights on changes
6. Return formatted comparison

## Export Functionality

### PDF Export
- Use ReportLab or WeasyPrint
- Professional formatting with headers/footers
- Include charts as images
- Branded with platform logo
- Date range and student name in header
- Page numbers

### CSV Export
- Tabular data format
- Headers for all columns
- One row per data point
- Suitable for Excel import
- Include metadata in first rows

## Insights Generation

### Automated Insights
The system generates insights based on data patterns:

**Practice Patterns:**
- "Most active on Mondays" (highest time)
- "Prefers afternoon practice" (most sessions)
- "Excellent consistency" (practices 6+ days/week)

**Performance Patterns:**
- "Improving trend" (accuracy increasing)
- "Strong in arithmetic" (high accuracy category)
- "Needs practice in fractions" (low accuracy)

**Comparisons:**
- "15% more practice time than last week"
- "Accuracy improved by 3 points"
- "Mastered 2 new skills this month"

**Recommendations:**
- "Current schedule is working well - keep it up!"
- "Consider more practice in fractions"
- "Great improvement - celebrate progress!"

## Success Metrics

### For Parents
- 60% of parents view reports monthly
- 40% of parents export reports
- 80% find reports useful (survey)
- 50% discuss reports with child

### For Platform
- Increased parent engagement
- Higher perceived value
- Better retention
- Reduced "how is my child doing?" support tickets

## Implementation Plan

1. **Phase 1:** ReportService with all report generation methods
2. **Phase 2:** API routes for all report types
3. **Phase 3:** Export functionality (PDF, CSV)
4. **Phase 4:** Testing with comprehensive test suite
5. **Phase 5:** Documentation and completion report

## Testing Strategy

### Unit Tests
- Test each report generation method
- Test date range calculations
- Test insight generation
- Test trend calculations
- Test export functions

### Integration Tests
- Test API endpoints
- Test authorization
- Test with real data
- Test edge cases (no data, single session)
- Test export formats

### Test Coverage
- All report types
- All time periods
- All export formats
- Authorization checks
- Error handling

## Notes

- Reports are generated on-demand (not pre-computed)
- Cache results for 1 hour to reduce database load
- All reports require parent-child link verification
- Export files are temporary (deleted after download)
- Insights are rule-based (not ML, for now)
- Charts are generated server-side for PDF export
- CSV exports are raw data without charts

---

**Next Step:** Implement ReportService and API routes, then create comprehensive tests.

