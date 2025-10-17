import { useState } from 'react';
import axios from 'axios';
import './HintDisplay.css';

export default function HintDisplay({ hints, onFeedback }) {
  const [expandedHints, setExpandedHints] = useState(new Set());
  const [feedbackGiven, setFeedbackGiven] = useState(new Set());

  const toggleHint = (hintId) => {
    const newExpanded = new Set(expandedHints);
    if (newExpanded.has(hintId)) {
      newExpanded.delete(hintId);
    } else {
      newExpanded.add(hintId);
    }
    setExpandedHints(newExpanded);
  };

  const provideFeedback = async (hint, helpful) => {
    if (!hint.usage_id) return;

    try {
      const token = localStorage.getItem('token');
      await axios.put(
        `/api/hints/usage/${hint.usage_id}/feedback`,
        { helpful },
        { headers: { Authorization: `Bearer ${token}` } }
      );

      setFeedbackGiven(new Set([...feedbackGiven, hint.id]));

      if (onFeedback) {
        onFeedback(hint.id, helpful);
      }
    } catch (error) {
      console.error('Error providing feedback:', error);
    }
  };

  const getLevelColor = (level) => {
    switch (level) {
      case 1: return 'blue';
      case 2: return 'purple';
      case 3: return 'orange';
      case 4: return 'green';
      default: return 'gray';
    }
  };

  const getLevelName = (level) => {
    switch (level) {
      case 1: return 'Strategic';
      case 2: return 'Conceptual';
      case 3: return 'Procedural';
      case 4: return 'Example';
      default: return 'Hint';
    }
  };

  const getIcon = (type) => {
    switch (type) {
      case 'example': return '📚';
      case 'visual': return '👁️';
      default: return '💡';
    }
  };

  if (!hints || hints.length === 0) {
    return null;
  }

  return (
    <div className="hint-display">
      <h3 className="hint-display-title">Hints</h3>
      <div className="hints-list">
        {hints.map((hint) => (
          <div
            key={hint.id}
            className={`hint-card level-${getLevelColor(hint.hint_level)} ${
              expandedHints.has(hint.id) ? 'expanded' : ''
            }`}
          >
            <div className="hint-header" onClick={() => toggleHint(hint.id)}>
              <div className="hint-header-left">
                <span className="hint-icon">{getIcon(hint.hint_type)}</span>
                <span className="hint-level-badge">
                  Level {hint.hint_level}: {getLevelName(hint.hint_level)}
                </span>
              </div>
              <span className="hint-toggle">
                {expandedHints.has(hint.id) ? '▼' : '▶'}
              </span>
            </div>

            {expandedHints.has(hint.id) && (
              <div className="hint-content">
                <p className="hint-text">{hint.hint_text}</p>

                {hint.image_url && (
                  <div className="hint-image">
                    <img src={hint.image_url} alt="Hint visualization" />
                  </div>
                )}

                {hint.usage_id && !feedbackGiven.has(hint.id) && (
                  <div className="hint-feedback">
                    <span className="feedback-label">Was this helpful?</span>
                    <div className="feedback-buttons">
                      <button
                        className="feedback-btn thumbs-up"
                        onClick={() => provideFeedback(hint, true)}
                      >
                        👍 Yes
                      </button>
                      <button
                        className="feedback-btn thumbs-down"
                        onClick={() => provideFeedback(hint, false)}
                      >
                        👎 No
                      </button>
                    </div>
                  </div>
                )}

                {feedbackGiven.has(hint.id) && (
                  <div className="feedback-thanks">
                    Thank you for your feedback!
                  </div>
                )}
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}

