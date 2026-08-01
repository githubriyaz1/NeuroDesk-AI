import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './contexts/AuthContext';
import { ThemeProvider } from './contexts/ThemeContext';
import { ProtectedRoute } from './components/auth/ProtectedRoute';
import { DashboardLayout } from './layouts/DashboardLayout';

import { LoginPage } from './pages/LoginPage';
import { RegisterPage } from './pages/RegisterPage';
import { ProfilePage } from './pages/ProfilePage';
import { DashboardOverview } from './pages/DashboardOverview';
import { WorkspacePage } from './pages/WorkspacePage';
import { AIStudioPage } from './pages/AIStudioPage';
import { ProjectGeneratorPage } from './pages/ProjectGeneratorPage';
import { AIChatPage } from './pages/AIChatPage';
import { WorkflowsPage } from './pages/WorkflowsPage';
import { SettingsPage } from './pages/SettingsPage';
import { NotFoundPage } from './pages/NotFoundPage';

export function App() {
  return (
    <AuthProvider>
      <ThemeProvider>
        <BrowserRouter>
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
        </BrowserRouter>
      </ThemeProvider>
    </AuthProvider>
  );
}

export default App;
