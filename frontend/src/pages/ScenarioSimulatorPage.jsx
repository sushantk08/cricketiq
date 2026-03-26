import React, { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { Compass, TrendingUp, AlertTriangle, Shield, CheckCircle, RefreshCw } from 'lucide-react'
import PageWrapper from '../components/PageWrapper'
import { simulateScenario } from '../services/api'

export default function ScenarioSimulatorPage() {
  const [score, setScore] = useState(138)
  const [overs, setOvers] = useState(16.0)
  const [wickets, setWickets] = useState(5)
  const [isChasing, setIsChasing] = useState(true)
  const [target, setTarget] = useState(185)
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)

  const runSimulation = async () => {
    setLoading(true)
    try {
      const payload = {
        current_score: Number(score),
        overs_completed: Number(overs),
        wickets_lost: Number(wickets),
        target_runs: isChasing ? Number(target) : null,
        total_overs: 20
      }
      const data = await simulateScenario(payload)
      setResult(data)
    } catch (err) {
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  // Auto-simulate on initial render
  useEffect(() => {
    runSimulation()
  }, [])

  const getRiskColor = (risk) => {
    switch (risk) {
      case 'LOW': return 'var(--accent-green)'
      case 'MODERATE': return 'var(--accent-cyan)'
      case 'HIGH': return 'var(--accent-orange)'
      case 'EXTREME': return 'var(--accent-red)'
      default: return 'var(--text-muted)'
    }
  }

  return (
    <PageWrapper>
      <div style={{ marginBottom: '28px' }}>
        <div style={{ display: 'inline-flex', alignItems: 'center', gap: '6px', color: 'var(--accent-green)', fontWeight: 700, fontSize: '0.85rem', marginBottom: '8px' }}>
          <Compass size={16} /> Interactive Strategy Sandbox
        </div>
        <h1 style={{ fontSize: '2.2rem', fontWeight: 800 }}>Scenario Simulator</h1>
        <p style={{ color: 'var(--text-muted)' }}>
          Adjust score, overs, wickets, and chase targets to recalculate trajectories, win likelihood, and tactical risk in real time.
        </p>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: '24px', marginBottom: '32px' }}>
        {/* Control Panel */}
        <div className="glass-card">
          <h3 style={{ fontSize: '1.15rem', marginBottom: '20px', color: 'var(--accent-green)' }}>
            Match Variables
          </h3>

          {/* Score Input */}
          <div style={{ marginBottom: '18px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '6px', fontSize: '0.9rem', fontWeight: 600 }}>
              <span>Current Score:</span>
              <span style={{ color: 'var(--accent-cyan)' }}>{score} Runs</span>
            </div>
            <input
              type="range"
              min="0"
              max="250"
              value={score}
              onChange={e => setScore(e.target.value)}
              style={{ width: '100%', accentColor: 'var(--accent-cyan)' }}
            />
          </div>

          {/* Overs Input */}
          <div style={{ marginBottom: '18px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '6px', fontSize: '0.9rem', fontWeight: 600 }}>
              <span>Overs Completed:</span>
              <span style={{ color: 'var(--accent-blue)' }}>{overs} / 20.0</span>
            </div>
            <input
              type="range"
              min="0.0"
              max="19.5"
              step="0.1"
              value={overs}
              onChange={e => setOvers(e.target.value)}
              style={{ width: '100%', accentColor: 'var(--accent-blue)' }}
            />
          </div>

          {/* Wickets Input */}
          <div style={{ marginBottom: '22px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '6px', fontSize: '0.9rem', fontWeight: 600 }}>
              <span>Wickets Fallen:</span>
              <span style={{ color: 'var(--accent-orange)' }}>{wickets} / 10</span>
            </div>
            <input
              type="range"
              min="0"
              max="10"
              value={wickets}
              onChange={e => setWickets(e.target.value)}
              style={{ width: '100%', accentColor: 'var(--accent-orange)' }}
            />
          </div>

          {/* Chase Toggle */}
          <div style={{ marginBottom: '20px', padding: '14px', backgroundColor: 'var(--bg-main)', borderRadius: '8px', border: '1px solid var(--border-subtle)' }}>
            <label style={{ display: 'flex', alignItems: 'center', gap: '8px', cursor: 'pointer', fontSize: '0.9rem', fontWeight: 600, marginBottom: isChasing ? '12px' : '0' }}>
              <input
                type="checkbox"
                checked={isChasing}
                onChange={e => setIsChasing(e.target.checked)}
                style={{ width: '16px', height: '16px', accentColor: 'var(--accent-green)' }}
              />
              2nd Innings Run Chase
            </label>

            {isChasing && (
              <div>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '6px', fontSize: '0.85rem' }}>
                  <span style={{ color: 'var(--text-muted)' }}>Target Runs:</span>
                  <span style={{ fontWeight: 700 }}>{target}</span>
                </div>
                <input
                  type="number"
                  min="1"
                  max="300"
                  value={target}
                  onChange={e => setTarget(e.target.value)}
                  style={{
                    width: '100%',
                    padding: '8px 10px',
                    borderRadius: '6px',
                    backgroundColor: 'var(--bg-card)',
                    border: '1px solid var(--border-subtle)',
                    color: 'var(--text-main)',
                    fontSize: '0.9rem'
                  }}
                />
              </div>
            )}
          </div>

          <button
            onClick={runSimulation}
            disabled={loading}
            className="btn-primary"
            style={{ width: '100%', justifyContent: 'center', padding: '12px' }}
          >
            {loading ? <RefreshCw size={16} className="animate-spin" /> : <Compass size={16} />}
            Recalculate Trajectory
          </button>
        </div>

        {/* Results Dashboard */}
        {result && (
          <motion.div
            key={`${score}-${overs}-${wickets}-${target}-${isChasing}`}
            initial={{ opacity: 0, scale: 0.98 }}
            animate={{ opacity: 1, scale: 1 }}
            className="glass-card"
            style={{ display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}
          >
            <div>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px', borderBottom: '1px solid var(--border-subtle)', paddingBottom: '14px' }}>
                <span style={{ fontSize: '0.8rem', fontWeight: 800, color: 'var(--text-muted)', textTransform: 'uppercase' }}>
                  Trajectory Output
                </span>
                <span style={{
                  padding: '4px 12px',
                  borderRadius: '12px',
                  fontSize: '0.75rem',
                  fontWeight: 800,
                  backgroundColor: `rgba(255, 255, 255, 0.05)`,
                  color: getRiskColor(result.risk_level),
                  border: `1px solid ${getRiskColor(result.risk_level)}`
                }}>
                  {result.risk_level} RISK
                </span>
              </div>

              {/* Metric Tiles */}
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(130px, 1fr))', gap: '12px', marginBottom: '22px' }}>
                <div style={{ backgroundColor: 'var(--bg-main)', padding: '14px', borderRadius: '8px', border: '1px solid var(--border-subtle)' }}>
                  <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginBottom: '4px' }}>Projected Total</div>
                  <div style={{ fontSize: '1.4rem', fontWeight: 800, color: 'var(--accent-cyan)' }}>{result.projected_score}</div>
                </div>

                <div style={{ backgroundColor: 'var(--bg-main)', padding: '14px', borderRadius: '8px', border: '1px solid var(--border-subtle)' }}>
                  <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginBottom: '4px' }}>Current Run Rate</div>
                  <div style={{ fontSize: '1.4rem', fontWeight: 800 }}>{result.current_run_rate}</div>
                </div>

                {result.required_run_rate !== null && (
                  <div style={{ backgroundColor: 'var(--bg-main)', padding: '14px', borderRadius: '8px', border: '1px solid var(--border-subtle)' }}>
                    <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginBottom: '4px' }}>Required RR</div>
                    <div style={{ fontSize: '1.4rem', fontWeight: 800, color: 'var(--accent-orange)' }}>{result.required_run_rate}</div>
                  </div>
                )}

                <div style={{ backgroundColor: 'var(--bg-main)', padding: '14px', borderRadius: '8px', border: '1px solid var(--border-subtle)' }}>
                  <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginBottom: '4px' }}>Balls Left</div>
                  <div style={{ fontSize: '1.4rem', fontWeight: 800 }}>{result.balls_remaining}</div>
                </div>
              </div>

              {/* Win Probability Bar (if chase) */}
              {result.win_probability_batting !== null && (
                <div style={{ marginBottom: '24px' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.85rem', marginBottom: '8px' }}>
                    <span>Chasing Win Prob: <strong>{result.win_probability_batting}%</strong></span>
                    <span>Defending Win Prob: <strong>{result.win_probability_bowling}%</strong></span>
                  </div>
                  <div style={{ height: '10px', borderRadius: '6px', backgroundColor: 'rgba(255,255,255,0.08)', overflow: 'hidden', display: 'flex' }}>
                    <motion.div
                      initial={{ width: 0 }}
                      animate={{ width: `${result.win_probability_batting}%` }}
                      transition={{ duration: 0.4 }}
                      style={{ height: '100%', backgroundColor: 'var(--accent-green)', borderRadius: '6px 0 0 6px' }}
                    />
                    <motion.div
                      initial={{ width: 0 }}
                      animate={{ width: `${result.win_probability_bowling}%` }}
                      transition={{ duration: 0.4 }}
                      style={{ height: '100%', backgroundColor: 'var(--accent-blue)', borderRadius: '0 6px 6px 0' }}
                    />
                  </div>
                </div>
              )}

              {/* Tactical Summary */}
              <div style={{ padding: '14px', backgroundColor: 'var(--bg-main)', borderRadius: '8px', border: '1px solid var(--border-subtle)' }}>
                <div style={{ fontSize: '0.8rem', fontWeight: 700, color: 'var(--accent-green)', marginBottom: '4px' }}>
                  Tactical Outlook
                </div>
                <p style={{ fontSize: '0.85rem', color: 'var(--text-main)', lineHeight: 1.5 }}>
                  {result.tactical_outlook}
                </p>
              </div>
            </div>
          </motion.div>
        )}
      </div>
    </PageWrapper>
  )
}