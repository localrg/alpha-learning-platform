import React, { useState, useEffect } from 'react';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import Login from './components/Login';
import Register from './components/Register';
import StudentProfile from './components/StudentProfile';
import Assessment from './components/Assessment';
import ProgressDashboard from './components/ProgressDashboard';
import SkillPractice from './components/SkillPractice';
import ReviewDashboard from './components/ReviewDashboard';
import ReviewSession from './components/ReviewSession';
import ResourceLibrary from './components/ResourceLibrary';
import XPDisplay from './components/XPDisplay';
import LevelUpModal from './components/LevelUpModal';
import XPNotification from './components/XPNotification';
import AchievementsPage from './components/AchievementsPage';
import LeaderboardPage from './components/LeaderboardPage';
import ProfilePage from './components/ProfilePage';
import FriendsPage from './components/FriendsPage';
import ClassesPage from './components/ClassesPage';
import SharedChallengesPage from './components/SharedChallengesPage';
import ChallengeDetailPage from './components/ChallengeDetailPage';
import SocialFeedPage from './components/SocialFeedPage';
import ProtectedRoute from './components/ProtectedRoute';
import { Button } from './components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './components/ui/card';
import './App.css';

function AuthenticatedApp() {
  const { user, logout } = useAuth();
  const [student, setStudent] = useState(null);
  const [loadingStudent, setLoadingStudent] = useState(true);
  const [currentView, setCurrentView] = useState('dashboard'); // 'dashboard', 'assessment', 'practice', 'reviews', 'review-session', 'resources', 'achievements', 'leaderboard', 'profile', 'friends', 'classes', 'shared-challenges', 'challenge-detail', 'feed'
  const [selectedSkill, setSelectedSkill] = useState(null);

  // Fetch student profile on mount
  useEffect(() => {
    const fetchStudentProfile = async () => {
      try {
        const token = localStorage.getItem('token');
        const response = await fetch('/api/student/profile', {
          headers: {
            'Authorization': `Bearer ${token}`,
          },
        });

        if (response.ok) {
          const data = await response.json();
          setStudent(data.student);
        }
        // If 404, student profile doesn't exist yet (that's okay)
      } catch (error) {
        console.error('Error fetching student profile:', error);
      } finally {
        setLoadingStudent(false);
      }
    };

    fetchStudentProfile();
  }, []);

  const handleProfileCreated = (studentData) => {
    setStudent(studentData);
    // After profile creation, show assessment
    setCurrentView('assessment');
  };

  const handleAssessmentComplete = () => {
    // After assessment, show dashboard
    setCurrentView('dashboard');
  };

  const handleStartPractice = (skill) => {
    setSelectedSkill(skill);
    setCurrentView('practice');
  };

  const handlePracticeComplete = () => {
    setCurrentView('dashboard');
  };

  const handleShowReviews = () => {
    setCurrentView('reviews');
  };

  const handleStartReviewSession = (learningPathId) => {
    setSelectedSkill({ learningPathId }); // Store for review session
    setCurrentView('review-session');
  };

  const handleReviewComplete = () => {
    setCurrentView('reviews');
  };

  if (loadingStudent) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading...</p>
        </div>
      </div>
    );
  }

  // If no student profile, show profile creation
  if (!student) {
    return <StudentProfile onProfileCreated={handleProfileCreated} />;
  }

  // Render current view
  if (currentView === 'leaderboard') {
    return (
      <div>
        <div className="bg-white shadow-sm border-b">
          <div className="max-w-6xl mx-auto px-6 py-4 flex justify-between items-center">
            <h1 className="text-2xl font-bold text-gray-900">Leaderboards</h1>
            <Button onClick={() => setCurrentView('dashboard')} variant="outline">
              ← Back to Dashboard
            </Button>
          </div>
        </div>
        <LeaderboardPage />
      </div>
    );
  }

  if (currentView === 'profile') {
    return (
      <div>
        <div className="bg-white shadow-sm border-b">
          <div className="max-w-6xl mx-auto px-6 py-4 flex justify-between items-center">
            <h1 className="text-2xl font-bold text-gray-900">My Profile</h1>
            <Button onClick={() => setCurrentView('dashboard')} variant="outline">
              ← Back to Dashboard
            </Button>
          </div>
        </div>
        <ProfilePage studentId={student?.id} isOwnProfile={true} />
      </div>
    );
  }

  if (currentView === 'friends') {
    return (
      <div>
        <div className="bg-white shadow-sm border-b">
          <div className="max-w-6xl mx-auto px-6 py-4 flex justify-between items-center">
            <h1 className="text-2xl font-bold text-gray-900">Friends</h1>
            <Button onClick={() => setCurrentView('dashboard')} variant="outline">
              ← Back to Dashboard
            </Button>
          </div>
        </div>
        <FriendsPage />
      </div>
    );
  }

  if (currentView === 'classes') {
    return (
      <div>
        <div className="bg-white shadow-sm border-b">
          <div className="max-w-6xl mx-auto px-6 py-4 flex justify-between items-center">
            <h1 className="text-2xl font-bold text-gray-900">Classes</h1>
            <Button onClick={() => setCurrentView('dashboard')} variant="outline">
              ← Back to Dashboard
            </Button>
          </div>
        </div>
        <ClassesPage />
      </div>
    );
  }

  if (currentView === 'shared-challenges') {
    return (
      <div>
        <div className="bg-white shadow-sm border-b">
          <div className="max-w-6xl mx-auto px-6 py-4 flex justify-between items-center">
            <h1 className="text-2xl font-bold text-gray-900">Challenges</h1>
            <Button onClick={() => setCurrentView('dashboard')} variant="outline">
              ← Back to Dashboard
            </Button>
          </div>
        </div>
        <SharedChallengesPage />
      </div>
    );
  }

  if (currentView === 'feed') {
    return (
      <div>
        <div className="bg-white shadow-sm border-b">
          <div className="max-w-6xl mx-auto px-6 py-4 flex justify-between items-center">
            <h1 className="text-2xl font-bold text-gray-900">Activity Feed</h1>
            <Button onClick={() => setCurrentView('dashboard')} variant="outline">
              ← Back to Dashboard
            </Button>
          </div>
        </div>
        <SocialFeedPage />
      </div>
    );
  }

  if (currentView === 'achievements') {
    return (
      <div>
        <div className="bg-white shadow-sm border-b">
          <div className="max-w-6xl mx-auto px-6 py-4 flex justify-between items-center">
            <h1 className="text-2xl font-bold text-gray-900">Achievements</h1>
            <Button onClick={() => setCurrentView('dashboard')} variant="outline">
              ← Back to Dashboard
            </Button>
          </div>
        </div>
        <AchievementsPage />
      </div>
    );
  }

  if (currentView === 'reviews') {
    return <ReviewDashboard onBack={() => setCurrentView('dashboard')} />;
  }

  if (currentView === 'resources') {
    return (
      <div>
        <div className="bg-white shadow-sm border-b">
          <div className="max-w-6xl mx-auto px-6 py-4 flex justify-between items-center">
            <h1 className="text-2xl font-bold text-gray-900">Resource Library</h1>
            <Button onClick={() => setCurrentView('dashboard')} variant="outline">
              ← Back to Dashboard
            </Button>
          </div>
        </div>
        <ResourceLibrary />
      </div>
    );
  }

  if (currentView === 'review-session' && selectedSkill?.learningPathId) {
    return (
      <ReviewSession 
        learningPathId={selectedSkill.learningPathId}
        onComplete={handleReviewComplete}
        onBack={() => setCurrentView('reviews')}
      />
    );
  }

  if (currentView === 'assessment') {
    return <Assessment onComplete={handleAssessmentComplete} />;
  }

  if (currentView === 'practice' && selectedSkill) {
    return (
      <SkillPractice 
        skill={selectedSkill}
        onComplete={handlePracticeComplete}
        onBack={() => setCurrentView('dashboard')}
      />
    );
  }

  // Default: Dashboard
  return (
    <div>
      {/* Header with logout */}
      <div className="bg-white shadow-sm border-b">
        <div className="max-w-6xl mx-auto px-6 py-4 flex justify-between items-center">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Alpha Learning Platform</h1>
            <p className="text-sm text-gray-600">Welcome back, {student.name}!</p>
          </div>
          <div className="flex gap-4 items-center">
            <XPDisplay onProgressClick={() => console.log('Show progress modal')} />
            <Button
              onClick={() => setCurrentView('leaderboard')}
              variant="outline"
            >
              🏆 Leaderboard
            </Button>
            <Button
              onClick={() => setCurrentView('achievements')}
              variant="outline"
            >
              🏅 Achievements
            </Button>
            <Button
              onClick={() => setCurrentView('reviews')}
              variant="outline"
            >
              📚 Reviews
            </Button>
            <Button
              onClick={() => setCurrentView('feed')}
              variant="outline"
            >
              📰 Feed
            </Button>
            <Button
              onClick={() => setCurrentView('friends')}
              variant="outline"
            >
              👥 Friends
            </Button>
            <Button
              onClick={() => setCurrentView('classes')}
              variant="outline"
            >
              🎓 Classes
            </Button>
            <Button
              onClick={() => setCurrentView('shared-challenges')}
              variant="outline"
            >
              🎯 Challenges
            </Button>
            <Button
              onClick={() => setCurrentView('profile')}
              variant="outline"
            >
              👤 Profile
            </Button>
            <Button
              onClick={() => setCurrentView('resources')}
              variant="outline"
            >
              📖 Resources
            </Button>
            <Button
              onClick={() => setCurrentView('assessment')}
              variant="outline"
            >
              Take Assessment
            </Button>
            <Button onClick={logout} variant="outline">
              Logout
            </Button>
          </div>
        </div>
      </div>

      {/* Dashboard */}
      <ProgressDashboard onStartPractice={handleStartPractice} />
    </div>
  );
}

function App() {
  const [showRegister, setShowRegister] = useState(false);

  return (
    <AuthProvider>
      <AppContent showRegister={showRegister} setShowRegister={setShowRegister} />
    </AuthProvider>
  );
}

function AppContent({ showRegister, setShowRegister }) {
  const { user } = useAuth();

  if (!user) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center p-4">
        {showRegister ? (
          <Register onSwitchToLogin={() => setShowRegister(false)} />
        ) : (
          <Login onSwitchToRegister={() => setShowRegister(true)} />
        )}
      </div>
    );
  }

  return <AuthenticatedApp />;
}

export default App;

