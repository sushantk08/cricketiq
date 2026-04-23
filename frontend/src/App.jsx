import React from 'react'
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import { AuthProvider } from './context/AuthContext'

import Navbar from './components/Navbar'
import ProtectedRoute from './components/ProtectedRoute'

import HomePage from './pages/HomePage'
import DashboardPage from './pages/DashboardPage'
import MatchesPage from './pages/MatchesPage'
import MatchDetailPage from './pages/MatchDetailPage'
import PlayersPage from './pages/PlayersPage'
import PlayerDetailPage from './pages/PlayerDetailPage'
import TeamsPage from './pages/TeamsPage'
import TeamDetailPage from './pages/TeamDetailPage'

import LoginPage from './pages/LoginPage'
import RegisterPage from './pages/RegisterPage'

import StrategyPage from './pages/StrategyPage'
import DecisionReplayPage from './pages/DecisionReplayPage'
import ScenarioSimulatorPage from './pages/ScenarioSimulatorPage'
import AIAnalystPage from './pages/AIAnalystPage'

import AdminVerificationsPage from './pages/AdminVerificationsPage'

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

          {/* Protected Routes */}
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
            path="/players/:id"
            element={
              <ProtectedRoute>
                <PlayerDetailPage />
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

          <Route
            path="/teams/:id"
            element={
              <ProtectedRoute>
                <TeamDetailPage />
              </ProtectedRoute>
            }
          />

          {/* Analytical Routes */}
          <Route
            path="/strategy"
            element={
              <ProtectedRoute allowedRoles={['ANALYST', 'COACH', 'ADMIN']}>
                <StrategyPage />
              </ProtectedRoute>
            }
          />

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

          {/* Admin Routes */}
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