# Step 4.1: Video Tutorial Integration - Design Document

**Date:** October 17, 2025  
**Status:** 🔄 In Progress  
**Week:** 4 - Content & Resources

---

## Overview

Step 4.1 implements a comprehensive video tutorial system that provides instructional videos for each skill. This supports visual learners and provides students with clear, engaging explanations before they practice skills.

The system will support multiple video sources (YouTube, Vimeo, direct uploads) and provide a seamless viewing experience integrated into the learning workflow.

---

## Goals

### Primary Goals
1. Enable video content for each skill
2. Support multiple video platforms (YouTube, Vimeo, direct)
3. Provide seamless video playback experience
4. Track video viewing progress
5. Integrate videos into practice workflow

### Secondary Goals
1. Support multiple videos per skill
2. Track video completion
3. Provide video recommendations
4. Enable video playlists
5. Support captions/transcripts

---

## System Architecture

### Components

```
┌─────────────────────────────────────────────────────────┐
│                    Video Tutorial System                 │
├─────────────────────────────────────────────────────────┤
│                                                           │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │   Database   │  │   Backend    │  │   Frontend   │  │
│  │              │  │              │  │              │  │
│  │ • VideoTutorial│ │ • VideoService│ │ • VideoPlayer│  │
│  │ • VideoView  │  │ • API Routes │  │ • TutorialList│ │
│  │ • Skill      │  │ • Embed Logic│  │ • Integration│  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
│                                                           │
└─────────────────────────────────────────────────────────┘
```

---

## Database Schema

### New Table: VideoTutorial

```python
class VideoTutorial(db.Model):
    id = Integer (Primary Key)
    skill_id = Integer (Foreign Key -> skills.id)
    
    # Video information
    title = String(200)
    description = Text
    video_url = String(500)  # YouTube, Vimeo, or direct URL
    video_platform = String(20)  # 'youtube', 'vimeo', 'direct'
    video_id = String(100)  # Platform-specific video ID
    duration_seconds = Integer
    thumbnail_url = String(500)
    
    # Metadata
    difficulty_level = String(20)  # 'beginner', 'intermediate', 'advanced'
    sequence_order = Integer  # Order within skill
    is_active = Boolean (default=True)
    
    # Timestamps
    created_at = DateTime
    updated_at = DateTime
```

### New Table: VideoView

```python
class VideoView(db.Model):
    id = Integer (Primary Key)
    student_id = Integer (Foreign Key -> students.id)
    video_id = Integer (Foreign Key -> video_tutorials.id)
    
    # Viewing progress
    watch_time_seconds = Integer  # Total time watched
    completed = Boolean  # Watched to end
    completion_percentage = Float  # % of video watched
    
    # Timestamps
    started_at = DateTime
    last_watched_at = DateTime
    completed_at = DateTime (nullable)
```

### Enhanced: Skill Model

```python
# Add to existing Skill model
video_tutorial_count = Integer (default=0)
has_video = Boolean (default=False)
```

---

## Video Platform Support

### YouTube Integration
- **URL Format:** `https://www.youtube.com/watch?v=VIDEO_ID`
- **Embed Format:** `https://www.youtube.com/embed/VIDEO_ID`
- **Features:** Auto-play control, quality selection, captions
- **API:** YouTube Data API v3 (for metadata)

### Vimeo Integration
- **URL Format:** `https://vimeo.com/VIDEO_ID`
- **Embed Format:** `https://player.vimeo.com/video/VIDEO_ID`
- **Features:** Privacy controls, custom player colors
- **API:** Vimeo API (for metadata)

### Direct Video
- **Supported Formats:** MP4, WebM, OGG
- **Storage:** Cloud storage (S3, CloudFlare R2)
- **Features:** HTML5 video player with controls
- **Fallback:** Multiple format support for compatibility

---

## API Endpoints

### Video Management

#### GET `/api/videos/skill/<skill_id>`
Get all videos for a specific skill.

**Response:**
```json
{
  "videos": [
    {
      "id": 1,
      "title": "Introduction to Multiplication",
      "description": "Learn the basics...",
      "video_url": "https://youtube.com/...",
      "platform": "youtube",
      "duration": 180,
      "thumbnail_url": "https://...",
      "difficulty": "beginner",
      "watched": false,
      "completion_percentage": 0
    }
  ],
  "total_videos": 1
}
```

#### GET `/api/videos/<video_id>`
Get details for a specific video.

#### POST `/api/videos/<video_id>/start`
Record that a student started watching a video.

**Request:**
```json
{
  "student_id": 1
}
```

#### PUT `/api/videos/<video_id>/progress`
Update viewing progress.

**Request:**
```json
{
  "watch_time_seconds": 120,
  "completion_percentage": 66.7
}
```

#### POST `/api/videos/<video_id>/complete`
Mark video as completed.

---

## Frontend Components

### VideoPlayer Component

**Purpose:** Embedded video player with platform detection

**Features:**
- Automatic platform detection (YouTube/Vimeo/Direct)
- Responsive iframe/video element
- Progress tracking
- Play/pause controls
- Fullscreen support
- Loading states

**Props:**
```javascript
{
  videoUrl: string,
  platform: 'youtube' | 'vimeo' | 'direct',
  onStart: () => void,
  onProgress: (percentage: number) => void,
  onComplete: () => void
}
```

### TutorialList Component

**Purpose:** Display list of videos for a skill

**Features:**
- Video cards with thumbnails
- Duration display
- Watched/unwatched indicators
- Difficulty badges
- Click to play

### SkillVideoSection Component

**Purpose:** Integrated video section in skill practice

**Features:**
- "Watch Tutorial" button
- Collapsible video player
- Multiple video tabs (if multiple videos)
- Progress indicators

---

## User Workflows

### Workflow 1: Watch Before Practice

1. Student navigates to skill practice
2. Sees "Watch Tutorial" button at top
3. Clicks to expand video section
4. Watches instructional video
5. Video completion tracked automatically
6. Proceeds to practice questions

### Workflow 2: Watch During Practice

1. Student struggles with practice questions
2. Clicks "Need Help?" button
3. Video tutorial appears
4. Watches relevant section
5. Returns to practice with better understanding

### Workflow 3: Browse Tutorials

1. Student visits skill page
2. Sees "Tutorials" tab
3. Views list of available videos
4. Selects video by difficulty level
5. Watches and tracks progress

---

## Video Content Strategy

### Content Types

1. **Introduction Videos** (2-3 minutes)
   - Skill overview
   - Real-world applications
   - What students will learn

2. **Instructional Videos** (5-8 minutes)
   - Step-by-step explanations
   - Worked examples
   - Common mistakes to avoid

3. **Advanced Videos** (3-5 minutes)
   - Advanced techniques
   - Problem-solving strategies
   - Challenge problems

### Video Quality Standards

- **Resolution:** Minimum 720p (1080p preferred)
- **Audio:** Clear narration, no background noise
- **Visuals:** Clear text, diagrams, animations
- **Length:** 2-8 minutes (attention span optimized)
- **Pacing:** Appropriate for grade level
- **Captions:** Available for accessibility

---

## Video URL Parsing

### YouTube URL Patterns

```python
# Standard watch URL
https://www.youtube.com/watch?v=VIDEO_ID

# Short URL
https://youtu.be/VIDEO_ID

# Embed URL
https://www.youtube.com/embed/VIDEO_ID

# Extract VIDEO_ID from any format
```

### Vimeo URL Patterns

```python
# Standard URL
https://vimeo.com/VIDEO_ID

# Player URL
https://player.vimeo.com/video/VIDEO_ID

# Extract VIDEO_ID
```

---

## Progress Tracking

### Tracking Metrics

1. **Watch Time** - Total seconds watched
2. **Completion Percentage** - % of video viewed
3. **Completion Status** - Boolean (watched to end)
4. **View Count** - Number of times started
5. **Last Watched** - Timestamp of last view

### Completion Criteria

- Video considered "completed" when:
  - Watch time ≥ 90% of duration, OR
  - Student explicitly marks as complete

### Analytics

- Most watched videos
- Average completion rate
- Videos with high replay rate
- Videos correlated with mastery

---

## Integration Points

### With Skill Practice

- Video button in practice header
- "Watch Tutorial First" recommendation for new skills
- "Need Help?" button shows video during practice
- Video completion tracked in progress

### With Learning Path

- Video icon on skills with tutorials
- "Watch Video" CTA on skill cards
- Video completion as optional milestone
- Recommended videos in learning path

### With Progress Dashboard

- Videos watched count
- Video completion percentage
- Time spent watching tutorials
- Video recommendations

---

## Technical Implementation

### Backend Service Layer

```python
class VideoService:
    @staticmethod
    def parse_video_url(url):
        """Parse video URL and extract platform and ID."""
        
    @staticmethod
    def get_videos_for_skill(skill_id, student_id):
        """Get all videos for a skill with student progress."""
        
    @staticmethod
    def start_video_view(video_id, student_id):
        """Record video view start."""
        
    @staticmethod
    def update_video_progress(view_id, watch_time, percentage):
        """Update viewing progress."""
        
    @staticmethod
    def complete_video(view_id):
        """Mark video as completed."""
```

### Frontend Video Player

```javascript
// YouTube Player
<iframe
  src={`https://www.youtube.com/embed/${videoId}`}
  allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
  allowFullScreen
/>

// Vimeo Player
<iframe
  src={`https://player.vimeo.com/video/${videoId}`}
  allow="autoplay; fullscreen; picture-in-picture"
  allowFullScreen
/>

// Direct Video
<video controls>
  <source src={videoUrl} type="video/mp4" />
  Your browser does not support the video tag.
</video>
```

---

## Sample Video Data

### Example Videos for Skills

**Skill: Basic Multiplication**
- Video 1: "Introduction to Multiplication" (3 min, beginner)
- Video 2: "Multiplication Strategies" (6 min, intermediate)
- Video 3: "Mental Math Tricks" (4 min, advanced)

**Skill: Fractions**
- Video 1: "What are Fractions?" (4 min, beginner)
- Video 2: "Adding Fractions" (7 min, intermediate)
- Video 3: "Fraction Word Problems" (5 min, advanced)

---

## Security & Privacy

### Video Content
- All videos reviewed for age-appropriateness
- No external ads or tracking in embedded players
- Privacy-enhanced mode for YouTube embeds
- Vimeo privacy settings configured

### Data Privacy
- Video viewing data stored securely
- No sharing of student viewing data
- COPPA compliant tracking
- Parent access to viewing history

---

## Performance Considerations

### Video Loading
- Lazy loading for video embeds
- Thumbnail preloading
- Progressive enhancement
- Fallback for slow connections

### Bandwidth
- Adaptive quality for YouTube/Vimeo
- Video compression for direct uploads
- CDN delivery for hosted videos
- Mobile-optimized streaming

---

## Accessibility

### Video Accessibility
- Captions/subtitles required
- Transcript available
- Audio descriptions (where applicable)
- Keyboard controls for player

### UI Accessibility
- Screen reader compatible
- ARIA labels on controls
- High contrast mode support
- Focus indicators

---

## Future Enhancements

### Phase 2 Features
1. **Interactive Videos** - Embedded quizzes in videos
2. **Video Playlists** - Curated learning sequences
3. **User-Generated Content** - Student explanation videos
4. **Live Tutoring** - Real-time video sessions
5. **Video Notes** - Student annotations and bookmarks

### Phase 3 Features
1. **AI-Generated Summaries** - Key points from videos
2. **Personalized Recommendations** - ML-based suggestions
3. **Video Search** - Search within video content
4. **Multi-language Support** - Translated videos
5. **Offline Viewing** - Downloaded videos for mobile

---

## Success Metrics

### Engagement Metrics
- % of students watching videos
- Average watch time per video
- Video completion rate
- Videos per skill practiced

### Learning Outcomes
- Correlation between video watching and mastery
- Time to mastery with vs without videos
- Student satisfaction with video quality
- Parent/teacher feedback

### Content Metrics
- Most popular videos
- Videos with highest completion
- Videos with most replays
- Videos needing improvement

---

## Implementation Plan

### Phase 1: Core System (This Step)
1. Database schema and models
2. Video URL parsing and embedding
3. Basic video player component
4. API endpoints for video management
5. Integration with skill practice

### Phase 2: Enhanced Features (Future)
1. Progress tracking and analytics
2. Video recommendations
3. Multiple videos per skill
4. Video playlists

### Phase 3: Advanced Features (Future)
1. Interactive elements
2. User-generated content
3. Live sessions
4. Advanced analytics

---

## Technical Requirements

### Backend
- Python 3.11+
- Flask 3.0+
- SQLAlchemy 2.0+
- URL parsing library (urllib)

### Frontend
- React 18+
- Video player library (react-player)
- Responsive iframe handling
- Progress tracking hooks

### External Services
- YouTube Data API (optional, for metadata)
- Vimeo API (optional, for metadata)
- Cloud storage (for direct uploads)

---

## Conclusion

The video tutorial system will significantly enhance the learning experience by providing visual instruction before and during practice. This supports multiple learning styles and helps students understand concepts more deeply before attempting practice problems.

The system is designed to be flexible (supporting multiple platforms), scalable (handling many videos), and integrated (seamlessly fitting into the learning workflow).

---

**Next Steps:**
1. Implement database models
2. Create video service layer
3. Build API endpoints
4. Develop frontend components
5. Test and integrate

