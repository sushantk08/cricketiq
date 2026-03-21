import React from 'react'

function App() {
  return (
    <div style={{ fontFamily: 'Segoe UI, Tahoma, Geneva, Verdana, sans-serif', maxWidth: '900px', margin: '40px auto', padding: '24px' }}>
      <header style={{ borderBottom: '2px solid #1e3a8a', paddingBottom: '16px', marginBottom: '24px' }}>
        <h1 style={{ color: '#1e3a8a', margin: 0, fontSize: '2.4rem' }}>CricketIQ</h1>
        <p style={{ color: '#4b5563', margin: '8px 0 0 0', fontSize: '1.1rem' }}>
          AI-Powered Cricket Strategy, Performance & Decision Intelligence Platform
        </p>
      </header>

      <main style={{ backgroundColor: '#f8fafc', border: '1px solid #e2e8f0', borderRadius: '8px', padding: '24px' }}>
        <h2 style={{ color: '#0f172a', marginTop: 0 }}>Frontend Environment Initialized</h2>
        <p style={{ color: '#334155' }}>
          Vite, React, and React Router are configured and ready to connect to the CricketIQ FastAPI backend.
        </p>
      </main>
    </div>
  )
}

export default App