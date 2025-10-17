import { useState } from 'react';
import SolutionViewer from './SolutionViewer';
import './SolutionButton.css';

export default function SolutionButton({ questionId, eligible = true, attemptsRequired = 1, attemptsMade = 0 }) {
  const [showViewer, setShowViewer] = useState(false);

  const handleClick = () => {
    if (eligible) {
      setShowViewer(true);
    }
  };

  const getButtonText = () => {
    if (!eligible) {
      const remaining = attemptsRequired - attemptsMade;
      return `View Solution (${remaining} more ${remaining === 1 ? 'attempt' : 'attempts'} needed)`;
    }
    return '📖 View Complete Solution';
  };

  return (
    <>
      <button
        className={`solution-button ${!eligible ? 'disabled' : ''}`}
        onClick={handleClick}
        disabled={!eligible}
      >
        {getButtonText()}
      </button>

      {showViewer && (
        <SolutionViewer
          questionId={questionId}
          onClose={() => setShowViewer(false)}
          onFeedback={(helpful, understood) => {
            console.log(`Solution feedback: helpful=${helpful}, understood=${understood}`);
          }}
        />
      )}
    </>
  );
}

