import React, { useEffect, useState } from 'react'
import { motion } from 'framer-motion'
import { PlayCircle, Award, AlertCircle, RefreshCw, AlertTriangle } from 'lucide-react'
import PageWrapper from '../components/PageWrapper'
import { fetchMatches, fetchDecisionPoints, fetchPlayers, simulateDecisionReplay } from '../services/api'

export default function DecisionReplayPage() {
  const [matches, setMatches] = useState([])
  const [selectedMatchId, setSelectedMatchId] = useState(1)
  const [decisionPoints, setDecisionPoints] = useState([])
  const [selectedOver, setSelectedOver] = useState(null)
  const [bowlers, setBowlers] = useState([])
  const [selectedAltBowler, setSelectedAltBowler] = useState('')
  const [replayResult, setReplayResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [errorMsg, setErrorMsg] = useState('')

  useEffect(() => {
    fetchMatches().then(data => {
      setMatches(data)
      // Explicitly default to Match 1 which has full ball-by-ball deliveries
      const matchWithData = data.find(m => m.id === 1) || data[0]
      if (matchWithData) setSelectedMatchId(matchWithData.id)
    }).catch(console.error)
  }, [])

  useEffect(() => {
    if (selectedMatchId) {
      setReplayResult(null)
      setErrorMsg('')

      fetchDecisionPoints(selectedMatchId).then(pts => {
        setDecisionPoints(pts)
        if (pts.length > 0) {
          setSelectedOver(pts[0].over_number)
        } else {
          setSelectedOver(null)
        }
      }).catch(() => setDecisionPoints([]))

      fetchPlayers().then(pls => {
        const bowlingSquad = pls.filter(p => p.role === 'BOWLER' || p.role === 'ALL_ROUNDER')
        setBowlers(bowlingSquad)
        if (bowlingSquad.length > 0) setSelectedAltBowler(bowlingSquad[0].id)
      }).catch(console.error)
    }
  }, [selectedMatchId])

  const handleSimulate = async () => {
    if (!selectedMatchId || selectedOver === null || !selectedAltBowler) return
    setLoading(true)
    setErrorMsg('')
    try {
      const data = await simulateDecisionReplay(
        Number(selectedMatchId),
        Number(selectedOver),
        Number(selectedAltBowler)
      )
      setReplayResult(data)
    } catch (err) {
      setErrorMsg('Simulation failed. Please verify that the selected match has recorded deliveries.')
    } finally {
      setLoading(false)
    }
  }

  const currentPoint = decisionPoints.find(p => p.over_number === selectedOver)
  const isMatchPlayable = decisionPoints.length > 0

  return (
    <PageWrapper>
      <div style={{ marginBottom: '28px' }}>
        <div style={{ display: 'inline-flex', alignItems: 'center', gap: '6px', color: 'var(--accent-cyan)', fontWeight: 700, fontSize: '0.85rem', marginBottom: '8px' }}>
          <PlayCircle size={16} /> Counterfactual Decision Engine
        </div>
        <h1 style={{ fontSize: '2.2rem', fontWeight: 800 }}>Decision Replay</h1>
        <p style={{ color: 'var(--text-muted)' }}>
          Re-run critical match moments with alternative tactical choices to evaluate what-if scenarios.
        </p>
      </div>

      {/* Match Selector Dropdown */}
      <div className="glass-card" style={{ marginBottom: '24px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '16px', flexWrap: 'wrap', marginBottom: isMatchPlayable ? '0' : '12px' }}>
          <label style={{ fontWeight: 700, fontSize: '0.9rem', color: 'var(--accent-cyan)' }}>
            Select Match for Replay:
          </label>
          <select
            value={selectedMatchId}
            onChange={e => setSelectedMatchId(Number(e.target.value))}
            style={{
              padding: '10px 14px',
              borderRadius: '8px',
              backgroundColor: 'var(--bg-main)',
              border: '1px solid var(--border-subtle)',
              color: 'var(--text-main)',
              fontSize: '0.9rem',
              minWidth: '340px'
            }}
          >
            {matches.map(m => (
              <option key={m.id} value={m.id}>
                {m.title} {m.id === 1 ? '★ (240 Deliveries Available)' : '(External Fixture - No Deliveries)'}
              </option>
            ))}
          </select>
        </div>

        {!isMatchPlayable && (
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: 'var(--accent-orange)', fontSize: '0.85rem' }}>
            <AlertTriangle size={16} />
            <span>This fixture was synced from the external API and does not have delivery-level innings yet. Please select <strong>India vs Australia</strong> above to simulate.</span>
          </div>
        )}
      </div>

      {/* Configuration Grid */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: '20px', marginBottom: '32px' }}>
        {/* Step 1: Decision Point Selector */}
        <div className="glass-card">
          <h3 style={{ fontSize: '1.05rem', marginBottom: '16px', color: 'var(--accent-cyan)' }}>
            1. Select Decision Moment
          </h3>
          {decisionPoints.length === 0 ? (
            <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>
              No turning points recorded for this match. Select "India vs Australia".
            </p>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
              {decisionPoints.map(dp => (
                <button
                  key={dp.over_number}
                  onClick={() => { setSelectedOver(dp.over_number); setReplayResult(null); }}
                  style={{
                    textAlign: 'left',
                    padding: '12px',
                    borderRadius: '8px',
                    border: selectedOver === dp.over_number ? '1px solid var(--accent-cyan)' : '1px solid var(--border-subtle)',
                    backgroundColor: selectedOver === dp.over_number ? 'rgba(0, 210, 255, 0.08)' : 'var(--bg-main)',
                    color: 'var(--text-main)',
                    cursor: 'pointer'
                  }}
                >
                  <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '4px' }}>
                    <span style={{ fontWeight: 700, fontSize: '0.9rem' }}>Over {dp.display_over}</span>
                    <span style={{ color: 'var(--accent-orange)', fontSize: '0.8rem', fontWeight: 600 }}>
                      {dp.runs_required} off {dp.balls_remaining}b
                    </span>
                  </div>
                  <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                    Bowler: {dp.actual_bowler_name} vs {dp.batter_name}
                  </div>
                </button>
              ))}
            </div>
          )}
        </div>

        {/* Step 2: Alternative Bowler Choice */}
        <div className="glass-card" style={{ display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
          <div>
            <h3 style={{ fontSize: '1.05rem', marginBottom: '16px', color: 'var(--accent-cyan)' }}>
              2. Choose Alternative Option
            </h3>

            {currentPoint ? (
              <div style={{ backgroundColor: 'var(--bg-main)', border: '1px solid var(--border-subtle)', borderRadius: '8px', padding: '14px', marginBottom: '18px', fontSize: '0.85rem' }}>
                <div style={{ color: 'var(--text-muted)', marginBottom: '4px' }}>Actual In-Game Decision:</div>
                <div style={{ fontWeight: 700, color: 'var(--text-main)' }}>{currentPoint.actual_bowler_name} bowled over {currentPoint.display_over}</div>
                <div style={{ color: 'var(--text-muted)', marginTop: '4px' }}>{currentPoint.context_reason}</div>
              </div>
            ) : (
              <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem', marginBottom: '18px' }}>Select an over from the list.</p>
            )}

            <label style={{ display: 'block', fontSize: '0.85rem', color: 'var(--text-muted)', marginBottom: '8px', fontWeight: 600 }}>
              Substituted Alternative Bowler:
            </label>
            <select
              value={selectedAltBowler}
              onChange={e => setSelectedAltBowler(e.target.value)}
              style={{
                width: '100%',
                padding: '10px 12px',
                borderRadius: '8px',
                backgroundColor: 'var(--bg-main)',
                border: '1px solid var(--border-subtle)',
                color: 'var(--text-main)',
                fontSize: '0.9rem',
                marginBottom: '20px'
              }}
            >
              {bowlers.map(b => (
                <option key={b.id} value={b.id}>
                  {b.name} ({b.role})
                </option>
              ))}
            </select>
          </div>

          {errorMsg && (
            <p style={{ color: 'var(--accent-red)', fontSize: '0.85rem', marginBottom: '12px' }}>{errorMsg}</p>
          )}

          <button
            onClick={handleSimulate}
            disabled={loading || selectedOver === null || !isMatchPlayable}
            className="btn-primary"
            style={{
              width: '100%',
              justifyContent: 'center',
              padding: '12px',
              opacity: (loading || selectedOver === null || !isMatchPlayable) ? 0.5 : 1,
              cursor: (loading || selectedOver === null || !isMatchPlayable) ? 'not-allowed' : 'pointer'
            }}
          >
            {loading ? <RefreshCw size={16} className="animate-spin" /> : <PlayCircle size={16} />}
            {loading ? 'Simulating Physics & Telemetry...' : 'Simulate Counterfactual Replay'}
          </button>
        </div>
      </div>

      {/* Step 3: Simulation Results Card with Framer Motion */}
      {replayResult && (
        <motion.div
          initial={{ opacity: 0, scale: 0.96 }}
          animate={{ opacity: 1, scale: 1 }}
          className="glass-card"
          style={{ border: '1px solid rgba(0, 210, 255, 0.4)' }}
        >
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '12px', marginBottom: '20px', borderBottom: '1px solid var(--border-subtle)', paddingBottom: '16px' }}>
            <div>
              <span style={{ fontSize: '0.75rem', fontWeight: 800, color: 'var(--accent-cyan)', textTransform: 'uppercase' }}>
                Replay Simulation #{replayResult.replay_id}
              </span>
              <h2 style={{ fontSize: '1.4rem', margin: '4px 0 0 0' }}>{replayResult.tactical_verdict}</h2>
            </div>

            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', backgroundColor: 'rgba(0, 210, 255, 0.1)', border: '1px solid rgba(0, 210, 255, 0.3)', borderRadius: '20px', padding: '6px 14px' }}>
              <Award size={16} color="var(--accent-cyan)" />
              <span style={{ fontSize: '0.85rem', fontWeight: 700 }}>Quality Score: {replayResult.decision_quality_score}/100</span>
            </div>
          </div>

          {/* Side-by-Side Comparison Bars */}
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '20px', marginBottom: '24px' }}>
            <div style={{ backgroundColor: 'var(--bg-main)', padding: '16px', borderRadius: '8px', border: '1px solid var(--border-subtle)' }}>
              <div style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginBottom: '6px' }}>Actual Decision</div>
              <div style={{ fontSize: '1.1rem', fontWeight: 700, marginBottom: '12px' }}>{replayResult.actual_bowler_name}</div>
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.85rem', marginBottom: '6px' }}>
                <span>Defending Win Probability:</span>
                <span style={{ fontWeight: 700 }}>{replayResult.actual_win_prob}%</span>
              </div>
              <div style={{ height: '8px', borderRadius: '4px', backgroundColor: 'rgba(255,255,255,0.08)', overflow: 'hidden' }}>
                <div style={{ height: '100%', width: `${replayResult.actual_win_prob}%`, backgroundColor: 'var(--accent-blue)', borderRadius: '4px' }} />
              </div>
              <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginTop: '8px' }}>
                Runs Conceded: {replayResult.expected_runs_actual}
              </div>
            </div>

            <div style={{ backgroundColor: 'var(--bg-main)', padding: '16px', borderRadius: '8px', border: '1px solid var(--border-subtle)' }}>
              <div style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginBottom: '6px' }}>Alternative Option</div>
              <div style={{ fontSize: '1.1rem', fontWeight: 700, marginBottom: '12px' }}>{replayResult.alternative_bowler_name}</div>
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.85rem', marginBottom: '6px' }}>
                <span>Projected Win Probability:</span>
                <span style={{ fontWeight: 700, color: replayResult.decision_impact >= 0 ? 'var(--accent-green)' : 'var(--accent-red)' }}>
                  {replayResult.alternative_win_prob}% ({replayResult.decision_impact >= 0 ? `+${replayResult.decision_impact}` : replayResult.decision_impact}%)
                </span>
              </div>
              <div style={{ height: '8px', borderRadius: '4px', backgroundColor: 'rgba(255,255,255,0.08)', overflow: 'hidden' }}>
                <div style={{
                  height: '100%',
                  width: `${replayResult.alternative_win_prob}%`,
                  backgroundColor: replayResult.decision_impact >= 0 ? 'var(--accent-green)' : 'var(--accent-red)',
                  borderRadius: '4px'
                }} />
              </div>
              <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginTop: '8px' }}>
                Projected Runs: {replayResult.expected_runs_alternative}
              </div>
            </div>
          </div>

          <p style={{ fontSize: '0.95rem', lineHeight: 1.6, color: 'var(--text-main)', marginBottom: '16px' }}>
            {replayResult.explanation}
          </p>

          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', backgroundColor: 'rgba(255, 122, 0, 0.08)', border: '1px solid rgba(255, 122, 0, 0.25)', borderRadius: '6px', padding: '10px 14px', fontSize: '0.8rem', color: 'var(--accent-orange)' }}>
            <AlertCircle size={16} />
            <span>{replayResult.uncertainty_disclaimer}</span>
          </div>
        </motion.div>
      )}
    </PageWrapper>
  )
}