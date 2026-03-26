const API_BASE = '/api'

export async function fetchMatches() {
  const res = await fetch(`${API_BASE}/matches`)
  if (!res.ok) throw new Error('Failed to fetch matches')
  return res.json()
}

export async function fetchMatchById(id) {
  const res = await fetch(`${API_BASE}/matches/${id}`)
  if (!res.ok) throw new Error('Failed to fetch match')
  return res.json()
}

export async function fetchMatchScorecard(id) {
  const res = await fetch(`${API_BASE}/matches/${id}/scorecard`)
  if (!res.ok) throw new Error('Failed to fetch scorecard')
  return res.json()
}

export async function fetchMatchTurningPoints(id) {
  const res = await fetch(`${API_BASE}/matches/${id}/turning-points`)
  if (!res.ok) throw new Error('Failed to fetch turning points')
  return res.json()
}

export async function fetchDecisionPoints(matchId) {
  const res = await fetch(`${API_BASE}/matches/${matchId}/decision-points`)
  if (!res.ok) throw new Error('Failed to fetch decision points')
  return res.json()
}

export async function simulateDecisionReplay(matchId, overNumber, alternativeBowlerId) {
  const res = await fetch(`${API_BASE}/replay/simulate`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      match_id: matchId,
      over_number: overNumber,
      alternative_bowler_id: alternativeBowlerId,
    }),
  })
  if (!res.ok) throw new Error('Failed to simulate decision replay')
  return res.json()
}

export async function fetchPlayers(teamId) {
  const url = teamId ? `${API_BASE}/players?team_id=${teamId}` : `${API_BASE}/players`
  const res = await fetch(url)
  if (!res.ok) throw new Error('Failed to fetch players')
  return res.json()
}