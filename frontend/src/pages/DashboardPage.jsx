import { useEffect, useState } from "react";
import { Link } from "react-router-dom";

function DashboardPage() {
  const [matches, setMatches] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch("http://127.0.0.1:8000/api/matches")
      .then((response) => {
        if (!response.ok) {
          throw new Error("Failed to fetch matches.");
        }

        return response.json();
      })
      .then((data) => {
        setMatches(data);
        setLoading(false);
      })
      .catch(() => {
        setMatches([]);
        setLoading(false);
      });
  }, []);

  const liveMatches = matches.filter(
    (match) => match.status === "LIVE"
  );

  const completedMatches = matches.filter(
    (match) => match.status === "COMPLETED"
  );

  const upcomingMatches = matches.filter(
    (match) => match.status === "UPCOMING"
  );

  const statCard = (label, value, description) => (
    <div className="glass-card">
      <p
        style={{
          color: "var(--text-muted)",
          fontSize: "12px",
          marginBottom: "8px",
        }}
      >
        {label}
      </p>

      <h2
        style={{
          fontSize: "30px",
          fontWeight: 800,
          marginBottom: "6px",
        }}
      >
        {value}
      </h2>

      <p
        style={{
          color: "var(--text-muted)",
          fontSize: "12px",
        }}
      >
        {description}
      </p>
    </div>
  );

  return (
    <div
      style={{
        maxWidth: "1400px",
        margin: "0 auto",
        padding: "40px 48px",
      }}
    >
      <div style={{ marginBottom: "30px" }}>
        <p
          style={{
            color: "var(--accent-cyan)",
            fontSize: "12px",
            fontWeight: 700,
            letterSpacing: "0.08em",
            marginBottom: "8px",
          }}
        >
          CRICKET INTELLIGENCE
        </p>

        <h1
          style={{
            fontSize: "38px",
            fontWeight: 800,
            marginBottom: "8px",
          }}
        >
          CricketIQ Dashboard
        </h1>

        <p
          style={{
            color: "var(--text-muted)",
            fontSize: "16px",
          }}
        >
          Match intelligence, live activity, and analytical insights
          at a glance.
        </p>
      </div>

      {loading ? (
        <p style={{ color: "var(--text-muted)" }}>
          Loading dashboard...
        </p>
      ) : (
        <>
          <div
            style={{
              display: "grid",
              gridTemplateColumns:
                "repeat(auto-fit, minmax(210px, 1fr))",
              gap: "16px",
              marginBottom: "30px",
            }}
          >
            {statCard(
              "TOTAL MATCHES",
              matches.length,
              "Matches in CricketIQ"
            )}

            {statCard(
              "LIVE",
              liveMatches.length,
              "Currently in progress"
            )}

            {statCard(
              "COMPLETED",
              completedMatches.length,
              "Completed matches"
            )}

            {statCard(
              "UPCOMING",
              upcomingMatches.length,
              "Scheduled matches"
            )}
          </div>

          <div
            className="glass-card"
            style={{
              marginBottom: "28px",
              padding: "26px",
            }}
          >
            <div
              style={{
                display: "flex",
                justifyContent: "space-between",
                alignItems: "center",
                gap: "16px",
                marginBottom: "20px",
              }}
            >
              <div>
                <p
                  style={{
                    color: "var(--accent-cyan)",
                    fontSize: "12px",
                    fontWeight: 700,
                    marginBottom: "5px",
                  }}
                >
                  LIVE CENTER
                </p>

                <h2 style={{ fontSize: "23px" }}>
                  Live Matches
                </h2>
              </div>

              <Link
                to="/matches"
                style={{
                  color: "var(--accent-cyan)",
                  fontSize: "13px",
                  fontWeight: 600,
                }}
              >
                View all →
              </Link>
            </div>

            {liveMatches.length === 0 ? (
              <div
                style={{
                  background: "var(--bg-main)",
                  border: "1px solid var(--border-subtle)",
                  borderRadius: "10px",
                  padding: "25px",
                }}
              >
                <p
                  style={{
                    color: "var(--text-muted)",
                    fontSize: "14px",
                  }}
                >
                  No live matches available right now.
                </p>
              </div>
            ) : (
              <div
                style={{
                  display: "grid",
                  gap: "12px",
                }}
              >
                {liveMatches.slice(0, 5).map((match) => (
                  <Link
                    key={match.id}
                    to={`/matches/${match.id}`}
                    style={{
                      display: "block",
                      background: "var(--bg-main)",
                      border: "1px solid var(--border-subtle)",
                      borderRadius: "10px",
                      padding: "18px",
                    }}
                  >
                    <div
                      style={{
                        display: "flex",
                        justifyContent: "space-between",
                        alignItems: "flex-start",
                        gap: "16px",
                      }}
                    >
                      <div>
                        <h3
                          style={{
                            fontSize: "17px",
                            marginBottom: "7px",
                          }}
                        >
                          {match.title}
                        </h3>

                        <p
                          style={{
                            color: "var(--text-muted)",
                            fontSize: "12px",
                          }}
                        >
                          {match.match_type} •{" "}
                          {match.venue?.name ||
                            "Venue unavailable"}
                        </p>
                      </div>

                      <span
                        style={{
                          background:
                            "rgba(16, 185, 129, 0.10)",
                          border:
                            "1px solid rgba(16, 185, 129, 0.25)",
                          color: "var(--accent-green)",
                          borderRadius: "999px",
                          padding: "6px 10px",
                          fontSize: "11px",
                          fontWeight: 700,
                        }}
                      >
                        LIVE
                      </span>
                    </div>
                  </Link>
                ))}
              </div>
            )}
          </div>

          <div
            style={{
              display: "grid",
              gridTemplateColumns:
                "repeat(auto-fit, minmax(320px, 1fr))",
              gap: "20px",
            }}
          >
            <div className="glass-card">
              <p
                style={{
                  color: "var(--accent-cyan)",
                  fontSize: "12px",
                  fontWeight: 700,
                  marginBottom: "6px",
                }}
              >
                ANALYTICS
              </p>

              <h2
                style={{
                  fontSize: "21px",
                  marginBottom: "10px",
                }}
              >
                Match Intelligence
              </h2>

              <p
                style={{
                  color: "var(--text-muted)",
                  fontSize: "13px",
                  lineHeight: 1.6,
                  marginBottom: "18px",
                }}
              >
                Explore scorecards, turning points, win
                probability, and detailed match analytics.
              </p>

              <Link
                to="/matches"
                className="btn-primary"
                style={{
                  fontSize: "13px",
                  padding: "9px 14px",
                }}
              >
                Explore Matches
              </Link>
            </div>

            <div className="glass-card">
              <p
                style={{
                  color: "var(--accent-cyan)",
                  fontSize: "12px",
                  fontWeight: 700,
                  marginBottom: "6px",
                }}
              >
                STRATEGY
              </p>

              <h2
                style={{
                  fontSize: "21px",
                  marginBottom: "10px",
                }}
              >
                Decision Intelligence
              </h2>

              <p
                style={{
                  color: "var(--text-muted)",
                  fontSize: "13px",
                  lineHeight: 1.6,
                  marginBottom: "18px",
                }}
              >
                Compare tactical choices, analyze matchups,
                and explore alternate cricket decisions.
              </p>

              <Link
                to="/replay"
                className="btn-primary"
                style={{
                  fontSize: "13px",
                  padding: "9px 14px",
                }}
              >
                Open Decision Replay
              </Link>
            </div>

            <div className="glass-card">
              <p
                style={{
                  color: "var(--accent-cyan)",
                  fontSize: "12px",
                  fontWeight: 700,
                  marginBottom: "6px",
                }}
              >
                AI ANALYST
              </p>

              <h2
                style={{
                  fontSize: "21px",
                  marginBottom: "10px",
                }}
              >
                AI Match Analysis
              </h2>

              <p
                style={{
                  color: "var(--text-muted)",
                  fontSize: "13px",
                  lineHeight: 1.6,
                  marginBottom: "18px",
                }}
              >
                Generate grounded match reports and ask
                natural-language questions about cricket.
              </p>

              <Link
                to="/ai-analyst"
                className="btn-primary"
                style={{
                  fontSize: "13px",
                  padding: "9px 14px",
                }}
              >
                Open AI Analyst
              </Link>
            </div>
          </div>
        </>
      )}
    </div>
  );
}

export default DashboardPage;