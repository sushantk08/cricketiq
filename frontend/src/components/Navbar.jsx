import React from 'react'
import { Link, useLocation } from 'react-router-dom'
import { motion } from 'framer-motion'
import { Activity, BarChart2, Compass, PlayCircle, Bot, LogIn, LogOut, ShieldCheck } from 'lucide-react'
import { useAuth } from '../context/AuthContext'

const navLinks = [
  { name: 'Dashboard', path: '/dashboard', icon: Activity },
  { name: 'Matches', path: '/matches', icon: BarChart2 },
  { name: 'Decision Replay', path: '/replay', icon: PlayCircle },
  { name: 'Scenarios', path: '/scenarios', icon: Compass },
  { name: 'AI Analyst', path: '/ai-analyst', icon: Bot },
]

export default function Navbar() {
  const location = useLocation()
  const { user, logout } = useAuth()

  return (
    <nav style={{
      backgroundColor: 'rgba(17, 26, 46, 0.85)',
      backdropFilter: 'blur(12px)',
      borderBottom: '1px solid var(--border-subtle)',
      position: 'sticky',
      top: 0,
      zIndex: 100,
      padding: '0 24px'
    }}>
      <div style={{
        maxWidth: '1200px',
        margin: '0 auto',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        height: '68px'
      }}>
        {/* Logo */}
        <motion.div whileHover={{ scale: 1.03 }} whileTap={{ scale: 0.98 }}>
          <Link to="/" style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <div style={{
              width: '32px',
              height: '32px',
              borderRadius: '8px',
              background: 'linear-gradient(135deg, #00d2ff, #3b82f6)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              fontWeight: 800,
              color: '#fff'
            }}>
              Q
            </div>
            <span style={{ fontSize: '1.35rem', fontWeight: 800, letterSpacing: '-0.5px' }}>
              Cricket<span style={{ color: 'var(--accent-cyan)' }}>IQ</span>
            </span>
          </Link>
        </motion.div>

        {/* Navigation Links */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          {navLinks.map((link) => {
            const Icon = link.icon
            const isActive = location.pathname === link.path

            return (
              <Link
                key={link.path}
                to={link.path}
                style={{
                  position: 'relative',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '6px',
                  padding: '8px 14px',
                  borderRadius: '8px',
                  fontSize: '0.9rem',
                  fontWeight: 600,
                  color: isActive ? 'var(--accent-cyan)' : 'var(--text-muted)',
                  transition: 'color 0.2s ease'
                }}
              >
                <Icon size={17} />
                {link.name}

                {isActive && (
                  <motion.div
                    layoutId="navbar-indicator"
                    style={{
                      position: 'absolute',
                      inset: 0,
                      borderRadius: '8px',
                      backgroundColor: 'rgba(0, 210, 255, 0.08)',
                      border: '1px solid rgba(0, 210, 255, 0.25)',
                      zIndex: -1
                    }}
                    transition={{ type: 'spring', stiffness: 400, damping: 30 }}
                  />
                )}
              </Link>
            )
          })}

          {/* Admin Portal Tab (Exclusively visible to ADMIN role) */}
          {user && user.role === 'ADMIN' && (
            <Link
              to="/admin"
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '6px',
                padding: '8px 14px',
                borderRadius: '8px',
                fontSize: '0.9rem',
                fontWeight: 700,
                color: location.pathname === '/admin' ? '#ffffff' : 'var(--accent-orange)',
                backgroundColor: location.pathname === '/admin' ? 'var(--accent-orange)' : 'rgba(255, 122, 0, 0.1)',
                border: '1px solid rgba(255, 122, 0, 0.3)',
                transition: 'all 0.2s ease'
              }}
            >
              <ShieldCheck size={16} /> Admin Portal
            </Link>
          )}
        </div>

        {/* User / Auth Indicator */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          {user ? (
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
              <div style={{ textAlign: 'right' }}>
                <div style={{ fontSize: '0.85rem', fontWeight: 700 }}>
                  {user.full_name || user.email}
                </div>
                <span style={{
                  display: 'inline-block',
                  padding: '1px 6px',
                  borderRadius: '4px',
                  backgroundColor: user.role === 'ADMIN'
                    ? 'rgba(255, 122, 0, 0.15)'
                    : user.role === 'COACH'
                    ? 'rgba(59, 130, 246, 0.15)'
                    : 'rgba(0, 210, 255, 0.15)',
                  color: user.role === 'ADMIN'
                    ? 'var(--accent-orange)'
                    : user.role === 'COACH'
                    ? 'var(--accent-blue)'
                    : 'var(--accent-cyan)',
                  fontSize: '0.65rem',
                  fontWeight: 800
                }}>
                  {user.role}
                </span>
              </div>
              <button
                onClick={logout}
                title="Log Out"
                style={{
                  background: 'none',
                  border: '1px solid var(--border-subtle)',
                  borderRadius: '8px',
                  padding: '8px',
                  color: 'var(--text-muted)',
                  cursor: 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  transition: 'border-color 0.2s ease'
                }}
                onMouseEnter={e => e.currentTarget.style.borderColor = 'var(--accent-red)'}
                onMouseLeave={e => e.currentTarget.style.borderColor = 'var(--border-subtle)'}
              >
                <LogOut size={16} />
              </button>
            </div>
          ) : (
            <div style={{ display: 'flex', gap: '8px' }}>
              <Link
                to="/login"
                style={{
                  padding: '8px 14px',
                  borderRadius: '8px',
                  border: '1px solid var(--border-subtle)',
                  fontSize: '0.85rem',
                  fontWeight: 600,
                  color: 'var(--text-main)',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '6px'
                }}
              >
                <LogIn size={15} /> Log In
              </Link>
              <Link
                to="/register"
                className="btn-primary"
                style={{ padding: '8px 14px', fontSize: '0.85rem' }}
              >
                Register
              </Link>
            </div>
          )}
        </div>
      </div>
    </nav>
  )
}