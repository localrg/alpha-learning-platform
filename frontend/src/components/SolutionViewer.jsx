import { useState, useEffect } from 'react';
import axios from 'axios';
import './SolutionViewer.css';

export default function SolutionViewer({ questionId, onClose, onFeedback }) {
  const [solution, setSolution] = useState(null);
  const [loading, setLoading] = useState(true);
  const [currentStep, setCurrentStep] = useState(0);
  const [viewId, setViewId] = useState(null);
  const [viewStartTime] = useState(Date.now());
  const [stepsViewed, setStepsViewed] = useState(new Set());
  const [showFeedback, setShowFeedback] = useState(false);
  const [feedbackSubmitted, setFeedbackSubmitted] = useState(false);

  useEffect(() => {
    loadSolution();
  }, [questionId]);

  useEffect(() => {
    // Track which steps have been viewed
    if (solution && currentStep < solution.steps.length) {
      setStepsViewed(prev => new Set([...prev, currentStep + 1]));
    }
  }, [currentStep, solution]);

  const loadSolution = async () => {
    setLoading(true);
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get(
        `/api/solutions/question/${questionId}`,
        { headers: { Authorization: `Bearer ${token}` } }
      );

      setSolution(response.data.solution);
      
      // Record view
      recordView(response.data.solution.id);
    } catch (error) {
      console.error('Error loading solution:', error);
    } finally {
      setLoading(false);
    }
  };

  const recordView = async (solutionId) => {
    try {
      const token = localStorage.getItem('token');
      const response = await axios.post(
        '/api/solutions/view',
        {
          question_id: questionId,
          solution_id: solutionId,
          steps_viewed: []
        },
        { headers: { Authorization: `Bearer ${token}` } }
      );

      setViewId(response.data.view_id);
    } catch (error) {
      console.error('Error recording view:', error);
    }
  };

  const handleClose = async () => {
    // Update view with time spent and steps viewed
    if (viewId) {
      const timeSpent = Math.floor((Date.now() - viewStartTime) / 1000);
      try {
        const token = localStorage.getItem('token');
        await axios.post(
          '/api/solutions/view',
          {
            question_id: questionId,
            solution_id: solution.id,
            time_spent_seconds: timeSpent,
            steps_viewed: Array.from(stepsViewed)
          },
          { headers: { Authorization: `Bearer ${token}` } }
        );
      } catch (error) {
        console.error('Error updating view:', error);
      }
    }

    if (onClose) {
      onClose();
    }
  };

  const submitFeedback = async (helpful, understood) => {
    if (!viewId) return;

    try {
      const token = localStorage.getItem('token');
      await axios.put(
        `/api/solutions/view/${viewId}/feedback`,
        { helpful, understood },
        { headers: { Authorization: `Bearer ${token}` } }
      );

      setFeedbackSubmitted(true);

      if (onFeedback) {
        onFeedback(helpful, understood);
      }

      // Close after 2 seconds
      setTimeout(handleClose, 2000);
    } catch (error) {
      console.error('Error submitting feedback:', error);
    }
  };

  const nextStep = () => {
    if (currentStep < solution.steps.length - 1) {
      setCurrentStep(currentStep + 1);
    } else {
      setShowFeedback(true);
    }
  };

  const prevStep = () => {
    if (currentStep > 0) {
      setCurrentStep(currentStep - 1);
    }
  };

  const goToStep = (stepIndex) => {
    setCurrentStep(stepIndex);
  };

  const getStepIcon = (stepType) => {
    switch (stepType) {
      case 'explanation':
        return '💡';
      case 'calculation':
        return '🔢';
      case 'check':
        return '✓';
      case 'visual':
        return '👁️';
      default:
        return '📝';
    }
  };

  const getStepTypeColor = (stepType) => {
    switch (stepType) {
      case 'explanation':
        return 'blue';
      case 'calculation':
        return 'green';
      case 'check':
        return 'purple';
      case 'visual':
        return 'orange';
      default:
        return 'gray';
    }
  };

  if (loading) {
    return (
      <div className="solution-viewer-overlay">
        <div className="solution-viewer">
          <div className="solution-loading">
            <div className="spinner"></div>
            <p>Loading solution...</p>
          </div>
        </div>
      </div>
    );
  }

  if (!solution) {
    return (
      <div className="solution-viewer-overlay">
        <div className="solution-viewer">
          <div className="solution-error">
            <p>No solution available for this question.</p>
            <button onClick={handleClose} className="close-button">Close</button>
          </div>
        </div>
      </div>
    );
  }

  const step = solution.steps[currentStep];

  return (
    <div className="solution-viewer-overlay">
      <div className="solution-viewer">
        {/* Header */}
        <div className="solution-header">
          <h2>📖 Complete Solution</h2>
          <button onClick={handleClose} className="close-button-x">×</button>
        </div>

        {/* Progress Bar */}
        <div className="solution-progress">
          <div className="progress-bar">
            <div
              className="progress-fill"
              style={{ width: `${((currentStep + 1) / solution.steps.length) * 100}%` }}
            ></div>
          </div>
          <div className="progress-text">
            Step {currentStep + 1} of {solution.steps.length}
          </div>
        </div>

        {/* Step Navigation Dots */}
        <div className="step-dots">
          {solution.steps.map((s, index) => (
            <button
              key={index}
              className={`step-dot ${index === currentStep ? 'active' : ''} ${
                stepsViewed.has(index + 1) ? 'viewed' : ''
              }`}
              onClick={() => goToStep(index)}
              title={`Step ${index + 1}: ${s.step_type}`}
            >
              {index + 1}
            </button>
          ))}
        </div>

        {/* Current Step */}
        {!showFeedback ? (
          <div className="solution-content">
            <div className={`step-card ${step.highlight ? 'highlighted' : ''}`}>
              <div className="step-header">
                <span className={`step-icon type-${getStepTypeColor(step.step_type)}`}>
                  {getStepIcon(step.step_type)}
                </span>
                <span className="step-number">Step {step.step_number}</span>
                <span className={`step-type type-${getStepTypeColor(step.step_type)}`}>
                  {step.step_type}
                </span>
              </div>

              <div className="step-content">
                <p className="step-main-content">{step.content}</p>
              </div>

              <div className="step-explanation">
                <span className="explanation-label">Why this step:</span>
                <p>{step.explanation}</p>
              </div>

              {step.formula && (
                <div className="step-formula">
                  <span className="formula-label">Formula:</span>
                  <code>{step.formula}</code>
                </div>
              )}

              {step.image_url && (
                <div className="step-image">
                  <img src={step.image_url} alt={`Step ${step.step_number} visualization`} />
                </div>
              )}
            </div>

            {/* Navigation Buttons */}
            <div className="solution-navigation">
              <button
                onClick={prevStep}
                disabled={currentStep === 0}
                className="nav-button prev-button"
              >
                ← Previous
              </button>
              <button
                onClick={nextStep}
                className="nav-button next-button"
              >
                {currentStep < solution.steps.length - 1 ? 'Next →' : 'Finish'}
              </button>
            </div>
          </div>
        ) : (
          <div className="solution-feedback">
            {!feedbackSubmitted ? (
              <>
                <h3>How was this solution?</h3>
                <p>Your feedback helps us improve!</p>

                <div className="feedback-question">
                  <p className="feedback-label">Was this solution helpful?</p>
                  <div className="feedback-buttons">
                    <button
                      className="feedback-btn helpful-yes"
                      onClick={() => submitFeedback(true, true)}
                    >
                      👍 Yes, very helpful
                    </button>
                    <button
                      className="feedback-btn helpful-no"
                      onClick={() => submitFeedback(false, false)}
                    >
                      👎 Not helpful
                    </button>
                  </div>
                </div>

                <div className="feedback-question">
                  <p className="feedback-label">Do you understand the solution now?</p>
                  <div className="feedback-buttons">
                    <button
                      className="feedback-btn understood-yes"
                      onClick={() => submitFeedback(true, true)}
                    >
                      ✓ Yes, I understand
                    </button>
                    <button
                      className="feedback-btn understood-no"
                      onClick={() => submitFeedback(true, false)}
                    >
                      ? Still confused
                    </button>
                  </div>
                </div>
              </>
            ) : (
              <div className="feedback-thanks">
                <div className="thanks-icon">✓</div>
                <h3>Thank you for your feedback!</h3>
                <p>Closing...</p>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

