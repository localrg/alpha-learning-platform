import React, { useState, useEffect } from 'react';
import './XPDisplay.css';

const XPDisplay = ({ onProgressClick }) => {
  const [progress, setProgress] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchProgress();
    // Refresh every 30 seconds
    const interval = setInterval(fetchProgress, 30000);
    return () => clearInterval(interval);
  }, []);

  const fetchProgress = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch('/api/gamification/progress', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (response.ok) {
        const data = await response.json();
        setProgress(data);
      }
    } catch (error) {
      console.error('Error fetching progress:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading || !progress) {
    return (
      <div className="xp-display loading">
        <div className="xp-skeleton"></div>
      </div>
    );
  }

  return (
    <div className="xp-display" onClick={onProgressClick}>
      <div className="level-badge">
        <div className="level-number">{progress.current_level}</div>
        <div className="level-title">{progress.level_title}</div>
      </div>
      
      <div className="xp-info">
        <div className="xp-text">
          <span className="xp-current">{progress.total_xp.toLocaleString()}</span>
          <span className="xp-label">XP</span>
        </div>
        
        <div className="xp-bar-container">
          <div 
            className="xp-bar-fill" 
            style={{ width: `${progress.progress_percentage}%` }}
          >
            <div className="xp-bar-shine"></div>
          </div>
        </div>
        
        <div className="xp-next">
          {progress.xp_to_next_level.toLocaleString()} XP to Level {progress.current_level + 1}
        </div>
      </div>
    </div>
  );
};

export default XPDisplay;

