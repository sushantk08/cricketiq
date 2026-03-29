import React from 'react'
import { Navigate, useLocation } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

export default function ProtectedRoute({ children, allowedRoles }) {
  const { user, loading } = useAuth()
  const location = useLocation()

  if (loading) {
    return (
      <div style={{ padding: '60px', textAlign: 'center', color: 'var(--text-muted)' }}>
        Verifying authentication credentials...
      </div>
    )
  }

  // Not logged in -> redirect to login with return path
  if (!user) {
    return <Navigate to="/login" state={{ from: location }} replace />
  }

  // Check role authorization
  if (allowedRoles && !allowedRoles.includes(user.role)) {
    return (
      <div style={{ maxWidth: '600px', margin: '60px auto', padding: '32px', textAlign: 'center' }} className="glass-card">
        <h2 style={{ color: 'var(--accent-red)', marginBottom: '12px' }}>Access Restricted</h2>
        <p style={{ color: 'var(--text-muted)', fontSize: '0.95rem', lineHeight: 1.6 }}>
          Your current platform role (<strong style={{ color: 'var(--accent-cyan)' }}>{user.role}</strong>) does not have permission to access this analytical feature.
        </p>
      </div>
    )
  }

  return children
}