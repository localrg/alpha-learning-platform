import React, { useEffect } from 'react';
import './AchievementNotification.css';

const AchievementNotification = ({ achievement, onClose }) => {
  useEffect(() => {
    const timer = setTimeout(onClose, 5000);
    return () => clearTimeout(timer);
  }, [onClose]);

  if (!achievement) return null;

  return (
    <div className="achievement-notification">
      <div className="achievement-notification-content">
        <div className="achievement-notification-header">
          <span className="achievement-trophy">🏆</span>
          <span className="achievement-notification-title">Achievement Unlocked!</span>
        </div>
        
        <div className="achievement-notification-body">
          <div className="achievement-notification-icon">{achievement.icon_emoji}</div>
          <div className="achievement-notification-details">
            <div className="achievement-notification-name">{achievement.name}</div>
            <div className="achievement-notification-description">{achievement.description}</div>
            <div className="achievement-notification-reward">+{achievement.xp_reward} XP</div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AchievementNotification;

