import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Button } from './ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Progress } from './ui/progress';
import { Trophy, Target, TrendingUp, BookOpen, ArrowRight, CheckCircle2 } from 'lucide-react';

export default function AssessmentResults({ assessmentId, onStartLearning }) {
  const [loading, setLoading] = useState(true);
  const [assessment, setAssessment] = useState(null);
  const [learningPath, setLearningPath] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    loadResults();
  }, [assessmentId]);

  const loadResults = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const token = localStorage.getItem('token');
      
      // Get assessment details
      const assessmentResponse = await axios.get(
        `/api/assessment/${assessmentId}`,
        { headers: { Authorization: `Bearer ${token}` } }
      );
      setAssessment(assessmentResponse.data);
      
      // Generate learning path from assessment
      const learningPathResponse = await axios.post(
        `/api/learning-path/generate/${assessmentId}`,
        {},
        { headers: { Authorization: `Bearer ${token}` } }
      );
      setLearningPath(learningPathResponse.data);
      
    } catch (err) {
      console.error('Error loading results:', err);
      setError('Failed to load assessment results. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Analyzing your results...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <Card>
        <CardContent className="pt-6">
          <p className="text-red-600">{error}</p>
          <Button onClick={loadResults} className="mt-4">Try Again</Button>
        </CardContent>
      </Card>
    );
  }

  if (!assessment || !learningPath) {
    return null;
  }

  const scorePercentage = assessment.score_percentage;
  const isGoodScore = scorePercentage >= 70;
  const isGreatScore = scorePercentage >= 85;

  return (
    <div className="space-y-6">
      {/* Header with Score */}
      <Card className="border-2 border-blue-200 bg-gradient-to-br from-blue-50 to-white">
        <CardHeader className="text-center">
          <div className="flex justify-center mb-4">
            <Trophy className={`w-16 h-16 ${isGreatScore ? 'text-yellow-500' : isGoodScore ? 'text-blue-500' : 'text-gray-400'}`} />
          </div>
          <CardTitle className="text-3xl">Assessment Complete!</CardTitle>
          <CardDescription className="text-lg mt-2">
            Here's how you did
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="text-center space-y-4">
            <div>
              <div className="text-6xl font-bold text-blue-600 mb-2">
                {Math.round(scorePercentage)}%
              </div>
              <p className="text-gray-600">
                {assessment.correct_answers} out of {assessment.total_questions} questions correct
              </p>
            </div>
            
            <Progress value={scorePercentage} className="h-3" />
            
            <div className="pt-4">
              {isGreatScore && (
                <p className="text-lg font-semibold text-green-600">
                  🌟 Excellent work! You're doing great!
                </p>
              )}
              {isGoodScore && !isGreatScore && (
                <p className="text-lg font-semibold text-blue-600">
                  👍 Good job! You're on the right track!
                </p>
              )}
              {!isGoodScore && (
                <p className="text-lg font-semibold text-orange-600">
                  💪 Don't worry! We'll help you master these skills!
                </p>
              )}
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Skills Analysis */}
      {learningPath.skills_analysis && learningPath.skills_analysis.length > 0 && (
        <Card>
          <CardHeader>
            <div className="flex items-center gap-2">
              <Target className="w-5 h-5 text-orange-500" />
              <CardTitle>Skills to Work On</CardTitle>
            </div>
            <CardDescription>
              We identified {learningPath.total_skills_to_master} skill{learningPath.total_skills_to_master !== 1 ? 's' : ''} where you can improve
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {learningPath.skills_analysis.map((skill, index) => (
                <div key={index} className="border rounded-lg p-4 bg-gray-50">
                  <div className="flex justify-between items-start mb-2">
                    <div>
                      <h4 className="font-semibold">{skill.skill_name}</h4>
                      <p className="text-sm text-gray-600">Grade {skill.skill_grade}</p>
                    </div>
                    <div className="text-right">
                      <div className="text-lg font-semibold text-orange-600">
                        {Math.round(skill.accuracy)}%
                      </div>
                      <div className="text-xs text-gray-500">
                        {skill.correct}/{skill.questions_attempted} correct
                      </div>
                    </div>
                  </div>
                  <Progress value={skill.accuracy} className="h-2" />
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Personalized Learning Path */}
      {learningPath.learning_path && learningPath.learning_path.length > 0 && (
        <Card>
          <CardHeader>
            <div className="flex items-center gap-2">
              <TrendingUp className="w-5 h-5 text-green-500" />
              <CardTitle>Your Personalized Learning Path</CardTitle>
            </div>
            <CardDescription>
              Master these skills in order for the best results
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {learningPath.learning_path.map((item, index) => (
                <div 
                  key={item.id} 
                  className={`border rounded-lg p-4 ${index === 0 ? 'bg-blue-50 border-blue-300' : 'bg-white'}`}
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <div className={`flex items-center justify-center w-8 h-8 rounded-full ${index === 0 ? 'bg-blue-600 text-white' : 'bg-gray-200 text-gray-600'} font-semibold`}>
                        {index + 1}
                      </div>
                      <div>
                        <h4 className="font-semibold">{item.skill_name}</h4>
                        {index === 0 && (
                          <p className="text-sm text-blue-600 font-medium">
                            👉 Start here!
                          </p>
                        )}
                      </div>
                    </div>
                    {index === 0 && (
                      <CheckCircle2 className="w-6 h-6 text-blue-600" />
                    )}
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Recommendations */}
      {learningPath.recommendations && learningPath.recommendations.length > 0 && (
        <Card>
          <CardHeader>
            <div className="flex items-center gap-2">
              <BookOpen className="w-5 h-5 text-purple-500" />
              <CardTitle>Recommendations</CardTitle>
            </div>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {learningPath.recommendations.map((rec, index) => (
                <div key={index} className="flex items-start gap-3 p-3 bg-purple-50 rounded-lg">
                  <div className="flex-shrink-0 w-6 h-6 rounded-full bg-purple-200 flex items-center justify-center text-purple-700 text-sm font-semibold mt-0.5">
                    {index + 1}
                  </div>
                  <p className="text-gray-700">{rec.message}</p>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Action Button */}
      <div className="flex justify-center pt-4">
        <Button 
          onClick={onStartLearning}
          size="lg"
          className="text-lg px-8 py-6"
        >
          Start Learning
          <ArrowRight className="w-5 h-5 ml-2" />
        </Button>
      </div>
    </div>
  );
}

