import { useState, useEffect } from 'react';
import axios from 'axios';
import NumberLine from './interactive/NumberLine';
import ArrayGrid from './interactive/ArrayGrid';
import './InteractiveExample.css';

const InteractiveExample = ({ example, onComplete }) => {
  const [interactionId, setInteractionId] = useState(null);
  const [timeSpent, setTimeSpent] = useState(0);
  const [startTime, setStartTime] = useState(null);

  useEffect(() => {
    // Start interaction tracking
    startInteraction();
    setStartTime(Date.now());

    // Track time spent
    const timer = setInterval(() => {
      setTimeSpent(prev => prev + 1);
    }, 1000);

    return () => {
      clearInterval(timer);
      if (interactionId) {
        updateTimeSpent();
      }
    };
  }, []);

  const startInteraction = async () => {
    try {
      const token = localStorage.getItem('token');
      const config = { headers: { Authorization: `Bearer ${token}` } };

      const response = await axios.post(
        `http://localhost:5000/api/examples/${example.id}/start`,
        {},
        config
      );

      setInteractionId(response.data.interaction_id);
    } catch (err) {
      console.error('Error starting interaction:', err);
    }
  };

  const logInteraction = async (actionData) => {
    if (!interactionId) return;

    try {
      const token = localStorage.getItem('token');
      const config = { headers: { Authorization: `Bearer ${token}` } };

      await axios.post(
        `http://localhost:5000/api/examples/interaction/${interactionId}/log`,
        { action: actionData },
        config
      );
    } catch (err) {
      console.error('Error logging interaction:', err);
    }
  };

  const updateTimeSpent = async () => {
    if (!interactionId) return;

    try {
      const token = localStorage.getItem('token');
      const config = { headers: { Authorization: `Bearer ${token}` } };

      await axios.put(
        `http://localhost:5000/api/examples/interaction/${interactionId}/time`,
        { time_spent_seconds: timeSpent },
        config
      );
    } catch (err) {
      console.error('Error updating time:', err);
    }
  };

  const completeInteraction = async () => {
    if (!interactionId) return;

    try {
      const token = localStorage.getItem('token');
      const config = { headers: { Authorization: `Bearer ${token}` } };

      await axios.post(
        `http://localhost:5000/api/examples/interaction/${interactionId}/complete`,
        {},
        config
      );

      if (onComplete) {
        onComplete();
      }
    } catch (err) {
      console.error('Error completing interaction:', err);
    }
  };

  const renderExample = () => {
    const { example_type, config } = example;

    switch (example_type) {
      case 'number_line':
        return <NumberLine config={config} onInteraction={logInteraction} />;
      case 'array':
        return <ArrayGrid config={config} onInteraction={logInteraction} />;
      default:
        return (
          <div className="unsupported-type">
            <p>Example type "{example_type}" is not yet supported.</p>
          </div>
        );
    }
  };

  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  return (
    <div className="interactive-example-wrapper">
      {/* Header */}
      <div className="example-header">
        <div className="example-info">
          <h3 className="example-title">{example.title}</h3>
          {example.description && (
            <p className="example-description">{example.description}</p>
          )}
        </div>
        <div className="example-meta">
          <span className={`difficulty-badge ${example.difficulty}`}>
            {example.difficulty}
          </span>
          <span className="time-badge">
            ⏱ {formatTime(timeSpent)}
          </span>
        </div>
      </div>

      {/* Interactive Component */}
      <div className="example-content">
        {renderExample()}
      </div>

      {/* Footer */}
      <div className="example-footer">
        <button className="btn-complete" onClick={completeInteraction}>
          ✓ Mark as Complete
        </button>
      </div>
    </div>
  );
};

export default InteractiveExample;

