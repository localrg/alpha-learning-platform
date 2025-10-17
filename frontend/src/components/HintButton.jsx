import { useState } from 'react';
import axios from 'axios';
import './HintButton.css';

export default function HintButton({ questionId, onHintReceived, disabled }) {
  const [loading, setLoading] = useState(false);
  const [currentLevel, setCurrentLevel] = useState(0);
  const [totalLevels, setTotalLevels] = useState(4);
  const [hasMore, setHasMore] = useState(true);

  const requestHint = async () => {
    if (loading || !hasMore) return;

    setLoading(true);
    try {
      const token = localStorage.getItem('token');
      const response = await axios.post(
        '/api/hints/request',
        {
          question_id: questionId,
          current_level: currentLevel,
          attempt_number: 1,
          time_before_hint: 30
        },
        { headers: { Authorization: `Bearer ${token}` } }
      );

      const { hint, next_level_available, total_levels, usage_id } = response.data;

      setCurrentLevel(hint.hint_level);
      setTotalLevels(total_levels);
      setHasMore(next_level_available);

      // Pass hint to parent component
      if (onHintReceived) {
        onHintReceived({
          ...hint,
          usage_id
        });
      }
    } catch (error) {
      console.error('Error requesting hint:', error);
      if (error.response?.status === 404) {
        setHasMore(false);
      }
    } finally {
      setLoading(false);
    }
  };

  const getButtonText = () => {
    if (loading) return 'Loading...';
    if (!hasMore) return 'No more hints';
    if (currentLevel === 0) return '💡 Get Hint';
    return `💡 Get Hint (Level ${currentLevel}/${totalLevels})`;
  };

  return (
    <button
      className={`hint-button ${!hasMore ? 'disabled' : ''}`}
      onClick={requestHint}
      disabled={disabled || loading || !hasMore}
    >
      {getButtonText()}
    </button>
  );
}

