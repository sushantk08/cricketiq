import React, { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { motion } from 'framer-motion'
import {
  Calendar,
  MapPin,
  Radio,
  ArrowRight,
  RefreshCw,
  TrendingUp,
} from 'lucide-react'
import PageWrapper from '../components/PageWrapper'
import {
  fetchMatches,
  fetchLiveScores,
  fetchLiveIntelligence,
} from '../services/api'

export default function MatchesPage() {
  const [matches, setMatches] = useState([])
  const [liveScores, setLiveScores] = useState([])
  const [liveIntelligence, setLiveIntelligence] = useState([])
  const [loading, setLoading] = useState(true)
  const [refreshingLive, setRefreshingLive] = useState(false)
  const [matchFilter, setMatchFilter] = useState('ALL')

  const loadData = () => {
    Promise.all([
      fetchMatches(),
      fetchLiveScores(),
      fetchLiveIntelligence(),
    ])
      .then(([dbMatches, liveData, intelligenceData]) => {
        setMatches(dbMatches)
        setLiveScores(liveData)
        setLiveIntelligence(intelligenceData)
        setLoading(false)
        setRefreshingLive(false)
      })
      .catch(err => {
        console.error(err)
        setLoading(false)
        setRefreshingLive(false)
      })
  }

  useEffect(() => {
    loadData()

    const interval = setInterval(() => {
      Promise.all([
        fetchLiveScores(),
        fetchLiveIntelligence(),
      ])
        .then(([liveData, intelligenceData]) => {
          setLiveScores(liveData)
          setLiveIntelligence(intelligenceData)
        })
        .catch(err =>
          console.error('Live intelligence refresh failed:', err)
        )
    }, 30000)

    return () => clearInterval(interval)
  }, [])

  const activeLiveScores = liveScores.filter(
    (match) => match.match_started && !match.match_ended
  )

  const filteredMatches =
    matchFilter === 'ALL'
      ? matches
      : matches.filter((match) => match.status === matchFilter)

  const handleRefresh = () => {
    setRefreshingLive(true)
    loadData()
  }

  return (
    <PageWrapper>
      <div
        style={{
          marginBottom: '32px',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'flex-start',
          flexWrap: 'wrap',
          gap: '16px',
        }}
      >
        <div>
          <h1
            style={{
              fontSize: '2rem',
              fontWeight: 800,
              marginBottom: '8px',
            }}
          >
            Match Center & Live Scores
          </h1>

          <p style={{ color: 'var(--text-muted)' }}>
            Real-time CricAPI scores and historical analytical telemetry.
          </p>
        </div>

        <button
          onClick={handleRefresh}
          disabled={refreshingLive}
          className="btn-primary"
          style={{
            fontSize: '0.85rem',
            display: 'inline-flex',
            alignItems: 'center',
            gap: '6px',
          }}
        >
          <RefreshCw
            size={14}
            className={refreshingLive ? 'animate-spin' : ''}
          />

          {refreshingLive
            ? 'Updating Scores...'
            : 'Refresh Live Scores'}
        </button>
      </div>

      {/* MATCH FILTERS */}
      <div
        style={{
          display: 'flex',
          gap: '8px',
          flexWrap: 'wrap',
          marginBottom: '28px',
        }}
      >
        {['ALL', 'LIVE', 'COMPLETED', 'UPCOMING'].map((filter) => (
          <button
            key={filter}
            onClick={() => setMatchFilter(filter)}
            style={{
              padding: '8px 14px',
              borderRadius: '20px',
              border:
                matchFilter === filter
                  ? '1px solid var(--accent-cyan)'
                  : '1px solid var(--border-subtle)',
              background:
                matchFilter === filter
                  ? 'rgba(0, 210, 255, 0.12)'
                  : 'var(--bg-card)',
              color:
                matchFilter === filter
                  ? 'var(--accent-cyan)'
                  : 'var(--text-muted)',
              fontWeight: 700,
              fontSize: '0.8rem',
              cursor: 'pointer',
            }}
          >
            {filter === 'ALL'
              ? 'All Matches'
              : filter.charAt(0) +
                filter.slice(1).toLowerCase()}
          </button>
        ))}
      </div>

      {/* LIVE CRICKET SCORES SECTION */}
      <div style={{ marginBottom: '40px' }}>
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
            marginBottom: '16px',
          }}
        >
          <Radio
            size={18}
            color="var(--accent-red)"
            className="animate-pulse"
          />

          <h2
            style={{
              fontSize: '1.25rem',
              fontWeight: 700,
            }}
          >
            Live CricAPI Feed
          </h2>
        </div>

        {activeLiveScores.length === 0 ? (
          <p
            style={{
              color: 'var(--text-muted)',
              fontSize: '0.9rem',
            }}
          >
            No live matches currently in progress.
          </p>
        ) : (
          <div
            style={{
              display: 'grid',
              gridTemplateColumns:
                'repeat(auto-fill, minmax(340px, 1fr))',
              gap: '18px',
            }}
          >
            {activeLiveScores.map((m, idx) => (
              <motion.div
                key={m.external_id || idx}
                initial={{ opacity: 0, y: 12 }}
                animate={{ opacity: 1, y: 0 }}
                className="glass-card"
                style={{
                  border:
                    '1px solid rgba(239, 68, 68, 0.35)',
                  backgroundColor:
                    'rgba(17, 26, 46, 0.95)',
                }}
              >
                <div
                  style={{
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center',
                    marginBottom: '10px',
                  }}
                >
                  <span
                    style={{
                      padding: '2px 8px',
                      borderRadius: '10px',
                      fontSize: '0.7rem',
                      fontWeight: 800,
                      backgroundColor:
                        'rgba(239, 68, 68, 0.2)',
                      color: 'var(--accent-red)',
                      display: 'inline-flex',
                      alignItems: 'center',
                      gap: '4px',
                    }}
                  >
                    ● {m.status}
                  </span>

                  <span
                    style={{
                      fontSize: '0.8rem',
                      fontWeight: 600,
                      color: 'var(--accent-cyan)',
                    }}
                  >
                    {m.match_type}
                  </span>
                </div>

                <h3
                  style={{
                    fontSize: '1.05rem',
                    fontWeight: 700,
                    marginBottom: '12px',
                  }}
                >
                  {m.title}
                </h3>

                <div
                  style={{
                    backgroundColor: 'var(--bg-main)',
                    padding: '12px',
                    borderRadius: '8px',
                    marginBottom: '12px',
                    border:
                      '1px solid var(--border-subtle)',
                  }}
                >
                  <div
                    style={{
                      fontSize: '1.1rem',
                      fontWeight: 800,
                      color: 'var(--text-main)',
                      marginBottom: '4px',
                    }}
                  >
                    {m.formatted_score}
                  </div>

                  {m.status_note && (
                    <div
                      style={{
                        fontSize: '0.8rem',
                        color: 'var(--accent-orange)',
                      }}
                    >
                      {m.status_note}
                    </div>
                  )}
                </div>

                <div
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: '6px',
                    fontSize: '0.8rem',
                    color: 'var(--text-muted)',
                  }}
                >
                  <MapPin
                    size={13}
                    color="var(--accent-cyan)"
                  />

                  {m.venue_name}
                </div>
              </motion.div>
            ))}
          </div>
        )}
      </div>

      {/* LIVE INTELLIGENCE SECTION */}
      <div style={{ marginBottom: '40px' }}>
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
            marginBottom: '16px',
          }}
        >
          <TrendingUp
            size={18}
            color="var(--accent-cyan)"
          />

          <h2
            style={{
              fontSize: '1.25rem',
              fontWeight: 700,
            }}
          >
            Live Match Intelligence
          </h2>
        </div>

        {liveIntelligence.length === 0 ? (
          <div
            className="glass-card"
            style={{
              padding: '18px',
              color: 'var(--text-muted)',
              fontSize: '0.9rem',
            }}
          >
            <div
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '8px',
                marginBottom: '6px',
                color: 'var(--accent-cyan)',
                fontWeight: 700,
              }}
            >
              <Radio size={15} />
              No active intelligence
            </div>

            Live intelligence will appear automatically when a
            match is currently in progress.
          </div>
        ) : (
          <div
            style={{
              display: 'grid',
              gridTemplateColumns:
                'repeat(auto-fill, minmax(340px, 1fr))',
              gap: '18px',
            }}
          >
            {liveIntelligence.map((intel, idx) => (
              <motion.div
                key={intel.external_id || idx}
                initial={{
                  opacity: 0,
                  y: 12,
                }}
                animate={{
                  opacity: 1,
                  y: 0,
                }}
                transition={{
                  delay: idx * 0.05,
                }}
                className="glass-card"
                style={{
                  border:
                    '1px solid var(--border-subtle)',
                }}
              >
                <div
                  style={{
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center',
                    marginBottom: '12px',
                  }}
                >
                  <span
                    style={{
                      display: 'inline-flex',
                      alignItems: 'center',
                      gap: '5px',
                      fontSize: '0.7rem',
                      fontWeight: 800,
                      color: 'var(--accent-red)',
                    }}
                  >
                    <span className="animate-pulse">
                      ●
                    </span>
                    LIVE INTELLIGENCE
                  </span>

                  <span
                    style={{
                      fontSize: '0.75rem',
                      fontWeight: 700,
                      color: 'var(--accent-cyan)',
                    }}
                  >
                    {intel.match_type}
                  </span>
                </div>

                <h3
                  style={{
                    fontSize: '1rem',
                    fontWeight: 700,
                    marginBottom: '10px',
                  }}
                >
                  {intel.title}
                </h3>

                <div
                  style={{
                    padding: '12px',
                    borderRadius: '8px',
                    backgroundColor: 'var(--bg-main)',
                    border:
                      '1px solid var(--border-subtle)',
                    marginBottom: '12px',
                  }}
                >
                  <div
                    style={{
                      fontSize: '1rem',
                      fontWeight: 800,
                      marginBottom: '4px',
                    }}
                  >
                    {intel.formatted_score}
                  </div>

                  <div
                    style={{
                      fontSize: '0.75rem',
                      color: 'var(--text-muted)',
                    }}
                  >
                    {intel.venue_name}
                  </div>
                </div>

                {intel.current_score !== null && (
                  <div
                    style={{
                      display: 'grid',
                      gridTemplateColumns:
                        'repeat(3, 1fr)',
                      gap: '8px',
                      marginBottom: '14px',
                    }}
                  >
                    <div
                      style={{
                        padding: '9px',
                        borderRadius: '7px',
                        backgroundColor:
                          'rgba(255,255,255,0.03)',
                      }}
                    >
                      <div
                        style={{
                          fontSize: '0.68rem',
                          color: 'var(--text-muted)',
                        }}
                      >
                        Score
                      </div>

                      <div
                        style={{
                          fontWeight: 800,
                          marginTop: '2px',
                        }}
                      >
                        {intel.current_score}
                      </div>
                    </div>

                    <div
                      style={{
                        padding: '9px',
                        borderRadius: '7px',
                        backgroundColor:
                          'rgba(255,255,255,0.03)',
                      }}
                    >
                      <div
                        style={{
                          fontSize: '0.68rem',
                          color: 'var(--text-muted)',
                        }}
                      >
                        Wickets
                      </div>

                      <div
                        style={{
                          fontWeight: 800,
                          marginTop: '2px',
                        }}
                      >
                        {intel.current_wickets}
                      </div>
                    </div>

                    <div
                      style={{
                        padding: '9px',
                        borderRadius: '7px',
                        backgroundColor:
                          'rgba(255,255,255,0.03)',
                      }}
                    >
                      <div
                        style={{
                          fontSize: '0.68rem',
                          color: 'var(--text-muted)',
                        }}
                      >
                        Overs
                      </div>

                      <div
                        style={{
                          fontWeight: 800,
                          marginTop: '2px',
                        }}
                      >
                        {intel.current_overs}
                      </div>
                    </div>
                  </div>
                )}

                <div
                  style={{
                    padding: '12px',
                    borderRadius: '8px',
                    backgroundColor: 'var(--bg-main)',
                    border:
                      '1px solid var(--border-subtle)',
                    marginBottom: '12px',
                  }}
                >
                  <div
                    style={{
                      display: 'flex',
                      alignItems: 'center',
                      gap: '6px',
                      color: 'var(--accent-cyan)',
                      fontWeight: 700,
                      fontSize: '0.75rem',
                      marginBottom: '5px',
                    }}
                  >
                    <TrendingUp size={14} />
                    Decision Summary
                  </div>

                  <p
                    style={{
                      margin: 0,
                      fontSize: '0.78rem',
                      lineHeight: 1.5,
                      color: 'var(--text-main)',
                    }}
                  >
                    {intel.decision_summary}
                  </p>
                </div>

                {intel.insights?.length > 0 && (
                  <div>
                    <div
                      style={{
                        fontSize: '0.75rem',
                        fontWeight: 700,
                        color: 'var(--accent-orange)',
                        marginBottom: '8px',
                      }}
                    >
                      Live Signals
                    </div>

                    <div
                      style={{
                        display: 'grid',
                        gap: '7px',
                      }}
                    >
                      {intel.insights.map(
                        (insight, insightIndex) => (
                          <div
                            key={`${insight.category}-${insightIndex}`}
                            style={{
                              padding: '9px 10px',
                              borderRadius: '7px',
                              backgroundColor:
                                'rgba(255,255,255,0.03)',
                              border:
                                '1px solid var(--border-subtle)',
                            }}
                          >
                            <div
                              style={{
                                fontSize: '0.68rem',
                                textTransform:
                                  'uppercase',
                                color:
                                  'var(--text-muted)',
                                fontWeight: 700,
                                marginBottom: '2px',
                              }}
                            >
                              {insight.category}
                            </div>

                            <div
                              style={{
                                fontSize: '0.8rem',
                                fontWeight: 700,
                                marginBottom: '2px',
                              }}
                            >
                              {insight.title}
                            </div>

                            <div
                              style={{
                                fontSize: '0.75rem',
                                color:
                                  'var(--text-muted)',
                                lineHeight: 1.4,
                              }}
                            >
                              {insight.detail}
                            </div>
                          </div>
                        )
                      )}
                    </div>
                  </div>
                )}

                {intel.status_note && (
                  <div
                    style={{
                      marginTop: '12px',
                      fontSize: '0.72rem',
                      color: 'var(--text-muted)',
                    }}
                  >
                    Provider status: {intel.status_note}
                  </div>
                )}
              </motion.div>
            ))}
          </div>
        )}
      </div>

      {/* STORED MATCHES */}
      <div>
        <h2
          style={{
            fontSize: '1.25rem',
            fontWeight: 700,
            marginBottom: '16px',
          }}
        >
          {matchFilter === 'ALL'
            ? 'Stored Match Fixtures & Telemetry'
            : `${matchFilter.charAt(0) +
                matchFilter.slice(1).toLowerCase()} Matches`}
        </h2>

        {loading ? (
          <p
            style={{
              color: 'var(--text-muted)',
              fontSize: '0.9rem',
            }}
          >
            Loading matches...
          </p>
        ) : filteredMatches.length === 0 ? (
          <div
            className="glass-card"
            style={{
              padding: '40px 24px',
              textAlign: 'center',
              border:
                '1px dashed var(--border-subtle)',
            }}
          >
            <h3
              style={{
                marginBottom: '8px',
              }}
            >
              No Matches Found
            </h3>

            <p
              style={{
                color: 'var(--text-muted)',
                fontSize: '0.9rem',
              }}
            >
              There are no {matchFilter.toLowerCase()} matches
              available.
            </p>
          </div>
        ) : (
          <div
            style={{
              display: 'grid',
              gridTemplateColumns:
                'repeat(auto-fill, minmax(340px, 1fr))',
              gap: '20px',
            }}
          >
            {filteredMatches.map((m, idx) => (
              <motion.div
                key={m.id}
                initial={{
                  opacity: 0,
                  y: 15,
                }}
                animate={{
                  opacity: 1,
                  y: 0,
                }}
                transition={{
                  delay: idx * 0.04,
                }}
                whileHover={{ y: -3 }}
                className="glass-card"
                style={{
                  display: 'flex',
                  flexDirection: 'column',
                  justifyContent: 'space-between',
                }}
              >
                <div>
                  <div
                    style={{
                      display: 'flex',
                      justifyContent: 'space-between',
                      alignItems: 'center',
                      marginBottom: '12px',
                    }}
                  >
                    <span
                      style={{
                        padding: '3px 8px',
                        borderRadius: '10px',
                        fontSize: '0.7rem',
                        fontWeight: 700,
                        backgroundColor:
                          m.status === 'LIVE'
                            ? 'rgba(239, 68, 68, 0.15)'
                            : 'rgba(16, 185, 129, 0.15)',
                        color:
                          m.status === 'LIVE'
                            ? 'var(--accent-red)'
                            : 'var(--accent-green)',
                      }}
                    >
                      {m.status}
                    </span>

                    <span
                      style={{
                        fontSize: '0.8rem',
                        color: 'var(--text-muted)',
                        fontWeight: 600,
                      }}
                    >
                      {m.match_type}
                    </span>
                  </div>

                  <h3
                    style={{
                      fontSize: '1.05rem',
                      fontWeight: 700,
                      marginBottom: '14px',
                    }}
                  >
                    {m.title}
                  </h3>

                  <div
                    style={{
                      display: 'flex',
                      flexDirection: 'column',
                      gap: '6px',
                      marginBottom: '18px',
                      color: 'var(--text-muted)',
                      fontSize: '0.8rem',
                    }}
                  >
                    <div
                      style={{
                        display: 'flex',
                        alignItems: 'center',
                        gap: '6px',
                      }}
                    >
                      <MapPin
                        size={13}
                        color="var(--accent-cyan)"
                      />

                      {m.venue
                        ? `${m.venue.name}, ${m.venue.city}`
                        : 'Venue TBA'}
                    </div>

                    <div
                      style={{
                        display: 'flex',
                        alignItems: 'center',
                        gap: '6px',
                      }}
                    >
                      <Calendar
                        size={13}
                        color="var(--accent-blue)"
                      />

                      {new Date(
                        m.match_date
                      ).toLocaleDateString()}
                    </div>
                  </div>
                </div>

                <Link
                  to={`/matches/${m.id}`}
                  className="btn-primary"
                  style={{
                    width: '100%',
                    justifyContent: 'center',
                    fontSize: '0.85rem',
                  }}
                >
                  View Scorecard & Analytics
                  <ArrowRight size={14} />
                </Link>
              </motion.div>
            ))}
          </div>
        )}
      </div>
    </PageWrapper>
  )
}