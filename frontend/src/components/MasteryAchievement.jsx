import React from 'react';
import { Card, CardContent } from './ui/card';
import { Button } from './ui/button';
import { Trophy, Star, Sparkles, Award } from 'lucide-react';

export default function MasteryAchievement({ skill, onContinue, onNextSkill }) {
  return (
    <div className="min-h-screen bg-gradient-to-br from-yellow-50 via-orange-50 to-pink-50 flex items-center justify-center p-6">
      <Card className="max-w-2xl w-full border-4 border-yellow-400 shadow-2xl">
        <CardContent className="p-12 text-center">
          {/* Animated Trophy */}
          <div className="mb-8 relative">
            <div className="absolute inset-0 flex items-center justify-center">
              <div className="w-32 h-32 bg-yellow-200 rounded-full animate-ping opacity-20"></div>
            </div>
            <div className="relative flex items-center justify-center">
              <Trophy className="w-32 h-32 text-yellow-500 animate-bounce" />
              <Sparkles className="w-8 h-8 text-yellow-400 absolute top-0 right-0 animate-pulse" />
              <Star className="w-6 h-6 text-yellow-400 absolute bottom-0 left-0 animate-pulse" />
            </div>
          </div>

          {/* Congratulations Message */}
          <h1 className="text-5xl font-bold text-gray-900 mb-4">
            🎉 Skill Mastered! 🎉
          </h1>
          
          <p className="text-2xl text-gray-700 mb-6">
            You've mastered <span className="font-bold text-yellow-600">{skill.skill_name}</span>!
          </p>

          {/* Achievement Details */}
          <div className="bg-white rounded-lg p-6 mb-8 border-2 border-yellow-300">
            <div className="grid grid-cols-2 gap-6">
              <div>
                <p className="text-sm text-gray-600 mb-1">Final Accuracy</p>
                <p className="text-3xl font-bold text-green-600">{Math.round(skill.final_accuracy || skill.current_accuracy)}%</p>
              </div>
              <div>
                <p className="text-sm text-gray-600 mb-1">Total Attempts</p>
                <p className="text-3xl font-bold text-blue-600">{skill.total_attempts || skill.attempts}</p>
              </div>
            </div>
          </div>

          {/* Motivational Message */}
          <div className="bg-gradient-to-r from-yellow-100 to-orange-100 rounded-lg p-6 mb-8">
            <div className="flex items-center justify-center gap-2 mb-2">
              <Award className="w-6 h-6 text-yellow-600" />
              <p className="text-lg font-semibold text-gray-800">Outstanding Achievement!</p>
            </div>
            <p className="text-gray-700">
              You've demonstrated true mastery of this skill. Your hard work and dedication have paid off!
              Keep up the excellent work as you continue your learning journey.
            </p>
          </div>

          {/* Action Buttons */}
          <div className="flex gap-4 justify-center">
            <Button
              onClick={onContinue}
              size="lg"
              variant="outline"
              className="border-2 border-yellow-500 hover:bg-yellow-50"
            >
              Practice Again
            </Button>
            <Button
              onClick={onNextSkill}
              size="lg"
              className="bg-gradient-to-r from-yellow-500 to-orange-500 hover:from-yellow-600 hover:to-orange-600 text-white"
            >
              Next Skill →
            </Button>
          </div>

          {/* Confetti Effect (CSS animation) */}
          <div className="mt-8">
            <div className="flex justify-center gap-2">
              {[...Array(10)].map((_, i) => (
                <div
                  key={i}
                  className="w-2 h-2 rounded-full bg-yellow-400 animate-bounce"
                  style={{
                    animationDelay: `${i * 0.1}s`,
                    animationDuration: '1s'
                  }}
                />
              ))}
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

