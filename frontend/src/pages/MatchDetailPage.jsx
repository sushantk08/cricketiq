import React, { useEffect, useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import { motion } from 'framer-motion'
import { ArrowLeft, Zap, Shield, Award } from 'lucide-react'
import PageWrapper from '../components/PageWrapper'
import { fetchMatchById, fetchMatchScorecard, fetchMatchTurningPoints } from '../services/api'

export default function MatchDetailPage() {
  const { id } = useParams()
  const [match, setMatch] = useState(null)
  const [scorecard, setScorecard] = useState(null)
  const [turningPoints, setTurningPoints] = useState(null)
  const [activeTab, setActiveTab] = useState('scorecard')
  const [activeInnings, setActiveInnings] = useState(0)

  useEffect(() => {
    fetchMatchById(id).then(setMatch).catch(console.error)
    fetchMatchScorecard(id).then(setScorecard).catch(console.error)
    fetchMatchTurningPoints(id).then(setTurningPoints).catch(console.error)
  }, [id])

  if (!match || !scorecard) {
    return (
      <PageWrapper>
        <p style={{ color: 'var(--text-muted)' }}>Loading match data...</p>
      </PageWrapper>
    )
  }

  const currentInnings = scorecard.innings[activeInnings]

  return (
    <PageWrapper>
      <Link to="/matches" style={{ display: 'inline-flex', alignItems: 'center', gap: '6px', color: 'var(--accent-cyan)', fontSize: '0.9rem', marginBottom: '20px' }}>
        <ArrowLeft size={16} /> Back to Match Center
      </Link>

      {/* Match Banner */}
      <div className="glass-card" style={{ marginBottom: '28px' }}>
        <span style={{ fontSize: '0.8rem', color: 'var(--accent-cyan)', fontWeight: 700, textTransform: 'uppercase' }}>
          {match.match_type} • {match.status}
        </span>
        <h1 style={{ fontSize: '1.8rem', margin: '8px 0 12px 0' }}>{match.title}</h1>
        <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem' }}>
          {match.venue?.name} • Toss won by {match.team1?.name} (elected to {match.toss_decision || 'bat'})
        </p>
      </div>

      {/* Navigation Tabs */}
      <div style={{ display: 'flex', gap: '12px', borderBottom: '1px solid var(--border-subtle)', paddingBottom: '12px', marginBottom: '24px' }}>
        {['scorecard', 'turning-points'].map(tab => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab)}
            style={{
              background: 'none',
              border: 'none',
              color: activeTab === tab ? 'var(--accent-cyan)' : 'var(--text-muted)',
              fontWeight: 700,
              fontSize: '0.95rem',
              cursor: 'pointer',
              padding: '6px 12px',
              borderBottom: activeTab === tab ? '2px solid var(--accent-cyan)' : '2px solid transparent'
            }}
          >
            {tab === 'scorecard' ? 'Scorecard' : 'Critical Turning Points'}
          </button>
        ))}
      </div>

      {/* SCORECARD VIEW */}
      {activeTab === 'scorecard' && currentInnings && (
        <div>
          {/* Innings Selector Pills */}
          <div style={{ display: 'flex', gap: '8px', marginBottom: '20px' }}>
            {scorecard.innings.map((inn, idx) => (
              <button
                key={inn.innings_number}
                onClick={() => setActiveInnings(idx)}
                style={{
                  padding: '8px 16px',
                  borderRadius: '20px',
                  border: activeInnings === idx ? '1px solid var(--accent-cyan)' : '1px solid var(--border-subtle)',
                  backgroundColor: activeInnings === idx ? 'rgba(0, 210, 255, 0.12)' : 'var(--bg-card)',
                  color: activeInnings === idx ? 'var(--accent-cyan)' : 'var(--text-muted)',
                  fontWeight: 600,
                  fontSize: '0.85rem',
                  cursor: 'pointer'
                }}
              >
                {inn.batting_team} ({inn.total_runs}/{inn.total_wickets})
              </button>
            ))}
          </div>

          {/* Batting Table */}
          <div className="glass-card" style={{ marginBottom: '24px', overflowX: 'auto' }}>
            <h3 style={{ fontSize: '1.1rem', marginBottom: '14px', color: 'var(--text-main)' }}>Batting</h3>
            <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left', fontSize: '0.9rem' }}>
              <thead>
                <tr style={{ color: 'var(--text-muted)', borderBottom: '1px solid var(--border-subtle)' }}>
                  <th style={{ padding: '8px' }}>Batter</th>
                  <th style={{ padding: '8px' }}>Dismissal</th>
                  <th style={{ padding: '8px', textAlign: 'right' }}>R</th>
                  <th style={{ padding: '8px', textAlign: 'right' }}>B</th>
                  <th style={{ padding: '8px', textAlign: 'right' }}>4s</th>
                  <th style={{ padding: '8px', textAlign: 'right' }}>6s</th>
                  <th style={{ padding: '8px', textAlign: 'right' }}>SR</th>
                </tr>
              </thead>
              <tbody>
                {currentInnings.batting.map(b => (
                  <tr key={b.player_id} style={{ borderBottom: '1px solid rgba(255,255,255,0.03)' }}>
                    <td style={{ padding: '10px 8px', fontWeight: 600 }}>{b.name}</td>
                    <td style={{ padding: '10px 8px', color: 'var(--text-muted)', fontSize: '0.8rem' }}>{b.dismissal}</td>
                    <td style={{ padding: '10px 8px', textAlign: 'right', fontWeight: 700, color: 'var(--accent-cyan)' }}>{b.runs}</td>
                    <td style={{ padding: '10px 8px', textAlign: 'right' }}>{b.balls}</td>
                    <td style={{ padding: '10px 8px', textAlign: 'right' }}>{b.fours}</td>
                    <td style={{ padding: '10px 8px', textAlign: 'right' }}>{b.sixes}</td>
                    <td style={{ padding: '10px 8px', textAlign: 'right', color: 'var(--text-muted)' }}>{b.strike_rate}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* Bowling Table */}
          <div className="glass-card" style={{ overflowX: 'auto' }}>
            <h3 style={{ fontSize: '1.1rem', marginBottom: '14px', color: 'var(--text-main)' }}>Bowling</h3>
            <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left', fontSize: '0.9rem' }}>
              <thead>
                <tr style={{ color: 'var(--text-muted)', borderBottom: '1px solid var(--border-subtle)' }}>
                  <th style={{ padding: '8px' }}>Bowler</th>
                  <th style={{ padding: '8px', textAlign: 'right' }}>O</th>
                  <th style={{ padding: '8px', textAlign: 'right' }}>M</th>
                  <th style={{ padding: '8px', textAlign: 'right' }}>R</th>
                  <th style={{ padding: '8px', textAlign: 'right' }}>W</th>
                  <th style={{ padding: '8px', textAlign: 'right' }}>Econ</th>
                </tr>
              </thead>
              <tbody>
                {currentInnings.bowling.map(bw => (
                  <tr key={bw.player_id} style={{ borderBottom: '1px solid rgba(255,255,255,0.03)' }}>
                    <td style={{ padding: '10px 8px', fontWeight: 600 }}>{bw.name}</td>
                    <td style={{ padding: '10px 8px', textAlign: 'right' }}>{bw.overs}</td>
                    <td style={{ padding: '10px 8px', textAlign: 'right' }}>{bw.maidens}</td>
                    <td style={{ padding: '10px 8px', textAlign: 'right' }}>{bw.runs_conceded}</td>
                    <td style={{ padding: '10px 8px', textAlign: 'right', fontWeight: 700, color: 'var(--accent-orange)' }}>{bw.wickets}</td>
                    <td style={{ padding: '10px 8px', textAlign: 'right', color: 'var(--text-muted)' }}>{bw.economy}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* TURNING POINTS VIEW */}
      {activeTab === 'turning-points' && turningPoints && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
          {turningPoints.turning_points.map((tp, idx) => (
            <motion.div
              key={idx}
              initial={{ opacity: 0, x: -10 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: idx * 0.05 }}
              className="glass-card"
              style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}
            >
              <div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '6px' }}>
                  <span style={{ fontSize: '0.85rem', fontWeight: 800, color: 'var(--accent-cyan)' }}>
                    OVER {tp.display_over}
                  </span>
                  <span style={{
                    padding: '2px 8px',
                    borderRadius: '10px',
                    fontSize: '0.7rem',
                    fontWeight: 700,
                    backgroundColor: tp.classification === 'CRITICAL_TURNING_POINT' ? 'rgba(239, 68, 68, 0.2)' : 'rgba(255, 122, 0, 0.2)',
                    color: tp.classification === 'CRITICAL_TURNING_POINT' ? 'var(--accent-red)' : 'var(--accent-orange)'
                  }}>
                    {tp.classification.replace(/_/g, ' ')}
                  </span>
                </div>
                <p style={{ fontSize: '0.95rem', fontWeight: 600 }}>{tp.event_summary}</p>
              </div>

              <div style={{ textAlign: 'right' }}>
                <div style={{
                  fontSize: '1.2rem',
                  fontWeight: 800,
                  color: tp.win_prob_delta > 0 ? 'var(--accent-green)' : 'var(--accent-red)'
                }}>
                  {tp.win_prob_delta > 0 ? `+${tp.win_prob_delta}%` : `${tp.win_prob_delta}%`}
                </div>
                <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                  Win Shift: {tp.win_prob_before}% &rarr; {tp.win_prob_after}%
                </span>
              </div>
            </motion.div>
          ))}
        </div>
      )}
    </PageWrapper>
  )
}