import React, { lazy, Suspense } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './contexts/AuthContext';
import { ThemeProvider } from './contexts/ThemeContext';
import { ProtectedRoute } from './components/auth/ProtectedRoute';
import { DashboardLayout } from './layouts/DashboardLayout';
import { LoadingSpinner } from './components/common/LoadingSpinner';

// Route-based code splitting using React.lazy() for pages
const LoginPage = lazy(() => import('./pages/LoginPage').then(m => ({ default: m.LoginPage })));
const RegisterPage = lazy(() => import('./pages/RegisterPage').then(m => ({ default: m.RegisterPage })));
const ProfilePage = lazy(() => import('./pages/ProfilePage').then(m => ({ default: m.ProfilePage })));
const DashboardOverview = lazy(() => import('./pages/DashboardOverview').then(m => ({ default: m.DashboardOverview })));
const WorkspacePage = lazy(() => import('./pages/WorkspacePage').then(m => ({ default: m.WorkspacePage })));
const AIStudioPage = lazy(() => import('./pages/AIStudioPage').then(m => ({ default: m.AIStudioPage })));
const ProjectGeneratorPage = lazy(() => import('./pages/ProjectGeneratorPage').then(m => ({ default: m.ProjectGeneratorPage })));
const AIChatPage = lazy(() => import('./pages/AIChatPage').then(m => ({ default: m.AIChatPage })));
const WorkflowsPage = lazy(() => import('./pages/WorkflowsPage').then(m => ({ default: m.WorkflowsPage })));
const SettingsPage = lazy(() => import('./pages/SettingsPage').then(m => ({ default: m.SettingsPage })));
const NotFoundPage = lazy(() => import('./pages/NotFoundPage').then(m => ({ default: m.NotFoundPage })));

export function App() {
  return (
    <AuthProvider>
      <ThemeProvider>
        <BrowserRouter>
          <Suspense fallback={<div className="h-screen w-screen flex items-center justify-center bg-zinc-950"><LoadingSpinner label="Loading Workspace..." /></div>}>
            <Routes>
              {/* Public Authentication Routes */}
              <Route path="/login" element={<LoginPage />} />
              <Route path="/register" element={<RegisterPage />} />

              {/* Protected Workspace Routes */}
              <Route element={<ProtectedRoute />}>
                <Route path="/" element={<DashboardLayout />}>
                  <Route index element={<DashboardOverview />} />
                  <Route path="workspace" element={<WorkspacePage />} />
                  <Route path="ai-studio" element={<AIStudioPage />} />
                  <Route path="project-generator" element={<ProjectGeneratorPage />} />
                  <Route path="chat" element={<AIChatPage />} />
                  <Route path="workflows" element={<WorkflowsPage />} />
                  <Route path="profile" element={<ProfilePage />} />
                  <Route path="settings" element={<SettingsPage />} />
                  <Route path="404" element={<NotFoundPage />} />
                  <Route path="*" element={<Navigate to="/404" replace />} />
                </Route>
              </Route>
            </Routes>
          </Suspense>
        </BrowserRouter>
      </ThemeProvider>
    </AuthProvider>
  );
}

export default App;
