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

export async function simulateScenario(scenarioData) {
  const res = await fetch(`${API_BASE}/scenarios/simulate`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(scenarioData),
  })
  if (!res.ok) throw new Error('Failed to simulate scenario')
  return res.json()
}

export async function fetchAIMatchAnalysis(matchId) {
  const res = await fetch(`${API_BASE}/ai/analyze-match`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ match_id: matchId }),
  })
  if (!res.ok) throw new Error('Failed to generate match analysis')
  return res.json()
}

export async function askAIAnalyst(question, matchId = null) {
  const res = await fetch(`${API_BASE}/ai/ask`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ question, match_id: matchId }),
  })
  if (!res.ok) throw new Error('Failed to query AI analyst')
  return res.json()
}

export async function registerUser(userData) {
  const res = await fetch(`${API_BASE}/auth/register`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(userData),
  })
  if (!res.ok) {
    const err = await res.json()
    throw new Error(err.detail || 'Registration failed')
  }
  return res.json()
}

export async function loginUser(credentials) {
  const res = await fetch(`${API_BASE}/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(credentials),
  })
  if (!res.ok) {
    const err = await res.json()
    throw new Error(err.detail || 'Login failed')
  }
  return res.json()
}

export async function fetchCurrentUser(token) {
  const res = await fetch(`${API_BASE}/auth/me`, {
    headers: { Authorization: `Bearer ${token}` },
  })
  if (!res.ok) throw new Error('Failed to fetch user profile')
  return res.json()
}