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