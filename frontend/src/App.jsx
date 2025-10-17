import React, { useState, useEffect } from 'react';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import Login from './components/Login';
import Register from './components/Register';
import StudentProfile from './components/StudentProfile';
import Assessment from './components/Assessment';
import ProgressDashboard from './components/ProgressDashboard';
import SkillPractice from './components/SkillPractice';
import ProtectedRoute from './components/ProtectedRoute';
import { Button } from './components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './components/ui/card';
import './App.css';

function AuthenticatedApp() {
  const { user, logout } = useAuth();
  const [student, setStudent] = useState(null);
  const [loadingStudent, setLoadingStudent] = useState(true);
  const [currentView, setCurrentView] = useState('dashboard'); // 'dashboard', 'assessment', 'practice'
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
          <div className="flex gap-4">
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

