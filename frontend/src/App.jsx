import React from 'react'
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import { AuthProvider } from './context/AuthContext'
import Navbar from './components/Navbar'
import ProtectedRoute from './components/ProtectedRoute'
import HomePage from './pages/HomePage'
import DashboardPage from './pages/DashboardPage'
import MatchesPage from './pages/MatchesPage'
import MatchDetailPage from './pages/MatchDetailPage'
import DecisionReplayPage from './pages/DecisionReplayPage'
import ScenarioSimulatorPage from './pages/ScenarioSimulatorPage'
import AIAnalystPage from './pages/AIAnalystPage'
import LoginPage from './pages/LoginPage'
import RegisterPage from './pages/RegisterPage'
import AdminVerificationsPage from './pages/AdminVerificationsPage'
import PlayersPage from './pages/PlayersPage'
import TeamsPage from './pages/TeamsPage'

function App() {
  return (
    <AuthProvider>
      <Router>
        <Navbar />
        <Routes>
          {/* Public Routes */}
          <Route path="/" element={<HomePage />} />
          <Route path="/matches" element={<MatchesPage />} />
          <Route path="/matches/:id" element={<MatchDetailPage />} />
          <Route path="/login" element={<LoginPage />} />
          <Route path="/register" element={<RegisterPage />} />

          <Route
            path="/dashboard"
            element={
                     <ProtectedRoute>
                     <DashboardPage />
                     </ProtectedRoute>
                    }
          />

          <Route
            path="/players"
            element={
                     <ProtectedRoute>
                      <PlayersPage />
                      </ProtectedRoute>
                    }
          />

          <Route
            path="/teams"
            element={
                     <ProtectedRoute>
                      <TeamsPage />
                     </ProtectedRoute>
                    }
          />

          {/* Analytical Routes */}
          <Route
            path="/replay"
            element={
              <ProtectedRoute allowedRoles={['ANALYST', 'COACH', 'ADMIN']}>
                <DecisionReplayPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/scenarios"
            element={
              <ProtectedRoute allowedRoles={['ANALYST', 'COACH', 'ADMIN']}>
                <ScenarioSimulatorPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/ai-analyst"
            element={
              <ProtectedRoute allowedRoles={['ANALYST', 'COACH', 'ADMIN']}>
                <AIAnalystPage />
              </ProtectedRoute>
            }
          />

          {/* Admin Verification Portal (ADMIN Only) */}
          <Route
            path="/admin"
            element={
              <ProtectedRoute allowedRoles={['ADMIN']}>
                <AdminVerificationsPage />
              </ProtectedRoute>
            }
          />
        </Routes>
      </Router>
    </AuthProvider>
  )
}

export default App