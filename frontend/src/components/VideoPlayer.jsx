import { useState, useRef, useEffect } from 'react';
import ReactPlayer from 'react-player';
import axios from 'axios';
import './VideoPlayer.css';

const VideoPlayer = ({ video, onStart, onProgress, onComplete }) => {
  const [playing, setPlaying] = useState(false);
  const [played, setPlayed] = useState(0);
  const [duration, setDuration] = useState(0);
  const [hasStarted, setHasStarted] = useState(false);
  const playerRef = useRef(null);

  // Handle video start
  const handleStart = () => {
    if (!hasStarted && onStart) {
      onStart();
      setHasStarted(true);
    }
  };

  // Handle progress updates
  const handleProgress = (state) => {
    setPlayed(state.played);
    
    if (onProgress) {
      const watchTime = Math.floor(state.playedSeconds);
      const percentage = Math.floor(state.played * 100);
      onProgress(watchTime, percentage);
    }

    // Auto-complete when reaching 90%
    if (state.played >= 0.9 && !video.completed && onComplete) {
      onComplete();
    }
  };

  // Handle video duration
  const handleDuration = (dur) => {
    setDuration(dur);
  };

  // Format time (seconds to MM:SS)
  const formatTime = (seconds) => {
    if (!seconds || isNaN(seconds)) return '0:00';
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  return (
    <div className="video-player-container">
      <div className="video-wrapper">
        <ReactPlayer
          ref={playerRef}
          url={video.embed_url || video.video_url}
          playing={playing}
          controls={true}
          width="100%"
          height="100%"
          onStart={handleStart}
          onProgress={handleProgress}
          onDuration={handleDuration}
          onPlay={() => setPlaying(true)}
          onPause={() => setPlaying(false)}
          config={{
            youtube: {
              playerVars: {
                modestbranding: 1,
                rel: 0
              }
            },
            vimeo: {
              playerOptions: {
                byline: false,
                portrait: false
              }
            }
          }}
        />
      </div>

      {/* Video Info */}
      <div className="video-info">
        <div className="video-header">
          <h3 className="video-title">{video.title}</h3>
          {video.difficulty && (
            <span className={`difficulty-badge ${video.difficulty}`}>
              {video.difficulty}
            </span>
          )}
        </div>
        
        {video.description && (
          <p className="video-description">{video.description}</p>
        )}

        {/* Progress Bar */}
        {duration > 0 && (
          <div className="video-progress-section">
            <div className="progress-bar-container">
              <div 
                className="progress-bar-fill" 
                style={{ width: `${played * 100}%` }}
              />
            </div>
            <div className="progress-info">
              <span className="time-info">
                {formatTime(played * duration)} / {formatTime(duration)}
              </span>
              <span className="percentage-info">
                {Math.floor(played * 100)}% watched
              </span>
            </div>
          </div>
        )}

        {/* Completion Status */}
        {video.completed && (
          <div className="completion-badge">
            <span className="check-icon">✓</span>
            Completed
          </div>
        )}
      </div>
    </div>
  );
};

export default VideoPlayer;

