import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import { NotificationProvider } from './contexts/NotificationContext';
import ErrorBoundary from './components/ErrorBoundary';
import Toast from './components/Toast';

// Layouts
import StudentLayout from './layouts/StudentLayout';
import TeacherLayout from './layouts/TeacherLayout';
import ParentLayout from './layouts/ParentLayout';
import AdminLayout from './layouts/AdminLayout';

// Auth Pages
import Login from './components/Login';
import Register from './components/Register';

// Student Pages
import StudentProfile from './components/StudentProfile';
import Assessment from './components/Assessment';
import ProgressDashboard from './components/ProgressDashboard';
import SkillPractice from './components/SkillPractice';
import ReviewDashboard from './components/ReviewDashboard';
import ReviewSession from './components/ReviewSession';
import ResourceLibrary from './components/ResourceLibrary';
import AchievementsPage from './components/AchievementsPage';
import LeaderboardPage from './components/LeaderboardPage';
import ProfilePage from './components/ProfilePage';
import FriendsPage from './components/FriendsPage';
import ClassesPage from './components/ClassesPage';
import SharedChallengesPage from './components/SharedChallengesPage';
import ChallengeDetailPage from './components/ChallengeDetailPage';
import SocialFeedPage from './components/SocialFeedPage';

// Teacher Pages
import TeacherDashboard from './components/TeacherDashboard';

// Parent Pages
import ParentDashboard from './components/parent/ParentDashboard';
import ChildProgress from './components/parent/ChildProgress';
import ChildReports from './components/parent/ChildReports';
import ParentMessaging from './components/parent/ParentMessaging';
import GoalManagement from './components/parent/GoalManagement';
import ChildLinking from './components/parent/ChildLinking';
import ParentSettings from './components/parent/ParentSettings';

// Admin Pages
import AdminDashboard from './components/admin/AdminDashboard';
import UserManagement from './components/admin/UserManagement';
import ContentManagement from './components/admin/ContentManagement';
import SystemSettings from './components/admin/SystemSettings';
import AuditLogs from './components/admin/AuditLogs';
import PlatformMetrics from './components/admin/PlatformMetrics';

// Shared Components
import NotFound from './components/shared/NotFound';

// Protected Route Component
const ProtectedRoute = ({ children, allowedRoles = [] }) => {
  const { user, loading } = useAuth();

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading...</p>
        </div>
      </div>
    );
  }

  if (!user) {
    return <Navigate to="/login" replace />;
  }

  if (allowedRoles.length > 0 && !allowedRoles.includes(user.role)) {
    return <Navigate to="/" replace />;
  }

  return children;
};

// Role-based redirect component
const RoleBasedRedirect = () => {
  const { user } = useAuth();

  if (!user) {
    return <Navigate to="/login" replace />;
  }

  switch (user.role) {
    case 'teacher':
      return <Navigate to="/teacher/dashboard" replace />;
    case 'parent':
      return <Navigate to="/parent/dashboard" replace />;
    case 'admin':
      return <Navigate to="/admin/dashboard" replace />;
    default:
      return <Navigate to="/student/dashboard" replace />;
  }
};

function AppRouter() {
  return (
    <ErrorBoundary>
      <BrowserRouter
        future={{
          v7_startTransition: true,
          v7_relativeSplatPath: true
        }}
      >
        <AuthProvider>
          <NotificationProvider>
            <Toast />
            <Routes>
              {/* Public Routes */}
              <Route path="/login" element={<Login />} />
              <Route path="/register" element={<Register />} />

              {/* Root redirect based on role */}
              <Route path="/" element={<RoleBasedRedirect />} />

              {/* Student Routes */}
              <Route
                path="/student/*"
                element={
                  <ProtectedRoute allowedRoles={['student']}>
                    <StudentLayout />
                  </ProtectedRoute>
                }
              >
                <Route path="dashboard" element={<ProgressDashboard />} />
                <Route path="profile-setup" element={<StudentProfile />} />
                <Route path="assessment" element={<Assessment />} />
                <Route path="practice" element={<SkillPractice />} />
                <Route path="reviews" element={<ReviewDashboard />} />
                <Route path="review-session" element={<ReviewSession />} />
                <Route path="resources" element={<ResourceLibrary />} />
                <Route path="achievements" element={<AchievementsPage />} />
                <Route path="leaderboard" element={<LeaderboardPage />} />
                <Route path="profile" element={<ProfilePage />} />
                <Route path="friends" element={<FriendsPage />} />
                <Route path="classes" element={<ClassesPage />} />
                <Route path="challenges" element={<SharedChallengesPage />} />
                <Route path="challenge/:id" element={<ChallengeDetailPage />} />
                <Route path="feed" element={<SocialFeedPage />} />
              </Route>

              {/* Teacher Routes */}
              <Route
                path="/teacher/*"
                element={
                  <ProtectedRoute allowedRoles={['teacher']}>
                    <TeacherLayout />
                  </ProtectedRoute>
                }
              >
                <Route path="dashboard" element={<TeacherDashboard />} />
                <Route path="classes" element={<div>My Classes (Coming Soon)</div>} />
                <Route path="assignments" element={<div>Assignments (Coming Soon)</div>} />
                <Route path="monitoring" element={<div>Student Monitoring (Coming Soon)</div>} />
                <Route path="analytics" element={<div>Analytics (Coming Soon)</div>} />
                <Route path="messages" element={<div>Messages (Coming Soon)</div>} />
                <Route path="interventions" element={<div>Interventions (Coming Soon)</div>} />
              </Route>

              {/* Parent Routes */}
              <Route
                path="/parent/*"
                element={
                  <ProtectedRoute allowedRoles={['parent']}>
                    <ParentLayout />
                  </ProtectedRoute>
                }
              >
                <Route path="dashboard" element={<ParentDashboard />} />
                <Route path="children" element={<ChildLinking />} />
                <Route path="progress" element={<ChildProgress />} />
                <Route path="reports" element={<ChildReports />} />
                <Route path="messages" element={<ParentMessaging />} />
                <Route path="goals" element={<GoalManagement />} />
                <Route path="settings" element={<ParentSettings />} />
              </Route>

              {/* Admin Routes */}
              <Route
                path="/admin/*"
                element={
                  <ProtectedRoute allowedRoles={['admin']}>
                    <AdminLayout />
                  </ProtectedRoute>
                }
              >
                <Route path="dashboard" element={<AdminDashboard />} />
                <Route path="users" element={<UserManagement />} />
                <Route path="content" element={<ContentManagement />} />
                <Route path="settings" element={<SystemSettings />} />
                <Route path="audit" element={<AuditLogs />} />
                <Route path="metrics" element={<PlatformMetrics />} />
              </Route>

              {/* 404 */}
              <Route path="*" element={<NotFound />} />
            </Routes>
          </NotificationProvider>
        </AuthProvider>
      </BrowserRouter>
    </ErrorBoundary>
  );
}

export default AppRouter;

