import React, { useEffect, useState } from 'react';
import './LevelUpModal.css';

const LevelUpModal = ({ levelData, onClose }) => {
  const [showConfetti, setShowConfetti] = useState(true);

  useEffect(() => {
    // Stop confetti after 3 seconds
    const timer = setTimeout(() => setShowConfetti(false), 3000);
    return () => clearTimeout(timer);
  }, []);

  if (!levelData) return null;

  const { current_level, level_title, new_rewards } = levelData;

  return (
    <div className="level-up-overlay">
      {showConfetti && <div className="confetti-container">
        {[...Array(50)].map((_, i) => (
          <div
            key={i}
            className="confetti"
            style={{
              left: `${Math.random() * 100}%`,
              animationDelay: `${Math.random() * 0.5}s`,
              backgroundColor: ['#ffd700', '#ff6b6b', '#4ecdc4', '#45b7d1', '#f7b731'][Math.floor(Math.random() * 5)]
            }}
          />
        ))}
      </div>}

      <div className="level-up-modal">
        <div className="level-up-content">
          <div className="level-up-header">
            <div className="level-up-icon">🎉</div>
            <h2 className="level-up-title">Level Up!</h2>
          </div>

          <div className="new-level-display">
            <div className="level-badge-large">
              <div className="level-number-large">{current_level}</div>
            </div>
            <div className="level-title-large">{level_title}</div>
          </div>

          {new_rewards && new_rewards.length > 0 && (
            <div className="rewards-section">
              <h3 className="rewards-title">🏆 Rewards Unlocked!</h3>
              <div className="rewards-grid">
                {new_rewards.map((reward, index) => (
                  <div key={index} className="reward-card">
                    <div className="reward-icon">
                      {reward.reward_type === 'title' && '👑'}
                      {reward.reward_type === 'badge' && '🏅'}
                      {reward.reward_type === 'avatar' && '🖼️'}
                      {reward.reward_type === 'multiplier' && '⚡'}
                    </div>
                    <div className="reward-name">{reward.reward_value}</div>
                    <div className="reward-description">{reward.description}</div>
                  </div>
                ))}
              </div>
            </div>
          )}

          <button className="continue-button" onClick={onClose}>
            Continue Learning! 🚀
          </button>
        </div>
      </div>
    </div>
  );
};

export default LevelUpModal;

