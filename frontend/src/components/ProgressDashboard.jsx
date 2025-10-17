import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Progress } from './ui/progress';
import { Button } from './ui/button';
import { Trophy, Target, Clock, TrendingUp, BookOpen, CheckCircle2, Circle } from 'lucide-react';
import DailyChallengesCard from './DailyChallengesCard';
import StreakDisplay from './StreakDisplay';

export default function ProgressDashboard({ onStartPractice }) {
  const [loading, setLoading] = useState(true);
  const [learningPath, setLearningPath] = useState([]);
  const [stats, setStats] = useState({
    totalSkills: 0,
    masteredSkills: 0,
    inProgressSkills: 0,
    overallAccuracy: 0,
    totalAttempts: 0,
    currentStreak: 0
  });

  useEffect(() => {
    fetchProgress();
  }, []);

  const fetchProgress = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get('/api/learning-path/current', {
        headers: { Authorization: `Bearer ${token}` }
      });

      const path = response.data.learning_path || [];
      setLearningPath(path);

      // Calculate statistics
      const mastered = path.filter(item => item.status === 'mastered').length;
      const inProgress = path.filter(item => item.status === 'in_progress').length;
      const totalAccuracy = path.reduce((sum, item) => sum + (item.current_accuracy || 0), 0);
      const avgAccuracy = path.length > 0 ? totalAccuracy / path.length : 0;
      const totalAttempts = path.reduce((sum, item) => sum + (item.attempts || 0), 0);

      setStats({
        totalSkills: path.length,
        masteredSkills: mastered,
        inProgressSkills: inProgress,
        overallAccuracy: Math.round(avgAccuracy),
        totalAttempts: totalAttempts,
        currentStreak: 0 // Will implement streak tracking later
      });

      setLoading(false);
    } catch (error) {
      console.error('Error fetching progress:', error);
      setLoading(false);
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'mastered':
        return <CheckCircle2 className="h-5 w-5 text-green-500" />;
      case 'in_progress':
        return <Circle className="h-5 w-5 text-blue-500" />;
      default:
        return <Circle className="h-5 w-5 text-gray-300" />;
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'mastered':
        return 'text-green-600 bg-green-50';
      case 'in_progress':
        return 'text-blue-600 bg-blue-50';
      default:
        return 'text-gray-600 bg-gray-50';
    }
  };

  const getStatusText = (status) => {
    switch (status) {
      case 'mastered':
        return 'Mastered';
      case 'in_progress':
        return 'In Progress';
      default:
        return 'Not Started';
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading your progress...</p>
        </div>
      </div>
    );
  }

  const masteryPercentage = stats.totalSkills > 0 
    ? Math.round((stats.masteredSkills / stats.totalSkills) * 100) 
    : 0;

  const nextSkill = learningPath.find(item => item.status !== 'mastered');

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-6">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">Your Learning Dashboard</h1>
          <p className="text-gray-600">Track your progress and continue your learning journey</p>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          {/* Mastered Skills */}
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Skills Mastered</CardTitle>
              <Trophy className="h-4 w-4 text-yellow-500" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats.masteredSkills}</div>
              <p className="text-xs text-gray-600">out of {stats.totalSkills} skills</p>
              <Progress value={masteryPercentage} className="mt-2" />
            </CardContent>
          </Card>

          {/* Overall Accuracy */}
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Overall Accuracy</CardTitle>
              <Target className="h-4 w-4 text-blue-500" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats.overallAccuracy}%</div>
              <p className="text-xs text-gray-600">average across all skills</p>
              <Progress value={stats.overallAccuracy} className="mt-2" />
            </CardContent>
          </Card>

          {/* In Progress */}
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">In Progress</CardTitle>
              <TrendingUp className="h-4 w-4 text-indigo-500" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats.inProgressSkills}</div>
              <p className="text-xs text-gray-600">skills being worked on</p>
            </CardContent>
          </Card>

          {/* Total Practice */}
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Practice Sessions</CardTitle>
              <BookOpen className="h-4 w-4 text-green-500" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats.totalAttempts}</div>
              <p className="text-xs text-gray-600">total practice attempts</p>
            </CardContent>
          </Card>
        </div>

        {/* Daily Challenges */}
        <DailyChallengesCard />

        {/* Streak Tracking */}
        <StreakDisplay />

        {/* Next Recommended Skill */}
        {nextSkill && (
          <Card className="mb-8 border-2 border-blue-500">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Target className="h-5 w-5 text-blue-500" />
                Next Recommended Skill
              </CardTitle>
              <CardDescription>Continue your learning journey</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="text-xl font-semibold text-gray-900">{nextSkill.skill_name}</h3>
                  <p className="text-sm text-gray-600">Grade {nextSkill.skill_grade}</p>
                  {nextSkill.current_accuracy > 0 && (
                    <div className="mt-2">
                      <p className="text-sm text-gray-600">Current Progress: {nextSkill.current_accuracy}%</p>
                      <Progress value={nextSkill.current_accuracy} className="mt-1 w-64" />
                    </div>
                  )}
                </div>
                <Button 
                  onClick={() => onStartPractice(nextSkill)}
                  size="lg"
                  className="bg-blue-600 hover:bg-blue-700"
                >
                  {nextSkill.status === 'not_started' ? 'Start Practice' : 'Continue Practice'}
                </Button>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Learning Path */}
        <Card>
          <CardHeader>
            <CardTitle>Your Learning Path</CardTitle>
            <CardDescription>All skills in your personalized learning journey</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {learningPath.length === 0 ? (
                <p className="text-center text-gray-600 py-8">
                  No learning path yet. Take the diagnostic assessment to get started!
                </p>
              ) : (
                learningPath.map((item, index) => (
                  <div 
                    key={item.id}
                    className="flex items-center justify-between p-4 rounded-lg border hover:border-blue-500 transition-colors"
                  >
                    <div className="flex items-center gap-4 flex-1">
                      <div className="flex items-center gap-2">
                        <span className="text-2xl font-bold text-gray-400">{index + 1}</span>
                        {getStatusIcon(item.status)}
                      </div>
                      <div className="flex-1">
                        <h4 className="font-semibold text-gray-900">{item.skill_name}</h4>
                        <p className="text-sm text-gray-600">Grade {item.skill_grade}</p>
                      </div>
                    </div>

                    <div className="flex items-center gap-6">
                      {/* Accuracy */}
                      <div className="text-center">
                        <p className="text-sm text-gray-600">Accuracy</p>
                        <p className="text-lg font-semibold">{item.current_accuracy || 0}%</p>
                      </div>

                      {/* Attempts */}
                      <div className="text-center">
                        <p className="text-sm text-gray-600">Attempts</p>
                        <p className="text-lg font-semibold">{item.attempts || 0}</p>
                      </div>

                      {/* Status Badge */}
                      <div className={`px-3 py-1 rounded-full text-sm font-medium ${getStatusColor(item.status)}`}>
                        {getStatusText(item.status)}
                      </div>

                      {/* Action Button */}
                      <Button
                        onClick={() => onStartPractice(item)}
                        variant={item.status === 'mastered' ? 'outline' : 'default'}
                        disabled={item.status === 'mastered'}
                      >
                        {item.status === 'mastered' ? 'Mastered ✓' : 'Practice'}
                      </Button>
                    </div>
                  </div>
                ))
              )}
            </div>
          </CardContent>
        </Card>

        {/* Motivational Message */}
        {stats.masteredSkills > 0 && (
          <div className="mt-8 text-center">
            <div className="inline-block bg-gradient-to-r from-yellow-400 to-orange-500 text-white px-6 py-3 rounded-full">
              <p className="font-semibold">
                🎉 Great job! You've mastered {stats.masteredSkills} skill{stats.masteredSkills !== 1 ? 's' : ''}! Keep going!
              </p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

