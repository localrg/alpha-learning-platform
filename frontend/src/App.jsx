import { useState } from 'react';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import Login from './components/Login';
import Register from './components/Register';
import ProtectedRoute from './components/ProtectedRoute';
import { Button } from './components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './components/ui/card';
import './App.css';

function AuthenticatedApp() {
  const { user, logout } = useAuth();

  return (
    <div className="min-h-screen bg-background p-8">
      <div className="max-w-4xl mx-auto">
        <Card>
          <CardHeader>
            <CardTitle>Welcome to Alpha Learning Platform</CardTitle>
            <CardDescription>
              You are logged in as <strong>{user?.username}</strong>
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="p-4 bg-muted rounded-lg">
              <h3 className="font-semibold mb-2">User Information</h3>
              <div className="space-y-1 text-sm">
                <p><strong>Username:</strong> {user?.username}</p>
                <p><strong>Email:</strong> {user?.email || 'Not provided'}</p>
                <p><strong>Account Created:</strong> {new Date(user?.created_at).toLocaleDateString()}</p>
                {user?.last_login && (
                  <p><strong>Last Login:</strong> {new Date(user?.last_login).toLocaleString()}</p>
                )}
              </div>
            </div>

            <div className="p-4 bg-primary/10 rounded-lg">
              <h3 className="font-semibold mb-2">🎉 Authentication Successful!</h3>
              <p className="text-sm text-muted-foreground mb-4">
                You have successfully logged in to the Alpha Learning Platform. 
                The student profile and learning features will be implemented in the next steps.
              </p>
            </div>

            <Button onClick={logout} variant="outline" className="w-full">
              Logout
            </Button>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}

function UnauthenticatedApp() {
  const [showRegister, setShowRegister] = useState(false);

  return (
    <div className="min-h-screen bg-background flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold mb-2">Alpha Learning Platform</h1>
          <p className="text-muted-foreground">
            Master mathematics through personalized, AI-powered learning
          </p>
        </div>

        {showRegister ? (
          <Register onSwitchToLogin={() => setShowRegister(false)} />
        ) : (
          <Login onSwitchToRegister={() => setShowRegister(true)} />
        )}
      </div>
    </div>
  );
}

function AppContent() {
  const { isAuthenticated, loading } = useAuth();

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto mb-4"></div>
          <p className="text-muted-foreground">Loading...</p>
        </div>
      </div>
    );
  }

  return isAuthenticated ? (
    <ProtectedRoute>
      <AuthenticatedApp />
    </ProtectedRoute>
  ) : (
    <UnauthenticatedApp />
  );
}

function App() {
  return (
    <AuthProvider>
      <AppContent />
    </AuthProvider>
  );
}

export default App;

