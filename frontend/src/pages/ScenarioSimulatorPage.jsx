import React, { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import {
  Compass,
  TrendingUp,
  AlertTriangle,
  Shield,
  CheckCircle,
  RefreshCw,
  Lightbulb,
  Brain,
  Info,
} from 'lucide-react'
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
        total_overs: 20,
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

  const getInsightIcon = (category) => {
    switch (category) {
      case 'probability':
        return <TrendingUp size={16} />
      case 'pressure':
        return <AlertTriangle size={16} />
      case 'resources':
        return <Shield size={16} />
      case 'opportunity':
        return <CheckCircle size={16} />
      case 'batting':
        return <TrendingUp size={16} />
      case 'match_state':
      default:
        return <Lightbulb size={16} />
    }
  }

  return (
    <PageWrapper>
      {/* Page Header */}
      <div style={{ marginBottom: '28px' }}>
        <div
          style={{
            display: 'inline-flex',
            alignItems: 'center',
            gap: '6px',
            color: 'var(--accent-green)',
            fontWeight: 700,
            fontSize: '0.85rem',
            marginBottom: '8px',
          }}
        >
          <Compass size={16} />
          Interactive Strategy Sandbox
        </div>

        <h1
          style={{
            fontSize: '2.2rem',
            fontWeight: 800,
          }}
        >
          Scenario Simulator
        </h1>

        <p style={{ color: 'var(--text-muted)' }}>
          Adjust score, overs, wickets, and chase targets to recalculate
          trajectories, win likelihood, tactical risk, and decision-oriented
          match insights in real time.
        </p>
      </div>

      <div
        style={{
          display: 'grid',
          gridTemplateColumns:
            'repeat(auto-fit, minmax(320px, 1fr))',
          gap: '24px',
          marginBottom: '32px',
        }}
      >
        {/* Control Panel */}
        <div className="glass-card">
          <h3
            style={{
              fontSize: '1.15rem',
              marginBottom: '20px',
              color: 'var(--accent-green)',
            }}
          >
            Match Variables
          </h3>

          {/* Score Input */}
          <div style={{ marginBottom: '18px' }}>
            <div
              style={{
                display: 'flex',
                justifyContent: 'space-between',
                marginBottom: '6px',
                fontSize: '0.9rem',
                fontWeight: 600,
              }}
            >
              <span>Current Score:</span>
              <span
                style={{
                  color: 'var(--accent-cyan)',
                }}
              >
                {score} Runs
              </span>
            </div>

            <input
              type="range"
              min="0"
              max="250"
              value={score}
              onChange={(e) => setScore(e.target.value)}
              style={{
                width: '100%',
                accentColor: 'var(--accent-cyan)',
              }}
            />
          </div>

          {/* Overs Input */}
          <div style={{ marginBottom: '18px' }}>
            <div
              style={{
                display: 'flex',
                justifyContent: 'space-between',
                marginBottom: '6px',
                fontSize: '0.9rem',
                fontWeight: 600,
              }}
            >
              <span>Overs Completed:</span>

              <span
                style={{
                  color: 'var(--accent-blue)',
                }}
              >
                {overs} / 20.0
              </span>
            </div>

            <input
              type="range"
              min="0.0"
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

          {/* Wickets Input */}
          <div style={{ marginBottom: '22px' }}>
            <div
              style={{
                display: 'flex',
                justifyContent: 'space-between',
                marginBottom: '6px',
                fontSize: '0.9rem',
                fontWeight: 600,
              }}
            >
              <span>Wickets Fallen:</span>

              <span
                style={{
                  color: 'var(--accent-orange)',
                }}
              >
                {wickets} / 10
              </span>
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

          {/* Chase Toggle */}
          <div
            style={{
              marginBottom: '20px',
              padding: '14px',
              backgroundColor: 'var(--bg-main)',
              borderRadius: '8px',
              border: '1px solid var(--border-subtle)',
            }}
          >
            <label
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '8px',
                cursor: 'pointer',
                fontSize: '0.9rem',
                fontWeight: 600,
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
                  width: '16px',
                  height: '16px',
                  accentColor: 'var(--accent-green)',
                }}
              />

              2nd Innings Run Chase
            </label>

            {isChasing && (
              <div>
                <div
                  style={{
                    display: 'flex',
                    justifyContent: 'space-between',
                    marginBottom: '6px',
                    fontSize: '0.85rem',
                  }}
                >
                  <span
                    style={{
                      color: 'var(--text-muted)',
                    }}
                  >
                    Target Runs:
                  </span>

                  <span style={{ fontWeight: 700 }}>
                    {target}
                  </span>
                </div>

                <input
                  type="number"
                  min="1"
                  max="300"
                  value={target}
                  onChange={(e) =>
                    setTarget(e.target.value)
                  }
                  style={{
                    width: '100%',
                    padding: '8px 10px',
                    borderRadius: '6px',
                    backgroundColor: 'var(--bg-card)',
                    border:
                      '1px solid var(--border-subtle)',
                    color: 'var(--text-main)',
                    fontSize: '0.9rem',
                  }}
                />
              </div>
            )}
          </div>

          <button
            onClick={runSimulation}
            disabled={loading}
            className="btn-primary"
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
              <Compass size={16} />
            )}

            Recalculate Trajectory
          </button>
        </div>

        {/* Results Dashboard */}
        {result && (
          <motion.div
            key={`${score}-${overs}-${wickets}-${target}-${isChasing}`}
            initial={{
              opacity: 0,
              scale: 0.98,
            }}
            animate={{
              opacity: 1,
              scale: 1,
            }}
            className="glass-card"
            style={{
              display: 'flex',
              flexDirection: 'column',
              justifyContent: 'space-between',
            }}
          >
            <div>
              {/* Result Header */}
              <div
                style={{
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center',
                  marginBottom: '20px',
                  borderBottom:
                    '1px solid var(--border-subtle)',
                  paddingBottom: '14px',
                }}
              >
                <span
                  style={{
                    fontSize: '0.8rem',
                    fontWeight: 800,
                    color: 'var(--text-muted)',
                    textTransform: 'uppercase',
                  }}
                >
                  Trajectory Output
                </span>

                <span
                  style={{
                    padding: '4px 12px',
                    borderRadius: '12px',
                    fontSize: '0.75rem',
                    fontWeight: 800,
                    backgroundColor:
                      'rgba(255, 255, 255, 0.05)',
                    color: getRiskColor(
                      result.risk_level
                    ),
                    border: `1px solid ${getRiskColor(
                      result.risk_level
                    )}`,
                  }}
                >
                  {result.risk_level} RISK
                </span>
              </div>

              {/* Metric Tiles */}
              <div
                style={{
                  display: 'grid',
                  gridTemplateColumns:
                    'repeat(auto-fit, minmax(130px, 1fr))',
                  gap: '12px',
                  marginBottom: '22px',
                }}
              >
                {/* Projected Total */}
                <div
                  style={{
                    backgroundColor: 'var(--bg-main)',
                    padding: '14px',
                    borderRadius: '8px',
                    border:
                      '1px solid var(--border-subtle)',
                  }}
                >
                  <div
                    style={{
                      fontSize: '0.75rem',
                      color: 'var(--text-muted)',
                      marginBottom: '4px',
                    }}
                  >
                    Projected Total
                  </div>

                  <div
                    style={{
                      fontSize: '1.4rem',
                      fontWeight: 800,
                      color: 'var(--accent-cyan)',
                    }}
                  >
                    {result.projected_score}
                  </div>
                </div>

                {/* Current Run Rate */}
                <div
                  style={{
                    backgroundColor: 'var(--bg-main)',
                    padding: '14px',
                    borderRadius: '8px',
                    border:
                      '1px solid var(--border-subtle)',
                  }}
                >
                  <div
                    style={{
                      fontSize: '0.75rem',
                      color: 'var(--text-muted)',
                      marginBottom: '4px',
                    }}
                  >
                    Current Run Rate
                  </div>

                  <div
                    style={{
                      fontSize: '1.4rem',
                      fontWeight: 800,
                    }}
                  >
                    {result.current_run_rate}
                  </div>
                </div>

                {/* Required Run Rate */}
                {result.required_run_rate !== null && (
                  <div
                    style={{
                      backgroundColor: 'var(--bg-main)',
                      padding: '14px',
                      borderRadius: '8px',
                      border:
                        '1px solid var(--border-subtle)',
                    }}
                  >
                    <div
                      style={{
                        fontSize: '0.75rem',
                        color: 'var(--text-muted)',
                        marginBottom: '4px',
                      }}
                    >
                      Required RR
                    </div>

                    <div
                      style={{
                        fontSize: '1.4rem',
                        fontWeight: 800,
                        color: 'var(--accent-orange)',
                      }}
                    >
                      {result.required_run_rate}
                    </div>
                  </div>
                )}

                {/* Balls Remaining */}
                <div
                  style={{
                    backgroundColor: 'var(--bg-main)',
                    padding: '14px',
                    borderRadius: '8px',
                    border:
                      '1px solid var(--border-subtle)',
                  }}
                >
                  <div
                    style={{
                      fontSize: '0.75rem',
                      color: 'var(--text-muted)',
                      marginBottom: '4px',
                    }}
                  >
                    Balls Left
                  </div>

                  <div
                    style={{
                      fontSize: '1.4rem',
                      fontWeight: 800,
                    }}
                  >
                    {result.balls_remaining}
                  </div>
                </div>

                {/* Wickets In Hand */}
                <div
                  style={{
                    backgroundColor: 'var(--bg-main)',
                    padding: '14px',
                    borderRadius: '8px',
                    border:
                      '1px solid var(--border-subtle)',
                  }}
                >
                  <div
                    style={{
                      fontSize: '0.75rem',
                      color: 'var(--text-muted)',
                      marginBottom: '4px',
                    }}
                  >
                    Wickets In Hand
                  </div>

                  <div
                    style={{
                      fontSize: '1.4rem',
                      fontWeight: 800,
                    }}
                  >
                    {result.wickets_in_hand}
                  </div>
                </div>
              </div>

              {/* Win Probability */}
              {result.win_probability_batting !== null && (
                <div
                  style={{
                    marginBottom: '24px',
                  }}
                >
                  <div
                    style={{
                      display: 'flex',
                      justifyContent: 'space-between',
                      fontSize: '0.85rem',
                      marginBottom: '8px',
                    }}
                  >
                    <span>
                      Chasing Win Prob:{' '}
                      <strong>
                        {result.win_probability_batting}%
                      </strong>
                    </span>

                    <span>
                      Defending Win Prob:{' '}
                      <strong>
                        {result.win_probability_bowling}%
                      </strong>
                    </span>
                  </div>

                  <div
                    style={{
                      height: '10px',
                      borderRadius: '6px',
                      backgroundColor:
                        'rgba(255,255,255,0.08)',
                      overflow: 'hidden',
                      display: 'flex',
                    }}
                  >
                    <motion.div
                      initial={{
                        width: 0,
                      }}
                      animate={{
                        width: `${result.win_probability_batting}%`,
                      }}
                      transition={{
                        duration: 0.4,
                      }}
                      style={{
                        height: '100%',
                        backgroundColor:
                          'var(--accent-green)',
                        borderRadius:
                          '6px 0 0 6px',
                      }}
                    />

                    <motion.div
                      initial={{
                        width: 0,
                      }}
                      animate={{
                        width: `${result.win_probability_bowling}%`,
                      }}
                      transition={{
                        duration: 0.4,
                      }}
                      style={{
                        height: '100%',
                        backgroundColor:
                          'var(--accent-blue)',
                        borderRadius:
                          '0 6px 6px 0',
                      }}
                    />
                  </div>
                </div>
              )}

              {/* Decision Summary */}
              {result.decision_summary && (
                <motion.div
                  initial={{
                    opacity: 0,
                    y: 8,
                  }}
                  animate={{
                    opacity: 1,
                    y: 0,
                  }}
                  style={{
                    padding: '14px',
                    backgroundColor:
                      'var(--bg-main)',
                    borderRadius: '8px',
                    border:
                      '1px solid var(--border-subtle)',
                    marginBottom: '14px',
                  }}
                >
                  <div
                    style={{
                      display: 'flex',
                      alignItems: 'center',
                      gap: '7px',
                      fontSize: '0.8rem',
                      fontWeight: 700,
                      color: 'var(--accent-cyan)',
                      marginBottom: '6px',
                    }}
                  >
                    <Brain size={16} />
                    Decision Summary
                  </div>

                  <p
                    style={{
                      fontSize: '0.85rem',
                      color: 'var(--text-main)',
                      lineHeight: 1.5,
                      margin: 0,
                    }}
                  >
                    {result.decision_summary}
                  </p>
                </motion.div>
              )}

              {/* Key Insights */}
              {result.key_insights?.length > 0 && (
                <motion.div
                  initial={{
                    opacity: 0,
                    y: 8,
                  }}
                  animate={{
                    opacity: 1,
                    y: 0,
                  }}
                  transition={{
                    delay: 0.05,
                  }}
                  style={{
                    padding: '14px',
                    backgroundColor:
                      'var(--bg-main)',
                    borderRadius: '8px',
                    border:
                      '1px solid var(--border-subtle)',
                    marginBottom: '14px',
                  }}
                >
                  <div
                    style={{
                      display: 'flex',
                      alignItems: 'center',
                      gap: '7px',
                      fontSize: '0.8rem',
                      fontWeight: 700,
                      color: 'var(--accent-orange)',
                      marginBottom: '12px',
                    }}
                  >
                    <Lightbulb size={16} />
                    Key Insights
                  </div>

                  <div
                    style={{
                      display: 'grid',
                      gap: '10px',
                    }}
                  >
                    {result.key_insights.map(
                      (insight, index) => (
                        <motion.div
                          key={`${insight.category}-${index}`}
                          initial={{
                            opacity: 0,
                            y: 6,
                          }}
                          animate={{
                            opacity: 1,
                            y: 0,
                          }}
                          transition={{
                            delay: 0.08 + index * 0.05,
                          }}
                          style={{
                            padding: '10px 12px',
                            borderRadius: '7px',
                            backgroundColor:
                              'rgba(255,255,255,0.03)',
                            border:
                              '1px solid var(--border-subtle)',
                          }}
                        >
                          <div
                            style={{
                              display: 'flex',
                              alignItems: 'center',
                              gap: '6px',
                              fontSize: '0.72rem',
                              color: 'var(--text-muted)',
                              textTransform: 'uppercase',
                              fontWeight: 700,
                              marginBottom: '4px',
                            }}
                          >
                            {getInsightIcon(
                              insight.category
                            )}

                            {insight.category}
                          </div>

                          <div
                            style={{
                              fontSize: '0.88rem',
                              fontWeight: 700,
                              marginBottom: '4px',
                            }}
                          >
                            {insight.title}
                          </div>

                          <div
                            style={{
                              fontSize: '0.8rem',
                              color: 'var(--text-muted)',
                              lineHeight: 1.45,
                            }}
                          >
                            {insight.detail}
                          </div>
                        </motion.div>
                      )
                    )}
                  </div>
                </motion.div>
              )}

              {/* Tactical Outlook */}
              <div
                style={{
                  padding: '14px',
                  backgroundColor:
                    'var(--bg-main)',
                  borderRadius: '8px',
                  border:
                    '1px solid var(--border-subtle)',
                  marginBottom: '14px',
                }}
              >
                <div
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: '7px',
                    fontSize: '0.8rem',
                    fontWeight: 700,
                    color: 'var(--accent-green)',
                    marginBottom: '5px',
                  }}
                >
                  <Compass size={16} />
                  Tactical Outlook
                </div>

                <p
                  style={{
                    fontSize: '0.85rem',
                    color: 'var(--text-main)',
                    lineHeight: 1.5,
                    margin: 0,
                  }}
                >
                  {result.tactical_outlook}
                </p>
              </div>

              {/* Model Note */}
              <div
                style={{
                  padding: '12px 14px',
                  borderRadius: '8px',
                  border:
                    '1px solid var(--border-subtle)',
                  backgroundColor:
                    'rgba(255,255,255,0.02)',
                }}
              >
                <div
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: '6px',
                    fontSize: '0.75rem',
                    fontWeight: 700,
                    color: 'var(--text-muted)',
                    marginBottom: '5px',
                  }}
                >
                  <Info size={14} />
                  Model Note
                </div>

                <p
                  style={{
                    margin: 0,
                    fontSize: '0.75rem',
                    color: 'var(--text-muted)',
                    lineHeight: 1.45,
                  }}
                >
                  {result.uncertainty_note ||
                    'All projections and probabilities are model-based estimates, not guarantees of match outcomes.'}
                </p>
              </div>
            </div>
          </motion.div>
        )}
      </div>
    </PageWrapper>
  )
}