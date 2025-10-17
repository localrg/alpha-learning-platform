import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import axios from 'axios';
import './ReviewSession.css';

const ReviewSession = () => {
  const { learningPathId } = useParams();
  const navigate = useNavigate();
  
  const [reviewSession, setReviewSession] = useState(null);
  const [skill, setSkill] = useState(null);
  const [questions, setQuestions] = useState([]);
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [selectedAnswer, setSelectedAnswer] = useState(null);
  const [answers, setAnswers] = useState([]);
  const [showFeedback, setShowFeedback] = useState(false);
  const [isCorrect, setIsCorrect] = useState(false);
  const [reviewComplete, setReviewComplete] = useState(false);
  const [reviewResult, setReviewResult] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    startReview();
  }, [learningPathId]);

  const startReview = async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem('token');
      const config = { headers: { Authorization: `Bearer ${token}` } };

      const response = await axios.post(
        'http://localhost:5000/api/reviews/start',
        { learning_path_id: parseInt(learningPathId) },
        config
      );

      setReviewSession(response.data.review_session_id);
      setSkill(response.data.skill);
      setQuestions(response.data.questions);
      setLoading(false);
    } catch (err) {
      console.error('Error starting review:', err);
      setError('Failed to start review session');
      setLoading(false);
    }
  };

  const handleAnswerSelect = (answer) => {
    if (!showFeedback) {
      setSelectedAnswer(answer);
    }
  };

  const submitAnswer = () => {
    if (!selectedAnswer) return;

    const currentQuestion = questions[currentQuestionIndex];
    const correct = selectedAnswer === currentQuestion.correct_answer;
    
    setIsCorrect(correct);
    setShowFeedback(true);

    // Record answer
    const newAnswer = {
      question_id: currentQuestion.id,
      selected_answer: selectedAnswer,
      is_correct: correct
    };
    setAnswers([...answers, newAnswer]);
  };

  const nextQuestion = () => {
    if (currentQuestionIndex < questions.length - 1) {
      setCurrentQuestionIndex(currentQuestionIndex + 1);
      setSelectedAnswer(null);
      setShowFeedback(false);
      setIsCorrect(false);
    } else {
      completeReview();
    }
  };

  const completeReview = async () => {
    try {
      const token = localStorage.getItem('token');
      const config = { headers: { Authorization: `Bearer ${token}` } };

      // Include the last answer if not already included
      const allAnswers = [...answers];
      if (showFeedback && selectedAnswer) {
        const currentQuestion = questions[currentQuestionIndex];
        const correct = selectedAnswer === currentQuestion.correct_answer;
        allAnswers.push({
          question_id: currentQuestion.id,
          selected_answer: selectedAnswer,
          is_correct: correct
        });
      }

      const response = await axios.put(
        `http://localhost:5000/api/reviews/${reviewSession}/complete`,
        { answers: allAnswers },
        config
      );

      setReviewResult(response.data);
      setReviewComplete(true);
    } catch (err) {
      console.error('Error completing review:', err);
      setError('Failed to complete review');
    }
  };

  if (loading) {
    return (
      <div className="review-session">
        <div className="loading">Loading review...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="review-session">
        <div className="error">{error}</div>
        <button onClick={() => navigate('/reviews')} className="btn-secondary">
          Back to Reviews
        </button>
      </div>
    );
  }

  if (reviewComplete && reviewResult) {
    return (
      <div className="review-session">
        <div className="review-results">
          <div className={`result-icon ${reviewResult.passed ? 'passed' : 'failed'}`}>
            {reviewResult.passed ? '✅' : '📝'}
          </div>
          
          <h1>{reviewResult.passed ? 'Review Passed!' : 'Needs More Practice'}</h1>
          
          <div className="result-stats">
            <div className="stat-card">
              <div className="stat-label">Accuracy</div>
              <div className="stat-value">{reviewResult.review_session.accuracy}%</div>
            </div>
            <div className="stat-card">
              <div className="stat-label">Score</div>
              <div className="stat-value">
                {reviewResult.review_session.correct_answers}/{reviewResult.review_session.questions_answered}
              </div>
            </div>
          </div>

          <div className="result-message">
            <p>{reviewResult.message}</p>
            {reviewResult.next_review_date && (
              <p className="next-review">
                Next review: {new Date(reviewResult.next_review_date).toLocaleDateString('en-US', {
                  month: 'long',
                  day: 'numeric',
                  year: 'numeric'
                })}
              </p>
            )}
          </div>

          <div className="result-actions">
            {!reviewResult.passed && (
              <button
                onClick={() => navigate(`/practice/${skill.id}`)}
                className="btn-practice"
              >
                Practice This Skill
              </button>
            )}
            <button
              onClick={() => navigate('/reviews')}
              className="btn-primary"
            >
              Back to Reviews
            </button>
            <button
              onClick={() => navigate('/dashboard')}
              className="btn-secondary"
            >
              Dashboard
            </button>
          </div>
        </div>
      </div>
    );
  }

  const currentQuestion = questions[currentQuestionIndex];
  const progress = ((currentQuestionIndex + 1) / questions.length) * 100;

  return (
    <div className="review-session">
      <div className="review-header">
        <h2>🔄 Review: {skill?.name}</h2>
        <p className="question-counter">
          Question {currentQuestionIndex + 1} of {questions.length}
        </p>
      </div>

      <div className="progress-bar">
        <div className="progress-fill" style={{ width: `${progress}%` }}></div>
      </div>

      <div className="question-card">
        <h3 className="question-text">{currentQuestion.question_text}</h3>

        <div className="answer-options">
          {currentQuestion.options && Object.entries(currentQuestion.options).map(([key, value]) => (
            <button
              key={key}
              className={`answer-option ${selectedAnswer === key ? 'selected' : ''} ${
                showFeedback && key === currentQuestion.correct_answer ? 'correct' : ''
              } ${
                showFeedback && selectedAnswer === key && key !== currentQuestion.correct_answer ? 'incorrect' : ''
              }`}
              onClick={() => handleAnswerSelect(key)}
              disabled={showFeedback}
            >
              <span className="option-letter">{key.toUpperCase()}</span>
              <span className="option-text">{value}</span>
            </button>
          ))}
        </div>

        {showFeedback && (
          <div className={`feedback ${isCorrect ? 'correct' : 'incorrect'}`}>
            <div className="feedback-icon">{isCorrect ? '✓' : '✗'}</div>
            <div className="feedback-text">
              {isCorrect ? 'Correct!' : `Incorrect. The correct answer is ${currentQuestion.correct_answer.toUpperCase()}.`}
            </div>
          </div>
        )}

        <div className="question-actions">
          {!showFeedback ? (
            <button
              onClick={submitAnswer}
              disabled={!selectedAnswer}
              className="btn-submit"
            >
              Submit Answer
            </button>
          ) : (
            <button onClick={nextQuestion} className="btn-next">
              {currentQuestionIndex < questions.length - 1 ? 'Next Question →' : 'Complete Review'}
            </button>
          )}
        </div>
      </div>
    </div>
  );
};

export default ReviewSession;

