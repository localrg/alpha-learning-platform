import React, { useEffect } from 'react';
import './XPNotification.css';

const XPNotification = ({ xpAmount, description, onClose }) => {
  useEffect(() => {
    const timer = setTimeout(onClose, 3000);
    return () => clearTimeout(timer);
  }, [onClose]);

  return (
    <div className="xp-notification">
      <div className="xp-notification-icon">⭐</div>
      <div className="xp-notification-content">
        <div className="xp-notification-amount">+{xpAmount} XP</div>
        {description && <div className="xp-notification-description">{description}</div>}
      </div>
    </div>
  );
};

export default XPNotification;

