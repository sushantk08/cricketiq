import { useEffect, useState } from 'react'
import PageWrapper from '../components/PageWrapper'
import {
  fetchPlayers,
  fetchTeams,
  fetchMatchup,
  fetchBowlingStrategy,
  fetchBattingStrategy,
} from '../services/api'

export default function StrategyPage() {
  const [players, setPlayers] = useState([])
  const [teams, setTeams] = useState([])
  const [batterId, setBatterId] = useState('')
  const [bowlerId, setBowlerId] = useState('')
  const [teamId, setTeamId] = useState('')
  const [phase, setPhase] = useState('middle')
  const [requiredRunRate, setRequiredRunRate] = useState('')
  const [matchup, setMatchup] = useState(null)
  const [bowlingStrategy, setBowlingStrategy] = useState(null)
  const [battingStrategy, setBattingStrategy] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => {
     Promise.all([fetchPlayers(), fetchTeams()])
       .then(([playerData, teamData]) => {
         setPlayers(playerData)
         setTeams(teamData)
      })
    .catch(() => setError('Failed to load players or teams'))
    }, [])

  const batters = players.filter(
    (player) =>
      player.role === 'BATTER' ||
      player.role === 'ALL_ROUNDER' ||
      player.role === 'WICKETKEEPER'
  )

  const bowlers = players.filter(
    (player) =>
      player.role === 'BOWLER' ||
      player.role === 'ALL_ROUNDER'
  )

  const handleMatchup = async () => {
    if (!batterId || !bowlerId) return

    setLoading(true)
    setError('')

    try {
      const result = await fetchMatchup(
        Number(batterId),
        Number(bowlerId)
      )
      setMatchup(result)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  const handleBowlingStrategy = async () => {
    if (!batterId || !teamId) return

    setLoading(true)
    setError('')

    try {
      const result = await fetchBowlingStrategy({
        batter_id: Number(batterId),
        bowling_team_id: Number(teamId),
        match_phase: phase,
      })
      setBowlingStrategy(result)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  const handleBattingStrategy = async () => {
    if (!bowlerId) return

    setLoading(true)
    setError('')

    try {
      const result = await fetchBattingStrategy({
        bowler_id: Number(bowlerId),
        match_phase: phase,
        required_run_rate: requiredRunRate
          ? Number(requiredRunRate)
          : null,
      })
      setBattingStrategy(result)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <PageWrapper>
      <div style={{ marginBottom: '28px' }}>
        <h1 style={{ fontSize: '2.2rem', fontWeight: 800 }}>
          Strategy Center
        </h1>
        <p style={{ color: 'var(--text-muted)' }}>
          Use player matchups and historical performance to evaluate tactical options.
        </p>
      </div>

      {error && (
        <div
          className="glass-card"
          style={{
            marginBottom: '20px',
            color: 'var(--accent-red)',
          }}
        >
          {error}
        </div>
      )}

      <div
        style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))',
          gap: '20px',
        }}
      >
        <div className="glass-card">
          <h2 style={{ marginBottom: '16px' }}>
            Batter vs Bowler
          </h2>

          <select
            value={batterId}
            onChange={(e) => setBatterId(e.target.value)}
            style={{ width: '100%', padding: '10px', marginBottom: '12px' }}
          >
            <option value="">Select Batter</option>
            {batters.map((player) => (
              <option key={player.id} value={player.id}>
                {player.name}
              </option>
            ))}
          </select>

          <select
            value={bowlerId}
            onChange={(e) => setBowlerId(e.target.value)}
            style={{ width: '100%', padding: '10px', marginBottom: '12px' }}
          >
            <option value="">Select Bowler</option>
            {bowlers.map((player) => (
              <option key={player.id} value={player.id}>
                {player.name}
              </option>
            ))}
          </select>

          <button
            onClick={handleMatchup}
            disabled={loading || !batterId || !bowlerId}
            className="btn-primary"
            style={{ width: '100%' }}
          >
            Analyze Matchup
          </button>

          {matchup && (
            <div style={{ marginTop: '20px' }}>
              <p>
                <strong>Advantage:</strong> {matchup.advantage}
              </p>
              <p>
                <strong>Balls:</strong> {matchup.balls_faced}
              </p>
              <p>
                <strong>Runs:</strong> {matchup.runs_scored}
              </p>
              <p>
                <strong>Dismissals:</strong> {matchup.dismissals}
              </p>
              <p>
                <strong>Strike Rate:</strong> {matchup.strike_rate}
              </p>
              <p>
                <strong>Dot Ball %:</strong> {matchup.dot_ball_pct}
              </p>
            </div>
          )}
        </div>

        <div className="glass-card">
          <h2 style={{ marginBottom: '16px' }}>
            Bowling Strategy
          </h2>

          <select
            value={batterId}
            onChange={(e) => setBatterId(e.target.value)}
            style={{ width: '100%', padding: '10px', marginBottom: '12px' }}
          >
            <option value="">Select Batter</option>
            {batters.map((player) => (
              <option key={player.id} value={player.id}>
                {player.name}
              </option>
            ))}
          </select>

          <select
            value={teamId}
            onChange={(e) => setTeamId(e.target.value)}
            style={{ width: '100%', padding: '10px', marginBottom: '12px' }}
          >
            <option value="">Select Bowling Team</option>
            {teams.map((team) => (
            <option key={team.id} value={team.id}>
              {team.name}
            </option>
             ))}
          </select>

          <select
            value={phase}
            onChange={(e) => setPhase(e.target.value)}
            style={{ width: '100%', padding: '10px', marginBottom: '12px' }}
          >
            <option value="powerplay">Powerplay</option>
            <option value="middle">Middle</option>
            <option value="death">Death</option>
          </select>

          <button
            onClick={handleBowlingStrategy}
            disabled={loading || !batterId || !teamId}
            className="btn-primary"
            style={{ width: '100%' }}
          >
            Recommend Bowlers
          </button>

          {bowlingStrategy && (
            <div style={{ marginTop: '20px' }}>
              {bowlingStrategy.recommendations.slice(0, 5).map((item) => (
                <div
                  key={item.bowler_id}
                  style={{
                    padding: '10px',
                    marginBottom: '8px',
                    border: '1px solid var(--border-subtle)',
                    borderRadius: '8px',
                  }}
                >
                  <strong>
                    #{item.rank} {item.bowler_name}
                  </strong>
                  <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                    Score: {item.recommendation_score} · Economy: {item.phase_economy}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        <div className="glass-card">
          <h2 style={{ marginBottom: '16px' }}>
            Batting Strategy
          </h2>

          <select
            value={bowlerId}
            onChange={(e) => setBowlerId(e.target.value)}
            style={{ width: '100%', padding: '10px', marginBottom: '12px' }}
          >
            <option value="">Select Bowler</option>
            {bowlers.map((player) => (
              <option key={player.id} value={player.id}>
                {player.name}
              </option>
            ))}
          </select>

          <input
            type="number"
            step="0.1"
            placeholder="Required Run Rate"
            value={requiredRunRate}
            onChange={(e) => setRequiredRunRate(e.target.value)}
            style={{ width: '100%', padding: '10px', marginBottom: '12px' }}
          />

          <button
            onClick={handleBattingStrategy}
            disabled={loading || !bowlerId}
            className="btn-primary"
            style={{ width: '100%' }}
          >
            Generate Batting Plan
          </button>

          {battingStrategy && (
            <div style={{ marginTop: '20px' }}>
              <p>
                <strong>Approach:</strong>{' '}
                {battingStrategy.recommended_approach}
              </p>
              <p>
                <strong>Risk:</strong>{' '}
                {battingStrategy.risk_level}
              </p>
              <p style={{ lineHeight: 1.5 }}>
                {battingStrategy.tactical_directive}
              </p>
              <p style={{ lineHeight: 1.5, color: 'var(--text-muted)' }}>
                {battingStrategy.supporting_insight}
              </p>
            </div>
          )}
        </div>
      </div>
    </PageWrapper>
  )
}