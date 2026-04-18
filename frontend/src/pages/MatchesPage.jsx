import React, { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { motion } from 'framer-motion'
import { Calendar, MapPin, Radio, ArrowRight, RefreshCw } from 'lucide-react'
import PageWrapper from '../components/PageWrapper'
import { fetchMatches, fetchLiveScores } from '../services/api'

export default function MatchesPage() {
  const [matches, setMatches] = useState([])
  const [liveScores, setLiveScores] = useState([])
  const [loading, setLoading] = useState(true)
  const [refreshingLive, setRefreshingLive] = useState(false)

  const loadData = () => {
    Promise.all([fetchMatches(), fetchLiveScores()])
      .then(([dbMatches, liveData]) => {
        setMatches(dbMatches)
        setLiveScores(liveData)
        setLoading(false)
        setRefreshingLive(false)
      })
      .catch(err => {
        console.error(err)
        setLoading(false)
        setRefreshingLive(false)
      })
  }

    useEffect(() => {
    loadData()

    const interval = setInterval(() => {
      fetchLiveScores()
        .then(setLiveScores)
        .catch(err => console.error('Live score refresh failed:', err))
    }, 30000)

    return () => clearInterval(interval)
  }, [])

  const activeLiveScores = liveScores.filter(
    (match) => match.match_started && !match.match_ended
  )

  const handleRefresh = () => {
    setRefreshingLive(true)
    loadData()
  }

  return (
    <PageWrapper>
      <div style={{ marginBottom: '32px', display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '16px' }}>
        <div>
          <h1 style={{ fontSize: '2rem', fontWeight: 800, marginBottom: '8px' }}>Match Center & Live Scores</h1>
          <p style={{ color: 'var(--text-muted)' }}>Real-time CricAPI scores and historical analytical telemetry.</p>
        </div>
        <button onClick={handleRefresh} disabled={refreshingLive} className="btn-primary" style={{ fontSize: '0.85rem' }}>
          <RefreshCw size={14} className={refreshingLive ? 'animate-spin' : ''} />
          {refreshingLive ? 'Updating Scores...' : 'Refresh Live Scores'}
        </button>
      </div>

      {/* LIVE CRICKET SCORES SECTION (From CricAPI) */}
      <div style={{ marginBottom: '40px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '16px' }}>
          <Radio size={18} color="var(--accent-red)" className="animate-pulse" />
          <h2 style={{ fontSize: '1.25rem', fontWeight: 700 }}>Live CricAPI Feed</h2>
        </div>

        {activeLiveScores.length === 0 ? (
          <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem' }}>No live matches currently in progress.</p>
        ) : (
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(340px, 1fr))', gap: '18px' }}>
            {activeLiveScores.map((m, idx) => (
              <motion.div
                key={m.external_id || idx}
                initial={{ opacity: 0, y: 12 }}
                animate={{ opacity: 1, y: 0 }}
                className="glass-card"
                style={{ border: '1px solid rgba(239, 68, 68, 0.35)', backgroundColor: 'rgba(17, 26, 46, 0.95)' }}
              >
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '10px' }}>
                  <span style={{
                    padding: '2px 8px',
                    borderRadius: '10px',
                    fontSize: '0.7rem',
                    fontWeight: 800,
                    backgroundColor: 'rgba(239, 68, 68, 0.2)',
                    color: 'var(--accent-red)',
                    display: 'inline-flex',
                    alignItems: 'center',
                    gap: '4px'
                  }}>
                    ● {m.status}
                  </span>
                  <span style={{ fontSize: '0.8rem', fontWeight: 600, color: 'var(--accent-cyan)' }}>{m.match_type}</span>
                </div>

                <h3 style={{ fontSize: '1.05rem', fontWeight: 700, marginBottom: '12px' }}>{m.title}</h3>

                {/* Parsed Live Score */}
                <div style={{
                  backgroundColor: 'var(--bg-main)',
                  padding: '12px',
                  borderRadius: '8px',
                  marginBottom: '12px',
                  border: '1px solid var(--border-subtle)'
                }}>
                  <div style={{ fontSize: '1.1rem', fontWeight: 800, color: 'var(--text-main)', marginBottom: '4px' }}>
                    {m.formatted_score}
                  </div>
                  {m.status_note && (
                    <div style={{ fontSize: '0.8rem', color: 'var(--accent-orange)' }}>
                      {m.status_note}
                    </div>
                  )}
                </div>

                <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                  <MapPin size={13} color="var(--accent-cyan)" />
                  {m.venue_name}
                </div>
              </motion.div>
            ))}
          </div>
        )}
      </div>

      {/* STORED TOURNAMENT MATCHES & ANALYTICAL FIXTURES */}
      <div>
        <h2 style={{ fontSize: '1.25rem', fontWeight: 700, marginBottom: '16px' }}>Stored Match Fixtures & Telemetry</h2>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(340px, 1fr))', gap: '20px' }}>
          {matches.map((m, idx) => (
            <motion.div
              key={m.id}
              initial={{ opacity: 0, y: 15 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: idx * 0.04 }}
              whileHover={{ y: -3 }}
              className="glass-card"
              style={{ display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}
            >
              <div>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px' }}>
                  <span style={{
                    padding: '3px 8px',
                    borderRadius: '10px',
                    fontSize: '0.7rem',
                    fontWeight: 700,
                    backgroundColor: m.status === 'LIVE' ? 'rgba(239, 68, 68, 0.15)' : 'rgba(16, 185, 129, 0.15)',
                    color: m.status === 'LIVE' ? 'var(--accent-red)' : 'var(--accent-green)',
                  }}>
                    {m.status}
                  </span>
                  <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)', fontWeight: 600 }}>{m.match_type}</span>
                </div>

                <h3 style={{ fontSize: '1.05rem', fontWeight: 700, marginBottom: '14px' }}>{m.title}</h3>

                <div style={{ display: 'flex', flexDirection: 'column', gap: '6px', marginBottom: '18px', color: 'var(--text-muted)', fontSize: '0.8rem' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                    <MapPin size={13} color="var(--accent-cyan)" />
                    {m.venue ? `${m.venue.name}, ${m.venue.city}` : 'Venue TBA'}
                  </div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                    <Calendar size={13} color="var(--accent-blue)" />
                    {new Date(m.match_date).toLocaleDateString()}
                  </div>
                </div>
              </div>

              <Link
                to={`/matches/${m.id}`}
                className="btn-primary"
                style={{ width: '100%', justifyContent: 'center', fontSize: '0.85rem' }}
              >
                View Scorecard & Analytics <ArrowRight size={14} />
              </Link>
            </motion.div>
          ))}
        </div>
      </div>
    </PageWrapper>
  )
}