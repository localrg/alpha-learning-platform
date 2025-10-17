import { useState, useEffect } from 'react';
import axios from 'axios';
import VideoPlayer from './VideoPlayer';
import './TutorialList.css';

const TutorialList = ({ skillId, skillName }) => {
  const [videos, setVideos] = useState([]);
  const [selectedVideo, setSelectedVideo] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (skillId) {
      fetchVideos();
    }
  }, [skillId]);

  const fetchVideos = async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem('token');
      const config = { headers: { Authorization: `Bearer ${token}` } };

      const response = await axios.get(
        `http://localhost:5000/api/videos/skill/${skillId}`,
        config
      );

      setVideos(response.data.videos || []);
      
      // Auto-select first video if available
      if (response.data.videos && response.data.videos.length > 0) {
        setSelectedVideo(response.data.videos[0]);
      }
      
      setLoading(false);
    } catch (err) {
      console.error('Error fetching videos:', err);
      setError('Failed to load videos');
      setLoading(false);
    }
  };

  const handleVideoStart = async () => {
    if (!selectedVideo) return;

    try {
      const token = localStorage.getItem('token');
      const config = { headers: { Authorization: `Bearer ${token}` } };

      await axios.post(
        `http://localhost:5000/api/videos/${selectedVideo.id}/start`,
        {},
        config
      );
    } catch (err) {
      console.error('Error starting video:', err);
    }
  };

  const handleVideoProgress = async (watchTime, percentage) => {
    if (!selectedVideo) return;

    try {
      const token = localStorage.getItem('token');
      const config = { headers: { Authorization: `Bearer ${token}` } };

      await axios.put(
        `http://localhost:5000/api/videos/${selectedVideo.id}/progress`,
        {
          watch_time_seconds: watchTime,
          completion_percentage: percentage
        },
        config
      );
    } catch (err) {
      console.error('Error updating progress:', err);
    }
  };

  const handleVideoComplete = async () => {
    if (!selectedVideo) return;

    try {
      const token = localStorage.getItem('token');
      const config = { headers: { Authorization: `Bearer ${token}` } };

      await axios.post(
        `http://localhost:5000/api/videos/${selectedVideo.id}/complete`,
        {},
        config
      );

      // Update local state
      setVideos(videos.map(v => 
        v.id === selectedVideo.id 
          ? { ...v, completed: true, completion_percentage: 100 }
          : v
      ));
      
      setSelectedVideo({ ...selectedVideo, completed: true, completion_percentage: 100 });
    } catch (err) {
      console.error('Error completing video:', err);
    }
  };

  const formatDuration = (seconds) => {
    if (!seconds) return '';
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  if (loading) {
    return (
      <div className="tutorial-list">
        <div className="loading">Loading tutorials...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="tutorial-list">
        <div className="error">{error}</div>
      </div>
    );
  }

  if (videos.length === 0) {
    return (
      <div className="tutorial-list">
        <div className="empty-state">
          <div className="empty-icon">🎥</div>
          <h3>No Tutorials Available</h3>
          <p>Video tutorials for {skillName} are coming soon!</p>
        </div>
      </div>
    );
  }

  return (
    <div className="tutorial-list">
      <div className="tutorial-header">
        <h2>📚 Video Tutorials</h2>
        <p className="tutorial-subtitle">
          Watch these videos to learn about {skillName}
        </p>
      </div>

      {/* Video Player */}
      {selectedVideo && (
        <div className="current-video">
          <VideoPlayer
            video={selectedVideo}
            onStart={handleVideoStart}
            onProgress={handleVideoProgress}
            onComplete={handleVideoComplete}
          />
        </div>
      )}

      {/* Video List */}
      {videos.length > 1 && (
        <div className="video-list-section">
          <h3 className="section-title">All Tutorials ({videos.length})</h3>
          <div className="video-grid">
            {videos.map((video) => (
              <div
                key={video.id}
                className={`video-card ${selectedVideo?.id === video.id ? 'active' : ''}`}
                onClick={() => setSelectedVideo(video)}
              >
                {/* Thumbnail */}
                <div className="video-thumbnail">
                  {video.thumbnail_url ? (
                    <img src={video.thumbnail_url} alt={video.title} />
                  ) : (
                    <div className="thumbnail-placeholder">
                      <span className="play-icon">▶</span>
                    </div>
                  )}
                  
                  {/* Duration Badge */}
                  {video.duration > 0 && (
                    <span className="duration-badge">
                      {formatDuration(video.duration)}
                    </span>
                  )}
                  
                  {/* Watched Indicator */}
                  {video.watched && (
                    <div className="watched-indicator">
                      <div 
                        className="watched-progress" 
                        style={{ width: `${video.completion_percentage}%` }}
                      />
                    </div>
                  )}
                </div>

                {/* Video Info */}
                <div className="video-card-info">
                  <h4 className="video-card-title">{video.title}</h4>
                  <div className="video-card-meta">
                    <span className={`difficulty-tag ${video.difficulty}`}>
                      {video.difficulty}
                    </span>
                    {video.completed && (
                      <span className="completed-tag">✓ Completed</span>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default TutorialList;

