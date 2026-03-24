import React, { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { motion } from 'framer-motion'
import { Calendar, MapPin, Trophy, ArrowRight } from 'lucide-react'
import PageWrapper from '../components/PageWrapper'
import { fetchMatches } from '../services/api'

export default function MatchesPage() {
  const [matches, setMatches] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchMatches()
      .then(data => {
        setMatches(data)
        setLoading(false)
      })
      .catch(err => {
        console.error(err)
        setLoading(false)
      })
  }, [])

  return (
    <PageWrapper>
      <div style={{ marginBottom: '32px' }}>
        <h1 style={{ fontSize: '2rem', fontWeight: 800, marginBottom: '8px' }}>Match Center</h1>
        <p style={{ color: 'var(--text-muted)' }}>Browse active fixtures, completed tournament matches, and tactical telemetry.</p>
      </div>

      {loading ? (
        <p style={{ color: 'var(--text-muted)' }}>Loading matches...</p>
      ) : matches.length === 0 ? (
        <p style={{ color: 'var(--text-muted)' }}>No matches found in database.</p>
      ) : (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(340px, 1fr))', gap: '20px' }}>
          {matches.map((m, idx) => (
            <motion.div
              key={m.id}
              initial={{ opacity: 0, y: 15 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: idx * 0.05 }}
              whileHover={{ y: -4 }}
              className="glass-card"
              style={{ display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}
            >
              <div>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '14px' }}>
                  <span style={{
                    padding: '4px 10px',
                    borderRadius: '12px',
                    fontSize: '0.75rem',
                    fontWeight: 700,
                    backgroundColor: m.status === 'LIVE' ? 'rgba(239, 68, 68, 0.15)' : 'rgba(16, 185, 129, 0.15)',
                    color: m.status === 'LIVE' ? 'var(--accent-red)' : 'var(--accent-green)',
                    border: `1px solid ${m.status === 'LIVE' ? 'rgba(239, 68, 68, 0.3)' : 'rgba(16, 185, 129, 0.3)'}`
                  }}>
                    {m.status}
                  </span>
                  <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)', fontWeight: 600 }}>{m.match_type}</span>
                </div>

                <h3 style={{ fontSize: '1.15rem', fontWeight: 700, marginBottom: '16px' }}>{m.title}</h3>

                <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', marginBottom: '20px', color: 'var(--text-muted)', fontSize: '0.85rem' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                    <MapPin size={14} color="var(--accent-cyan)" />
                    {m.venue ? `${m.venue.name}, ${m.venue.city}` : 'Venue TBA'}
                  </div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                    <Calendar size={14} color="var(--accent-blue)" />
                    {new Date(m.match_date).toLocaleDateString()}
                  </div>
                </div>
              </div>

              <Link
                to={`/matches/${m.id}`}
                className="btn-primary"
                style={{ width: '100%', justifyContent: 'center', fontSize: '0.85rem' }}
              >
                View Scorecard & Analytics <ArrowRight size={15} />
              </Link>
            </motion.div>
          ))}
        </div>
      )}
    </PageWrapper>
  )
}