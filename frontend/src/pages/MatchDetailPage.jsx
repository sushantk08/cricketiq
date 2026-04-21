import React, { useEffect, useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import { motion } from 'framer-motion'
import { ArrowLeft, Clock, Zap, MapPin } from 'lucide-react'
import PageWrapper from '../components/PageWrapper'
import {
  fetchMatchById,
  fetchMatchScorecard,
  fetchMatchTurningPoints,
  fetchMatchAnalytics,
} from '../services/api'

export default function MatchDetailPage() {
  const { id } = useParams()
  const [match, setMatch] = useState(null)
  const [scorecard, setScorecard] = useState(null)
  const [turningPoints, setTurningPoints] = useState(null)
  const [analytics, setAnalytics] = useState(null)
  const [activeTab, setActiveTab] = useState('scorecard')
  const [activeInnings, setActiveInnings] = useState(0)

  useEffect(() => {
    fetchMatchById(id).then(setMatch).catch(console.error)
    fetchMatchScorecard(id).then(setScorecard).catch(() => setScorecard({ innings: [] }))
    fetchMatchTurningPoints(id).then(setTurningPoints).catch(() => setTurningPoints({ turning_points: [] }))
  }, [id])
    fetchMatchAnalytics(id)
    .then(setAnalytics)
    .catch(() => setAnalytics(null))

  if (!match) {
    return (
      <PageWrapper>
        <p style={{ color: 'var(--text-muted)' }}>Loading match data...</p>
      </PageWrapper>
    )
  }

  const hasDeliveries = scorecard && scorecard.innings && scorecard.innings.length > 0
  const currentInnings = hasDeliveries ? scorecard.innings[activeInnings] : null

  return (
    <PageWrapper>
      <Link to="/matches" style={{ display: 'inline-flex', alignItems: 'center', gap: '6px', color: 'var(--accent-cyan)', fontSize: '0.9rem', marginBottom: '20px' }}>
        <ArrowLeft size={16} /> Back to Match Center
      </Link>

      {/* Match Banner */}
      <div className="glass-card" style={{ marginBottom: '28px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px' }}>
          <span style={{
            padding: '3px 10px',
            borderRadius: '12px',
            fontSize: '0.75rem',
            fontWeight: 800,
            backgroundColor: match.status === 'LIVE' ? 'rgba(239, 68, 68, 0.15)' : 'rgba(16, 185, 129, 0.15)',
            color: match.status === 'LIVE' ? 'var(--accent-red)' : 'var(--accent-green)',
            border: `1px solid ${match.status === 'LIVE' ? 'rgba(239, 68, 68, 0.3)' : 'rgba(16, 185, 129, 0.3)'}`
          }}>
            {match.match_type} • {match.status}
          </span>
        </div>
        
        <h1 style={{ fontSize: '1.8rem', margin: '4px 0 12px 0' }}>{match.title}</h1>
        <div style={{ display: 'flex', alignItems: 'center', gap: '6px', color: 'var(--text-muted)', fontSize: '0.9rem' }}>
          <MapPin size={14} color="var(--accent-cyan)" />
          {match.venue ? `${match.venue.name}, ${match.venue.city}` : 'Venue TBA'}
          {match.toss_decision && ` • Toss won by ${match.team1?.name || 'team'} (elected to ${match.toss_decision})`}
        </div>
      </div>

            {/* Match Summary */}
      <div
        className="glass-card"
        style={{
          marginBottom: '24px',
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))',
          gap: '16px',
        }}
      >
        <div>
          <span style={{ color: 'var(--text-muted)', fontSize: '0.8rem' }}>
            Match
          </span>
          <p style={{ margin: '6px 0 0', fontWeight: 700 }}>
            {match.team1?.short_name} vs {match.team2?.short_name}
          </p>
        </div>

        <div>
          <span style={{ color: 'var(--text-muted)', fontSize: '0.8rem' }}>
            Format
          </span>
          <p style={{ margin: '6px 0 0', fontWeight: 700 }}>
            {match.match_type}
          </p>
        </div>

        <div>
          <span style={{ color: 'var(--text-muted)', fontSize: '0.8rem' }}>
            Result
          </span>
          <p
            style={{
              margin: '6px 0 0',
              fontWeight: 700,
              color: 'var(--accent-green)',
            }}
          >
            {match.winner_id
              ? `${match.winner_id === match.team1?.id ? match.team1?.name : match.team2?.name} won`
              : 'Result unavailable'}
          </p>
        </div>

        <div>
          <span style={{ color: 'var(--text-muted)', fontSize: '0.8rem' }}>
            Date
          </span>
          <p style={{ margin: '6px 0 0', fontWeight: 700 }}>
            {new Date(match.match_date).toLocaleDateString()}
          </p>
        </div>
      </div>

      {/* Navigation Tabs */}
      <div style={{ display: 'flex', gap: '12px', borderBottom: '1px solid var(--border-subtle)', paddingBottom: '12px', marginBottom: '24px' }}>
        {['scorecard', 'analytics', 'turning-points'].map(tab => (
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
            {tab === 'scorecard'
                ? 'Scorecard'
                : tab === 'analytics'
                  ? 'Analytics'
                  : 'Critical Turning Points'}
          </button>
        ))}
      </div>

      {/* ANALYTICS VIEW */}
{activeTab === 'analytics' && (
  <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
    {!analytics || analytics.innings.length === 0 ? (
      <div
        className="glass-card"
        style={{
          textAlign: 'center',
          padding: '48px 24px',
          border: '1px dashed var(--border-subtle)',
        }}
      >
        <h3 style={{ marginBottom: '8px' }}>No Analytics Available</h3>
        <p style={{ color: 'var(--text-muted)' }}>
          Match analytics will appear when innings and delivery data are available.
        </p>
      </div>
    ) : (
      analytics.innings.map((inn) => (
        <div key={inn.innings_number} className="glass-card">
          <h3 style={{ marginBottom: '16px' }}>
            {inn.batting_team} — {inn.runs}/{inn.wickets}
          </h3>

          <div
            style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fit, minmax(140px, 1fr))',
              gap: '12px',
            }}
          >
            <div>
              <span style={{ color: 'var(--text-muted)', fontSize: '0.8rem' }}>
                Run Rate
              </span>
              <p style={{ fontWeight: 800, marginTop: '5px' }}>
                {inn.run_rate}
              </p>
            </div>

            <div>
              <span style={{ color: 'var(--text-muted)', fontSize: '0.8rem' }}>
                4s
              </span>
              <p style={{ fontWeight: 800, marginTop: '5px' }}>
                {inn.fours}
              </p>
            </div>

            <div>
              <span style={{ color: 'var(--text-muted)', fontSize: '0.8rem' }}>
                6s
              </span>
              <p style={{ fontWeight: 800, marginTop: '5px' }}>
                {inn.sixes}
              </p>
            </div>

            <div>
              <span style={{ color: 'var(--text-muted)', fontSize: '0.8rem' }}>
                Dot Balls
              </span>
              <p style={{ fontWeight: 800, marginTop: '5px' }}>
                {inn.dot_ball_percentage}%
              </p>
            </div>

            <div>
              <span style={{ color: 'var(--text-muted)', fontSize: '0.8rem' }}>
                Boundary Balls
              </span>
              <p style={{ fontWeight: 800, marginTop: '5px' }}>
                {inn.boundary_percentage}%
              </p>
            </div>
          </div>

          <h4 style={{ margin: '24px 0 12px' }}>Phase Analysis</h4>

          <div
            style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fit, minmax(160px, 1fr))',
              gap: '12px',
            }}
          >
            {Object.entries(inn.phases).map(([phase, data]) => (
              <div
                key={phase}
                style={{
                  padding: '14px',
                  borderRadius: '8px',
                  background: 'var(--bg-main)',
                  border: '1px solid var(--border-subtle)',
                }}
              >
                <div
                  style={{
                    fontSize: '0.8rem',
                    color: 'var(--accent-cyan)',
                    fontWeight: 700,
                  }}
                >
                  {phase}
                </div>
                <div style={{ marginTop: '8px', fontWeight: 700 }}>
                  {data.runs} runs
                </div>
                <div
                  style={{
                    marginTop: '4px',
                    color: 'var(--text-muted)',
                    fontSize: '0.8rem',
                  }}
                >
                  {data.run_rate} RR · {data.balls} balls
                </div>
              </div>
            ))}
          </div>
        </div>
      ))
    )}
  </div>
)}

      {/* SCORECARD VIEW */}
      {activeTab === 'scorecard' && (
        hasDeliveries && currentInnings ? (
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
        ) : (
          /* Graceful State when match has no deliveries */
          <div className="glass-card" style={{ textAlign: 'center', padding: '48px 24px', border: '1px dashed var(--border-subtle)' }}>
            <Clock size={36} color="var(--accent-cyan)" style={{ margin: '0 auto 12px auto' }} />
            <h3 style={{ fontSize: '1.25rem', marginBottom: '8px' }}>Fixture Scheduled / Awaiting Delivery Data</h3>
            <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem', maxWidth: '520px', margin: '0 auto 20px auto', lineHeight: 1.5 }}>
              This match was synchronized from the live cricket feed. Full ball-by-ball scorecards and player analytics will populate as deliveries are recorded.
            </p>
            <Link to="/matches/1" className="btn-primary" style={{ display: 'inline-flex' }}>
              View Sample Match Scorecard (India vs Australia) &rarr;
            </Link>
          </div>
        )
      )}

      {/* TURNING POINTS VIEW */}
      {activeTab === 'turning-points' && (
        turningPoints && turningPoints.turning_points && turningPoints.turning_points.length > 0 ? (
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
        ) : (
          <div className="glass-card" style={{ textAlign: 'center', padding: '48px 24px', border: '1px dashed var(--border-subtle)' }}>
            <Zap size={36} color="var(--accent-orange)" style={{ margin: '0 auto 12px auto' }} />
            <h3 style={{ fontSize: '1.25rem', marginBottom: '8px' }}>No Turning Points Available</h3>
            <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem', maxWidth: '480px', margin: '0 auto 20px auto' }}>
              Turning point detection evaluates probability shifts during the 2nd innings chase.
            </p>
            <Link to="/matches/1" className="btn-primary" style={{ display: 'inline-flex' }}>
              View India vs Australia Turning Points &rarr;
            </Link>
          </div>
        )
      )}
    </PageWrapper>
  )
}