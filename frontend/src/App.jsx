import React from 'react'
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import Navbar from './components/Navbar'
import HomePage from './pages/HomePage'
import MatchesPage from './pages/MatchesPage'
import MatchDetailPage from './pages/MatchDetailPage'
import DecisionReplayPage from './pages/DecisionReplayPage'
import ScenarioSimulatorPage from './pages/ScenarioSimulatorPage'
import AIAnalystPage from './pages/AIAnalystPage'

function App() {
  return (
    <Router>
      <Navbar />
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/matches" element={<MatchesPage />} />
        <Route path="/matches/:id" element={<MatchDetailPage />} />
        <Route path="/replay" element={<DecisionReplayPage />} />
        <Route path="/scenarios" element={<ScenarioSimulatorPage />} />
        <Route path="/ai-analyst" element={<AIAnalystPage />} />
      </Routes>
    </Router>
  )
}

export default App