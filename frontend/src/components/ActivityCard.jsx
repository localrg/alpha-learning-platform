import React from 'react';
import { useAuth } from '../contexts/AuthContext';
import './ActivityCard.css';

const ActivityCard = ({ activity, onDelete }) => {
  const { user } = useAuth();
  
  const getActivityIcon = (type) => {
    const icons = {
      'skill_mastery': '✅',
      'level_up': '🎉',
      'achievement_unlock': '🏆',
      'challenge_complete': '🎯',
      'streak_milestone': '🔥',
      'friend_added': '👥',
      'class_joined': '🎓',
      'practice_session': '📝'
    };
    return icons[type] || '📌';
  };

  const getActivityColor = (type) => {
    const colors = {
      'skill_mastery': 'green',
      'level_up': 'purple',
      'achievement_unlock': 'gold',
      'challenge_complete': 'blue',
      'streak_milestone': 'orange',
      'friend_added': 'lightblue',
      'class_joined': 'navy',
      'practice_session': 'gray'
    };
    return colors[type] || 'default';
  };

  const isOwnActivity = activity.student && user && 
                        activity.student.id === user.student_id;

  const handleDelete = () => {
    if (window.confirm('Delete this activity?')) {
      onDelete(activity.id);
    }
  };

  return (
    <div className={`activity-card ${getActivityColor(activity.activity_type)}`}>
      <div className="activity-header">
        <div className="student-info">
          <div className="student-avatar">{activity.student?.avatar || '😊'}</div>
          <div className="student-details">
            <div className="student-name">
              {activity.student?.name || 'Unknown'}
              {isOwnActivity && <span className="you-badge">You</span>}
            </div>
            <div className="student-meta">
              Level {activity.student?.level || 1} • {activity.time_ago}
            </div>
          </div>
        </div>
        {isOwnActivity && (
          <button className="btn-delete" onClick={handleDelete} title="Delete activity">
            ×
          </button>
        )}
      </div>

      <div className="activity-content">
        <div className="activity-icon">{getActivityIcon(activity.activity_type)}</div>
        <div className="activity-text">
          <h3 className="activity-title">{activity.title}</h3>
          {activity.description && (
            <p className="activity-description">{activity.description}</p>
          )}
        </div>
      </div>

      {(activity.xp_earned > 0 || activity.accuracy || activity.questions_answered) && (
        <div className="activity-stats">
          {activity.xp_earned > 0 && (
            <div className="stat-badge xp">
              +{activity.xp_earned} XP
            </div>
          )}
          {activity.accuracy && (
            <div className="stat-badge accuracy">
              {Math.round(activity.accuracy * 100)}% accuracy
            </div>
          )}
          {activity.questions_answered && (
            <div className="stat-badge questions">
              {activity.questions_answered} questions
            </div>
          )}
          {activity.streak_days && (
            <div className="stat-badge streak">
              {activity.streak_days} days
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default ActivityCard;

