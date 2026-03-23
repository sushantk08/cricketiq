import React from 'react'
import { Link, useLocation } from 'react-router-dom'
import { motion } from 'framer-motion'
import { Activity, BarChart2, Compass, PlayCircle, Bot } from 'lucide-react'

const navLinks = [
  { name: 'Dashboard', path: '/', icon: Activity },
  { name: 'Matches', path: '/matches', icon: BarChart2 },
  { name: 'Decision Replay', path: '/replay', icon: PlayCircle },
  { name: 'Scenarios', path: '/scenarios', icon: Compass },
  { name: 'AI Analyst', path: '/ai-analyst', icon: Bot },
]

export default function Navbar() {
  const location = useLocation()

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
        {/* Brand Logo with Animation */}
        <motion.div
          whileHover={{ scale: 1.03 }}
          whileTap={{ scale: 0.98 }}
        >
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
        <div style={{ display: 'flex', gap: '8px' }}>
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

                {/* Animated Active Indicator Pill */}
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
        </div>
      </div>
    </nav>
  )
}