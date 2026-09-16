import React, { useEffect, useState } from 'react'
import { motion } from 'framer-motion'
import {
  Brain,
  Compass,
  Shield,
  Target,
  TrendingDown,
  TrendingUp,
  AlertTriangle,
  RefreshCw,
  Info,
} from 'lucide-react'
import PageWrapper from '../components/PageWrapper'
import { fetchPlayers, fetchTeams, fetchStrategyLab } from '../services/api'

export default function StrategyLabPage() {
  const [players, setPlayers] = useState([])
  const [teams, setTeams] = useState([])

  const [batterId, setBatterId] = useState('')
  const [bowlingTeamId, setBowlingTeamId] = useState('')

  const [score, setScore] = useState(138)
  const [overs, setOvers] = useState(16.0)
  const [wickets, setWickets] = useState(5)

  const [isChasing, setIsChasing] = useState(true)
  const [target, setTarget] = useState(185)

  const [phase, setPhase] = useState('death')

  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [initialLoading, setInitialLoading] = useState(true)

  useEffect(() => {
    const loadData = async () => {
      try {
        const [playersData, teamsData] = await Promise.all([
          fetchPlayers(),
          fetchTeams(),
        ])

        setPlayers(playersData)
        setTeams(teamsData)

        if (playersData.length > 0) {
          setBatterId(String(playersData[0].id))
        }

        if (teamsData.length > 0) {
          setBowlingTeamId(String(teamsData[0].id))
        }
      } catch (error) {
        console.error('Failed to load Strategy Lab data:', error)
      } finally {
        setInitialLoading(false)
      }
    }

    loadData()
  }, [])

  const runStrategyLab = async () => {
    if (!batterId || !bowlingTeamId) return

    setLoading(true)

    try {
      const payload = {
        batter_id: Number(batterId),
        bowling_team_id: Number(bowlingTeamId),
        current_score: Number(score),
        overs_completed: Number(overs),
        wickets_lost: Number(wickets),
        target_runs: isChasing ? Number(target) : null,
        total_overs: 20,
        match_phase: phase,
      }

      const data = await fetchStrategyLab(payload)
      setResult(data)
    } catch (error) {
      console.error('Strategy Lab failed:', error)
      setResult(null)
    } finally {
      setLoading(false)
    }
  }



  const getRiskColor = (risk) => {
    switch (risk) {
      case 'LOW':
        return 'var(--accent-green)'
      case 'MODERATE':
        return 'var(--accent-cyan)'
      case 'HIGH':
        return 'var(--accent-orange)'
      case 'EXTREME':
        return 'var(--accent-red)'
      default:
        return 'var(--text-muted)'
    }
  }

  const getMatchupLabel = (value) => {
    return value
      ?.replaceAll('_', ' ')
      .replace(/\b\w/g, (char) => char.toUpperCase())
  }

  if (initialLoading) {
    return (
      <PageWrapper>
        <div
          className="glass-card"
          style={{
            padding: '40px',
            textAlign: 'center',
          }}
        >
          <RefreshCw
            size={24}
            className="animate-spin"
          />

          <p
            style={{
              marginTop: '12px',
              color: 'var(--text-muted)',
            }}
          >
            Loading Strategy Lab...
          </p>
        </div>
      </PageWrapper>
    )
  }

  return (
    <PageWrapper>
      {/* Header */}
      <div style={{ marginBottom: '28px' }}>
        <div
          style={{
            display: 'inline-flex',
            alignItems: 'center',
            gap: '7px',
            color: 'var(--accent-green)',
            fontWeight: 700,
            fontSize: '0.85rem',
            marginBottom: '8px',
          }}
        >
          <Brain size={16} />
          CricketIQ Decision Intelligence
        </div>

        <h1
          style={{
            fontSize: '2.2rem',
            fontWeight: 800,
            marginBottom: '8px',
          }}
        >
          Match Strategy Lab
        </h1>

        <p
          style={{
            color: 'var(--text-muted)',
            maxWidth: '850px',
            lineHeight: 1.6,
          }}
        >
          Compare bowling options against the current batter using phase
          performance, matchup evidence, recommendation scores, and
          decision-adjusted win probability estimates.
        </p>
      </div>

      <div
        style={{
          display: 'grid',
          gridTemplateColumns: 'minmax(300px, 360px) 1fr',
          gap: '24px',
          alignItems: 'start',
        }}
      >
        {/* Controls */}
        <div
          className="glass-card"
          style={{
            position: 'sticky',
            top: '20px',
          }}
        >
          <div
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
              marginBottom: '20px',
              color: 'var(--accent-cyan)',
            }}
          >
            <Compass size={18} />

            <h3
              style={{
                margin: 0,
                fontSize: '1.1rem',
              }}
            >
              Match Situation
            </h3>
          </div>

          {/* Batter */}
          <div style={{ marginBottom: '16px' }}>
            <label
              style={{
                display: 'block',
                fontSize: '0.8rem',
                fontWeight: 700,
                color: 'var(--text-muted)',
                marginBottom: '6px',
              }}
            >
              BATTER
            </label>

            <select
              value={batterId}
              onChange={(e) => setBatterId(e.target.value)}
              style={{
                width: '100%',
                padding: '10px',
                borderRadius: '7px',
                border: '1px solid var(--border-subtle)',
                background: 'var(--bg-main)',
                color: 'var(--text-main)',
              }}
            >
              <option value="">Select batter</option>

              {players.map((player) => (
                <option
                  key={player.id}
                  value={player.id}
                >
                  {player.name}
                </option>
              ))}
            </select>
          </div>

          {/* Bowling Team */}
          <div style={{ marginBottom: '16px' }}>
            <label
              style={{
                display: 'block',
                fontSize: '0.8rem',
                fontWeight: 700,
                color: 'var(--text-muted)',
                marginBottom: '6px',
              }}
            >
              BOWLING TEAM
            </label>

            <select
              value={bowlingTeamId}
              onChange={(e) =>
                setBowlingTeamId(e.target.value)
              }
              style={{
                width: '100%',
                padding: '10px',
                borderRadius: '7px',
                border: '1px solid var(--border-subtle)',
                background: 'var(--bg-main)',
                color: 'var(--text-main)',
              }}
            >
              <option value="">Select bowling team</option>

              {teams.map((team) => (
                <option
                  key={team.id}
                  value={team.id}
                >
                  {team.name}
                </option>
              ))}
            </select>
          </div>

          {/* Score */}
          <div style={{ marginBottom: '16px' }}>
            <div
              style={{
                display: 'flex',
                justifyContent: 'space-between',
                marginBottom: '6px',
                fontSize: '0.85rem',
              }}
            >
              <span>Current Score</span>

              <strong>
                {score}
              </strong>
            </div>

            <input
              type="range"
              min="0"
              max="300"
              value={score}
              onChange={(e) => setScore(e.target.value)}
              style={{
                width: '100%',
                accentColor: 'var(--accent-cyan)',
              }}
            />
          </div>

          {/* Overs */}
          <div style={{ marginBottom: '16px' }}>
            <div
              style={{
                display: 'flex',
                justifyContent: 'space-between',
                marginBottom: '6px',
                fontSize: '0.85rem',
              }}
            >
              <span>Overs Completed</span>

              <strong>
                {overs}
              </strong>
            </div>

            <input
              type="range"
              min="0"
              max="19.5"
              step="0.1"
              value={overs}
              onChange={(e) => setOvers(e.target.value)}
              style={{
                width: '100%',
                accentColor: 'var(--accent-blue)',
              }}
            />
          </div>

          {/* Wickets */}
          <div style={{ marginBottom: '18px' }}>
            <div
              style={{
                display: 'flex',
                justifyContent: 'space-between',
                marginBottom: '6px',
                fontSize: '0.85rem',
              }}
            >
              <span>Wickets Lost</span>

              <strong>
                {wickets}
              </strong>
            </div>

            <input
              type="range"
              min="0"
              max="10"
              value={wickets}
              onChange={(e) => setWickets(e.target.value)}
              style={{
                width: '100%',
                accentColor: 'var(--accent-orange)',
              }}
            />
          </div>

          {/* Chase */}
          <div
            style={{
              padding: '12px',
              borderRadius: '8px',
              background: 'var(--bg-main)',
              border: '1px solid var(--border-subtle)',
              marginBottom: '16px',
            }}
          >
            <label
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '8px',
                fontSize: '0.85rem',
                fontWeight: 700,
                cursor: 'pointer',
                marginBottom: isChasing ? '12px' : '0',
              }}
            >
              <input
                type="checkbox"
                checked={isChasing}
                onChange={(e) =>
                  setIsChasing(e.target.checked)
                }
                style={{
                  accentColor: 'var(--accent-green)',
                }}
              />

              Chasing
            </label>

            {isChasing && (
              <input
                type="number"
                min="1"
                max="400"
                value={target}
                onChange={(e) => setTarget(e.target.value)}
                placeholder="Target"
                style={{
                  width: '100%',
                  boxSizing: 'border-box',
                  padding: '9px',
                  borderRadius: '6px',
                  border: '1px solid var(--border-subtle)',
                  background: 'var(--bg-card)',
                  color: 'var(--text-main)',
                }}
              />
            )}
          </div>

          {/* Phase */}
          <div style={{ marginBottom: '20px' }}>
            <label
              style={{
                display: 'block',
                fontSize: '0.8rem',
                fontWeight: 700,
                color: 'var(--text-muted)',
                marginBottom: '6px',
              }}
            >
              MATCH PHASE
            </label>

            <select
              value={phase}
              onChange={(e) => setPhase(e.target.value)}
              style={{
                width: '100%',
                padding: '10px',
                borderRadius: '7px',
                border: '1px solid var(--border-subtle)',
                background: 'var(--bg-main)',
                color: 'var(--text-main)',
              }}
            >
              <option value="powerplay">
                Powerplay
              </option>
              <option value="middle">
                Middle
              </option>
              <option value="death">
                Death
              </option>
            </select>
          </div>

          <button
            className="btn-primary"
            onClick={runStrategyLab}
            disabled={
              loading ||
              !batterId ||
              !bowlingTeamId
            }
            style={{
              width: '100%',
              justifyContent: 'center',
              padding: '12px',
            }}
          >
            {loading ? (
              <RefreshCw
                size={16}
                className="animate-spin"
              />
            ) : (
              <Brain size={16} />
            )}

            Analyze Strategy
          </button>
        </div>

        {/* Results */}
        <div>
          {!result && !loading && (
            <div
              className="glass-card"
              style={{
                padding: '40px',
                textAlign: 'center',
                color: 'var(--text-muted)',
              }}
            >
              Configure the match situation and run the
              Strategy Lab.
            </div>
          )}

          {loading && (
            <div
              className="glass-card"
              style={{
                padding: '40px',
                textAlign: 'center',
              }}
            >
              <RefreshCw
                size={24}
                className="animate-spin"
              />

              <p
                style={{
                  marginTop: '12px',
                  color: 'var(--text-muted)',
                }}
              >
                Evaluating bowling options...
              </p>
            </div>
          )}

          {result && !loading && (
            <>
              {/* Situation Summary */}
              <div
                className="glass-card"
                style={{
                  marginBottom: '20px',
                }}
              >
                <div
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                    gap: '12px',
                    flexWrap: 'wrap',
                    marginBottom: '16px',
                  }}
                >
                  <div>
                    <div
                      style={{
                        fontSize: '0.75rem',
                        color: 'var(--text-muted)',
                        textTransform: 'uppercase',
                        fontWeight: 700,
                        marginBottom: '5px',
                      }}
                    >
                      Current Situation
                    </div>

                    <div
                      style={{
                        fontSize: '1.4rem',
                        fontWeight: 800,
                      }}
                    >
                      {result.current_score} /{' '}
                      {result.wickets_lost}
                    </div>
                  </div>

                  <div
                    style={{
                      padding: '7px 12px',
                      borderRadius: '15px',
                      border:
                        '1px solid var(--border-subtle)',
                      color: 'var(--accent-cyan)',
                      fontSize: '0.78rem',
                      fontWeight: 800,
                      textTransform: 'uppercase',
                    }}
                  >
                    {result.match_phase}
                  </div>
                </div>

                <div
                  style={{
                    display: 'grid',
                    gridTemplateColumns:
                      'repeat(auto-fit, minmax(120px, 1fr))',
                    gap: '12px',
                  }}
                >
                  <div
                    style={{
                      padding: '12px',
                      borderRadius: '8px',
                      background: 'var(--bg-main)',
                    }}
                  >
                    <div
                      style={{
                        fontSize: '0.72rem',
                        color: 'var(--text-muted)',
                      }}
                    >
                      Overs
                    </div>

                    <strong>
                      {result.overs_completed}
                    </strong>
                  </div>

                  <div
                    style={{
                      padding: '12px',
                      borderRadius: '8px',
                      background: 'var(--bg-main)',
                    }}
                  >
                    <div
                      style={{
                        fontSize: '0.72rem',
                        color: 'var(--text-muted)',
                      }}
                    >
                      Batter
                    </div>

                    <strong>
                      {result.batter_name}
                    </strong>
                  </div>

                  {result.target_runs !== null && (
                    <div
                      style={{
                        padding: '12px',
                        borderRadius: '8px',
                        background: 'var(--bg-main)',
                      }}
                    >
                      <div
                        style={{
                          fontSize: '0.72rem',
                          color: 'var(--text-muted)',
                        }}
                      >
                        Target
                      </div>

                      <strong>
                        {result.target_runs}
                      </strong>
                    </div>
                  )}
                </div>
              </div>

              {/* Decision Summary */}
              <motion.div
                initial={{
                  opacity: 0,
                  y: 8,
                }}
                animate={{
                  opacity: 1,
                  y: 0,
                }}
                className="glass-card"
                style={{
                  marginBottom: '20px',
                  border:
                    '1px solid rgba(0, 255, 170, 0.22)',
                }}
              >
                <div
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: '7px',
                    color: 'var(--accent-green)',
                    fontSize: '0.82rem',
                    fontWeight: 800,
                    textTransform: 'uppercase',
                    marginBottom: '8px',
                  }}
                >
                  <Target size={16} />
                  Decision Summary
                </div>

                <p
                  style={{
                    margin: 0,
                    lineHeight: 1.6,
                    fontSize: '0.92rem',
                  }}
                >
                  {result.decision_summary}
                </p>
              </motion.div>

              {/* Recommended Option */}
              {result.recommended_option && (
                <motion.div
                  initial={{
                    opacity: 0,
                    y: 8,
                  }}
                  animate={{
                    opacity: 1,
                    y: 0,
                  }}
                  className="glass-card"
                  style={{
                    marginBottom: '20px',
                    border:
                      '1px solid rgba(0, 255, 170, 0.3)',
                  }}
                >
                  <div
                    style={{
                      display: 'flex',
                      justifyContent: 'space-between',
                      alignItems: 'center',
                      gap: '12px',
                      marginBottom: '16px',
                      flexWrap: 'wrap',
                    }}
                  >
                    <div>
                      <div
                        style={{
                          fontSize: '0.74rem',
                          color: 'var(--accent-green)',
                          textTransform: 'uppercase',
                          fontWeight: 800,
                          marginBottom: '5px',
                        }}
                      >
                        Recommended Bowling Option
                      </div>

                      <h2
                        style={{
                          margin: 0,
                          fontSize: '1.6rem',
                        }}
                      >
                        {result.recommended_option.bowler_name}
                      </h2>
                    </div>

                    <div
                      style={{
                        fontSize: '1.4rem',
                        fontWeight: 800,
                        color: 'var(--accent-green)',
                      }}
                    >
                      {result.recommended_option.recommendation_score}
                      <span
                        style={{
                          fontSize: '0.75rem',
                          color: 'var(--text-muted)',
                          marginLeft: '3px',
                        }}
                      >
                        /100
                      </span>
                    </div>
                  </div>

                  <div
                    style={{
                      display: 'grid',
                      gridTemplateColumns:
                        'repeat(auto-fit, minmax(140px, 1fr))',
                      gap: '12px',
                      marginBottom: '16px',
                    }}
                  >
                    <div
                      style={{
                        padding: '12px',
                        borderRadius: '8px',
                        background: 'var(--bg-main)',
                      }}
                    >
                      <div
                        style={{
                          fontSize: '0.72rem',
                          color: 'var(--text-muted)',
                        }}
                      >
                        Phase Economy
                      </div>

                      <strong>
                        {result.recommended_option.phase_economy}
                        {' '}RPO
                      </strong>
                    </div>

                    <div
                      style={{
                        padding: '12px',
                        borderRadius: '8px',
                        background: 'var(--bg-main)',
                      }}
                    >
                      <div
                        style={{
                          fontSize: '0.72rem',
                          color: 'var(--text-muted)',
                        }}
                      >
                        Matchup
                      </div>

                      <strong>
                        {getMatchupLabel(
                          result.recommended_option
                            .matchup_advantage
                        )}
                      </strong>
                    </div>

                    <div
                      style={{
                        padding: '12px',
                        borderRadius: '8px',
                        background: 'var(--bg-main)',
                      }}
                    >
                      <div
                        style={{
                          fontSize: '0.72rem',
                          color: 'var(--text-muted)',
                        }}
                      >
                        Batting Win Estimate
                      </div>

                      <strong>
                        {
                          result.recommended_option
                            .projected_batting_win_probability
                        }
                        %
                      </strong>
                    </div>

                    <div
                      style={{
                        padding: '12px',
                        borderRadius: '8px',
                        background: 'var(--bg-main)',
                      }}
                    >
                      <div
                        style={{
                          fontSize: '0.72rem',
                          color: 'var(--text-muted)',
                        }}
                      >
                        Risk
                      </div>

                      <strong
                        style={{
                          color: getRiskColor(
                            result.recommended_option
                              .risk_level
                          ),
                        }}
                      >
                        {result.recommended_option.risk_level}
                      </strong>
                    </div>
                  </div>

                  <div
                    style={{
                      padding: '14px',
                      borderRadius: '8px',
                      background: 'rgba(255,255,255,0.03)',
                      border:
                        '1px solid var(--border-subtle)',
                    }}
                  >
                    <div
                      style={{
                        fontSize: '0.75rem',
                        color: 'var(--text-muted)',
                        textTransform: 'uppercase',
                        fontWeight: 700,
                        marginBottom: '5px',
                      }}
                    >
                      Tactical Rationale
                    </div>

                    <p
                      style={{
                        margin: 0,
                        lineHeight: 1.5,
                        fontSize: '0.87rem',
                      }}
                    >
                      {result.recommended_option.rationale}
                    </p>
                  </div>
                </motion.div>
              )}

              {/* Option Comparison */}
              <div className="glass-card">
                <div
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: '7px',
                    marginBottom: '16px',
                  }}
                >
                  <Shield
                    size={17}
                    color="var(--accent-cyan)"
                  />

                  <h3
                    style={{
                      margin: 0,
                      fontSize: '1.05rem',
                    }}
                  >
                    Bowling Option Comparison
                  </h3>
                </div>

                <div
                  style={{
                    display: 'grid',
                    gap: '12px',
                  }}
                >
                  {result.options.map(
                    (option, index) => (
                      <motion.div
                        key={option.bowler_id}
                        initial={{
                          opacity: 0,
                          x: -8,
                        }}
                        animate={{
                          opacity: 1,
                          x: 0,
                        }}
                        transition={{
                          delay: index * 0.04,
                        }}
                        style={{
                          padding: '14px',
                          borderRadius: '9px',
                          border:
                            index === 0
                              ? '1px solid rgba(0, 255, 170, 0.3)'
                              : '1px solid var(--border-subtle)',
                          background:
                            index === 0
                              ? 'rgba(0, 255, 170, 0.04)'
                              : 'var(--bg-main)',
                        }}
                      >
                        <div
                          style={{
                            display: 'grid',
                            gridTemplateColumns:
                              'auto 1fr auto',
                            gap: '12px',
                            alignItems: 'center',
                          }}
                        >
                          <div
                            style={{
                              width: '32px',
                              height: '32px',
                              borderRadius: '50%',
                              display: 'flex',
                              alignItems: 'center',
                              justifyContent: 'center',
                              background:
                                index === 0
                                  ? 'var(--accent-green)'
                                  : 'rgba(255,255,255,0.07)',
                              color:
                                index === 0
                                  ? 'var(--bg-main)'
                                  : 'var(--text-main)',
                              fontWeight: 800,
                              fontSize: '0.8rem',
                            }}
                          >
                            #{option.rank}
                          </div>

                          <div>
                            <div
                              style={{
                                fontWeight: 800,
                                marginBottom: '4px',
                              }}
                            >
                              {option.bowler_name}
                            </div>

                            <div
                              style={{
                                fontSize: '0.75rem',
                                color: 'var(--text-muted)',
                              }}
                            >
                              {getMatchupLabel(
                                option.matchup_advantage
                              )}{' '}
                              · {option.phase_economy} RPO
                            </div>
                          </div>

                          <div
                            style={{
                              textAlign: 'right',
                            }}
                          >
                            <div
                              style={{
                                fontWeight: 800,
                              }}
                            >
                              {
                                option
                                  .projected_batting_win_probability
                              }
                              %
                            </div>

                            <div
                              style={{
                                fontSize: '0.7rem',
                                color: 'var(--text-muted)',
                              }}
                            >
                              batting estimate
                            </div>
                          </div>
                        </div>

                        <div
                          style={{
                            display: 'flex',
                            gap: '8px',
                            flexWrap: 'wrap',
                            marginTop: '10px',
                          }}
                        >
                          <span
                            style={{
                              padding: '4px 8px',
                              borderRadius: '10px',
                              fontSize: '0.68rem',
                              fontWeight: 700,
                              border:
                                '1px solid var(--border-subtle)',
                            }}
                          >
                            Score {option.recommendation_score}
                          </span>

                          <span
                            style={{
                              padding: '4px 8px',
                              borderRadius: '10px',
                              fontSize: '0.68rem',
                              fontWeight: 700,
                              border:
                                '1px solid var(--border-subtle)',
                              color: getRiskColor(
                                option.risk_level
                              ),
                            }}
                          >
                            {option.risk_level} RISK
                          </span>
                        </div>

                        <div
                          style={{
                            marginTop: '10px',
                            fontSize: '0.8rem',
                            color: 'var(--text-muted)',
                            lineHeight: 1.45,
                          }}
                        >
                          {option.tactical_directive}
                        </div>
                      </motion.div>
                    )
                  )}
                </div>
              </div>

              {/* Uncertainty */}
              <div
                style={{
                  marginTop: '14px',
                  padding: '12px 14px',
                  borderRadius: '8px',
                  border:
                    '1px solid var(--border-subtle)',
                  display: 'flex',
                  gap: '8px',
                  alignItems: 'flex-start',
                }}
              >
                <Info
                  size={15}
                  style={{
                    marginTop: '2px',
                    flexShrink: 0,
                  }}
                />

                <div
                  style={{
                    fontSize: '0.74rem',
                    color: 'var(--text-muted)',
                    lineHeight: 1.5,
                  }}
                >
                  {result.uncertainty_note}
                </div>
              </div>
            </>
          )}
        </div>
      </div>
    </PageWrapper>
  )
}