import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Button } from './ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { RadioGroup, RadioGroupItem } from './ui/radio-group';
import { Label } from './ui/label';
import { Progress } from './ui/progress';
import { 
  CheckCircle2, 
  XCircle, 
  Lightbulb, 
  Target, 
  TrendingUp,
  ArrowRight,
  Award,
  BookOpen
} from 'lucide-react';

export default function SkillPractice({ skillId, onComplete, onBack }) {
  const [loading, setLoading] = useState(true);
  const [skill, setSkill] = useState(null);
  const [questions, setQuestions] = useState([]);
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [selectedAnswer, setSelectedAnswer] = useState('');
  const [feedback, setFeedback] = useState(null);
  const [showHint, setShowHint] = useState(false);
  const [sessionStats, setSessionStats] = useState({
    correct: 0,
    total: 0,
    startTime: Date.now()
  });
  const [practiceComplete, setPracticeComplete] = useState(false);
  const [learningPathItem, setLearningPathItem] = useState(null);

  useEffect(() => {
    loadSkillAndQuestions();
  }, [skillId]);

  const loadSkillAndQuestions = async () => {
    setLoading(true);
    try {
      const token = localStorage.getItem('token');
      
      // Get skill details
      const skillResponse = await axios.get(
        `/api/assessment/skills?skill_id=${skillId}`,
        { headers: { Authorization: `Bearer ${token}` } }
      );
      
      if (skillResponse.data.length > 0) {
        const skillData = skillResponse.data[0];
        setSkill(skillData);
        
        // Get questions for this skill
        const questionsResponse = await axios.get(
          `/api/assessment/skills?skill_id=${skillId}`,
          { headers: { Authorization: `Bearer ${token}` } }
        );
        
        // For now, we'll create practice questions from the skill
        // In a real implementation, this would be a separate endpoint
        setQuestions(skillData.questions || []);
      }
      
      // Get learning path item for this skill
      const pathResponse = await axios.get(
        `/api/learning-path/current`,
        { headers: { Authorization: `Bearer ${token}` } }
      );
      
      const pathItem = pathResponse.data.learning_path.find(item => item.skill_id === skillId);
      setLearningPathItem(pathItem);
      
    } catch (error) {
      console.error('Error loading skill:', error);
      alert('Failed to load skill. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const submitAnswer = async () => {
    if (!selectedAnswer) {
      alert('Please select an answer');
      return;
    }

    const question = questions[currentQuestionIndex];
    const isCorrect = selectedAnswer === question.correct_answer;
    
    // Update session stats
    setSessionStats(prev => ({
      ...prev,
      correct: prev.correct + (isCorrect ? 1 : 0),
      total: prev.total + 1
    }));

    // Show feedback
    setFeedback({
      is_correct: isCorrect,
      correct_answer: question.correct_answer,
      explanation: question.explanation
    });

    // Auto-advance after 3 seconds
    setTimeout(() => {
      if (currentQuestionIndex < questions.length - 1) {
        setCurrentQuestionIndex(prev => prev + 1);
        setSelectedAnswer('');
        setFeedback(null);
        setShowHint(false);
      } else {
        completePractice();
      }
    }, 3000);
  };

  const completePractice = async () => {
    const accuracy = (sessionStats.correct / sessionStats.total) * 100;
    
    try {
      const token = localStorage.getItem('token');
      
      // Update learning path progress
      await axios.put(
        `/api/learning-path/update-progress`,
        {
          skill_id: skillId,
          correct_answers: sessionStats.correct,
          total_questions: sessionStats.total
        },
        { headers: { Authorization: `Bearer ${token}` } }
      );
      
      setPracticeComplete(true);
      
    } catch (error) {
      console.error('Error updating progress:', error);
      setPracticeComplete(true); // Still show completion even if update fails
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading practice session...</p>
        </div>
      </div>
    );
  }

  if (!skill || questions.length === 0) {
    return (
      <Card>
        <CardContent className="pt-6">
          <p className="text-red-600">No questions available for this skill.</p>
          <Button onClick={onBack} className="mt-4">Go Back</Button>
        </CardContent>
      </Card>
    );
  }

  // Practice complete screen
  if (practiceComplete) {
    const accuracy = (sessionStats.correct / sessionStats.total) * 100;
    const isMastered = accuracy >= 90;
    const isGood = accuracy >= 70;
    
    return (
      <div className="max-w-2xl mx-auto space-y-6">
        <Card className="border-2 border-blue-200 bg-gradient-to-br from-blue-50 to-white">
          <CardHeader className="text-center">
            <div className="flex justify-center mb-4">
              <Award className={`w-16 h-16 ${isMastered ? 'text-yellow-500' : isGood ? 'text-blue-500' : 'text-gray-400'}`} />
            </div>
            <CardTitle className="text-3xl">Practice Complete!</CardTitle>
            <CardDescription className="text-lg mt-2">
              {skill.name}
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="text-center space-y-4">
              <div>
                <div className="text-6xl font-bold text-blue-600 mb-2">
                  {Math.round(accuracy)}%
                </div>
                <p className="text-gray-600">
                  {sessionStats.correct} out of {sessionStats.total} questions correct
                </p>
              </div>
              
              <Progress value={accuracy} className="h-3" />
              
              <div className="pt-4">
                {isMastered && (
                  <div className="space-y-2">
                    <p className="text-lg font-semibold text-green-600">
                      🌟 Excellent! You've mastered this skill!
                    </p>
                    <p className="text-gray-600">
                      You're ready to move on to the next skill.
                    </p>
                  </div>
                )}
                {isGood && !isMastered && (
                  <div className="space-y-2">
                    <p className="text-lg font-semibold text-blue-600">
                      👍 Good work! You're getting there!
                    </p>
                    <p className="text-gray-600">
                      Practice a bit more to reach mastery (90%+).
                    </p>
                  </div>
                )}
                {!isGood && (
                  <div className="space-y-2">
                    <p className="text-lg font-semibold text-orange-600">
                      💪 Keep practicing! You're improving!
                    </p>
                    <p className="text-gray-600">
                      Try again to strengthen your understanding.
                    </p>
                  </div>
                )}
              </div>

              <div className="flex gap-3 justify-center pt-4">
                {!isMastered && (
                  <Button 
                    onClick={() => window.location.reload()}
                    variant="outline"
                  >
                    Practice Again
                  </Button>
                )}
                <Button onClick={onComplete}>
                  {isMastered ? 'Next Skill' : 'Back to Learning Path'}
                  <ArrowRight className="w-4 h-4 ml-2" />
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Progress Update */}
        {learningPathItem && (
          <Card>
            <CardHeader>
              <div className="flex items-center gap-2">
                <TrendingUp className="w-5 h-5 text-green-500" />
                <CardTitle className="text-lg">Your Progress</CardTitle>
              </div>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                <div className="flex justify-between text-sm">
                  <span className="text-gray-600">Current Accuracy:</span>
                  <span className="font-semibold">{Math.round(accuracy)}%</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-gray-600">Total Attempts:</span>
                  <span className="font-semibold">{(learningPathItem.attempts || 0) + 1}</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-gray-600">Status:</span>
                  <span className={`font-semibold ${isMastered ? 'text-green-600' : 'text-blue-600'}`}>
                    {isMastered ? 'Mastered!' : 'In Progress'}
                  </span>
                </div>
              </div>
            </CardContent>
          </Card>
        )}
      </div>
    );
  }

  // Practice session
  const currentQuestion = questions[currentQuestionIndex];
  const progress = ((currentQuestionIndex + 1) / questions.length) * 100;
  const currentAccuracy = sessionStats.total > 0 
    ? (sessionStats.correct / sessionStats.total) * 100 
    : 0;

  return (
    <div className="max-w-2xl mx-auto space-y-6">
      {/* Header */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle className="flex items-center gap-2">
                <Target className="h-5 w-5" />
                {skill.name}
              </CardTitle>
              <CardDescription>Grade {skill.grade_level}</CardDescription>
            </div>
            <Button variant="outline" size="sm" onClick={onBack}>
              Back
            </Button>
          </div>
        </CardHeader>
        <CardContent>
          <div className="space-y-2">
            <div className="flex justify-between text-sm">
              <span className="text-gray-600">Question {currentQuestionIndex + 1} of {questions.length}</span>
              <span className="font-semibold text-blue-600">
                {sessionStats.correct}/{sessionStats.total} correct ({Math.round(currentAccuracy)}%)
              </span>
            </div>
            <Progress value={progress} className="h-2" />
          </div>
        </CardContent>
      </Card>

      {/* Question */}
      <Card>
        <CardHeader>
          <CardTitle className="text-xl">{currentQuestion.question_text}</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          {!feedback ? (
            <>
              <RadioGroup value={selectedAnswer} onValueChange={setSelectedAnswer}>
                <div className="space-y-3">
                  {currentQuestion.options.map((option, index) => (
                    <div key={index} className="flex items-center space-x-2 p-3 border rounded-lg hover:bg-gray-50">
                      <RadioGroupItem value={option} id={`option-${index}`} />
                      <Label htmlFor={`option-${index}`} className="flex-1 cursor-pointer">
                        {option}
                      </Label>
                    </div>
                  ))}
                </div>
              </RadioGroup>

              {/* Hint */}
              {currentQuestion.hint && (
                <div className="pt-2">
                  {!showHint ? (
                    <Button 
                      variant="outline" 
                      size="sm"
                      onClick={() => setShowHint(true)}
                      className="text-purple-600 border-purple-300"
                    >
                      <Lightbulb className="w-4 h-4 mr-2" />
                      Show Hint
                    </Button>
                  ) : (
                    <div className="p-3 bg-purple-50 border border-purple-200 rounded-lg">
                      <div className="flex items-start gap-2">
                        <Lightbulb className="w-5 h-5 text-purple-600 flex-shrink-0 mt-0.5" />
                        <p className="text-purple-900 text-sm">{currentQuestion.hint}</p>
                      </div>
                    </div>
                  )}
                </div>
              )}

              <Button 
                onClick={submitAnswer}
                className="w-full"
                size="lg"
                disabled={!selectedAnswer}
              >
                Submit Answer
              </Button>
            </>
          ) : (
            <div className={`p-4 rounded-lg ${feedback.is_correct ? 'bg-green-50' : 'bg-red-50'}`}>
              <div className="flex items-start gap-3">
                {feedback.is_correct ? (
                  <CheckCircle2 className="h-6 w-6 text-green-600 flex-shrink-0 mt-1" />
                ) : (
                  <XCircle className="h-6 w-6 text-red-600 flex-shrink-0 mt-1" />
                )}
                <div className="space-y-2 flex-1">
                  <p className={`font-semibold ${feedback.is_correct ? 'text-green-900' : 'text-red-900'}`}>
                    {feedback.is_correct ? 'Correct! 🎉' : 'Not quite right'}
                  </p>
                  {!feedback.is_correct && (
                    <p className="text-red-800">
                      The correct answer is: <strong>{feedback.correct_answer}</strong>
                    </p>
                  )}
                  <p className={feedback.is_correct ? 'text-green-800' : 'text-red-800'}>
                    {feedback.explanation}
                  </p>
                  <p className="text-sm text-gray-600 mt-2">
                    {currentQuestionIndex < questions.length - 1 
                      ? 'Moving to next question...' 
                      : 'Completing practice session...'}
                  </p>
                </div>
              </div>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}

