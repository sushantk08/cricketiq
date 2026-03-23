import React from 'react'
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import Navbar from './components/Navbar'
import HomePage from './pages/HomePage'

function App() {
  return (
    <Router>
      <Navbar />
      <Routes>
        <Route path="/" element={<HomePage />} />
        {/* Future multipage modules will mount here */}
        <Route path="/matches" element={<HomePage />} />
        <Route path="/replay" element={<HomePage />} />
        <Route path="/scenarios" element={<HomePage />} />
        <Route path="/ai-analyst" element={<HomePage />} />
      </Routes>
    </Router>
  )
}

export default App