import { useState, useEffect } from 'react';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import Login from './components/Login';
import Register from './components/Register';
import StudentProfile from './components/StudentProfile';
import Assessment from './components/Assessment';
import ProtectedRoute from './components/ProtectedRoute';
import { Button } from './components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './components/ui/card';
import './App.css';

function AuthenticatedApp() {
  const { user, logout } = useAuth();
  const [student, setStudent] = useState(null);
  const [loadingStudent, setLoadingStudent] = useState(true);
  const [showAssessment, setShowAssessment] = useState(false);

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
    setShowAssessment(true);
  };

  const handleAssessmentComplete = () => {
    setShowAssessment(false);
    // Refresh student data or navigate to learning dashboard
  };

  if (loadingStudent) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto mb-4"></div>
          <p className="text-gray-600">Loading...</p>
        </div>
      </div>
    );
  }

  // If no student profile, show profile creation
  if (!student) {
    return (
      <div className="min-h-screen bg-gray-50 p-4">
        <div className="max-w-4xl mx-auto py-8">
          <StudentProfile onProfileCreated={handleProfileCreated} />
        </div>
      </div>
    );
  }

  // If student profile exists but assessment not taken, show assessment
  if (showAssessment) {
    return (
      <div className="min-h-screen bg-gray-50">
        <header className="bg-white shadow-sm">
          <div className="max-w-7xl mx-auto px-4 py-4 flex justify-between items-center">
            <h1 className="text-2xl font-bold text-gray-900">Alpha Learning Platform</h1>
            <Button variant="outline" onClick={logout}>Logout</Button>
          </div>
        </header>
        <main className="max-w-7xl mx-auto px-4 py-8">
          <Assessment onComplete={handleAssessmentComplete} />
        </main>
      </div>
    );
  }

  // Main dashboard (after assessment)
  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 py-4 flex justify-between items-center">
          <h1 className="text-2xl font-bold text-gray-900">Alpha Learning Platform</h1>
          <Button variant="outline" onClick={logout}>Logout</Button>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 py-8">
        <div className="space-y-6">
          {/* Welcome Section */}
          <Card>
            <CardHeader>
              <CardTitle>Welcome back, {student.name}! 👋</CardTitle>
              <CardDescription>Grade {student.grade}</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="p-4 bg-blue-50 rounded-lg">
                  <h3 className="font-semibold text-blue-900">Skills Mastered</h3>
                  <p className="text-3xl font-bold text-blue-600 mt-2">0</p>
                </div>
                <div className="p-4 bg-green-50 rounded-lg">
                  <h3 className="font-semibold text-green-900">Current Streak</h3>
                  <p className="text-3xl font-bold text-green-600 mt-2">0 days</p>
                </div>
                <div className="p-4 bg-purple-50 rounded-lg">
                  <h3 className="font-semibold text-purple-900">Time Saved</h3>
                  <p className="text-3xl font-bold text-purple-600 mt-2">0 min</p>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Quick Actions */}
          <Card>
            <CardHeader>
              <CardTitle>Quick Actions</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <Button 
                onClick={() => setShowAssessment(true)}
                className="w-full"
                size="lg"
              >
                Take Assessment
              </Button>
              <Button 
                variant="outline"
                className="w-full"
                size="lg"
                disabled
              >
                Start Learning Session (Coming Soon)
              </Button>
            </CardContent>
          </Card>

          {/* Student Profile */}
          <Card>
            <CardHeader>
              <CardTitle>Your Profile</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                <div className="flex justify-between">
                  <span className="text-gray-600">Name:</span>
                  <span className="font-semibold">{student.name}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Grade:</span>
                  <span className="font-semibold">{student.grade}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Joined:</span>
                  <span className="font-semibold">
                    {new Date(student.created_at).toLocaleDateString()}
                  </span>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Account Information */}
          <Card>
            <CardHeader>
              <CardTitle>Account Information</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                <div className="flex justify-between">
                  <span className="text-gray-600">Username:</span>
                  <span className="font-semibold">{user.username}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Email:</span>
                  <span className="font-semibold">{user.email || 'Not provided'}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Last Login:</span>
                  <span className="font-semibold">
                    {new Date(user.last_login).toLocaleString()}
                  </span>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </main>
    </div>
  );
}

function App() {
  return (
    <AuthProvider>
      <AppContent />
    </AuthProvider>
  );
}

function AppContent() {
  const { isAuthenticated, loading } = useAuth();

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto mb-4"></div>
          <p className="text-gray-600">Loading...</p>
        </div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Login />;
  }

  return <AuthenticatedApp />;
}

export default App;

