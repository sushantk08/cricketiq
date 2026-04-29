import { useEffect, useState } from "react";
import { Link } from "react-router-dom";

function TeamsPage() {
  const [teams, setTeams] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch("http://127.0.0.1:8000/api/teams")
      .then((response) => {
        if (!response.ok) {
          throw new Error("Failed to fetch teams.");
        }

        return response.json();
      })
      .then((data) => {
        setTeams(data);
        setLoading(false);
      })
      .catch(() => {
        setTeams([]);
        setLoading(false);
      });
  }, []);

  return (
    <div
      style={{
        maxWidth: "1200px",
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
          CRICKETIQ DIRECTORY
        </p>

        <h1
          style={{
            fontSize: "38px",
            fontWeight: 800,
            marginBottom: "8px",
          }}
        >
          Teams
        </h1>

        <p
          style={{
            color: "var(--text-muted)",
            fontSize: "16px",
          }}
        >
          Explore teams and their CricketIQ player squads.
        </p>
      </div>

      {loading ? (
        <p style={{ color: "var(--text-muted)" }}>Loading teams...</p>
      ) : teams.length === 0 ? (
        <div className="glass-card" style={{ textAlign: "center" }}>
          <h2 style={{ marginBottom: "8px" }}>No teams found</h2>

          <p style={{ color: "var(--text-muted)" }}>
            There are currently no teams with registered players.
          </p>
        </div>
      ) : (
        <>
          <div
            style={{
              display: "flex",
              justifyContent: "space-between",
              alignItems: "center",
              marginBottom: "18px",
            }}
          >
            <h2 style={{ fontSize: "20px" }}>Team Directory</h2>

            <span
              style={{
                color: "var(--text-muted)",
                fontSize: "14px",
              }}
            >
              {teams.length} teams
            </span>
          </div>

          <div
            style={{
              display: "grid",
              gridTemplateColumns:
                "repeat(auto-fit, minmax(320px, 1fr))",
              gap: "18px",
            }}
          >
            {teams.map((team) => (
              <Link
                key={team.id}
                to={`/teams/${team.id}`}
                className="glass-card"
                style={{
                  display: "block",
                  padding: "24px",
                }}
              >
                <div
                  style={{
                    display: "flex",
                    justifyContent: "space-between",
                    alignItems: "center",
                    marginBottom: "20px",
                  }}
                >
                  <div
                    style={{
                      width: "54px",
                      height: "54px",
                      borderRadius: "14px",
                      display: "flex",
                      alignItems: "center",
                      justifyContent: "center",
                      background: "rgba(0, 210, 255, 0.08)",
                      border:
                        "1px solid rgba(0, 210, 255, 0.2)",
                      color: "var(--accent-cyan)",
                      fontSize: "18px",
                      fontWeight: 800,
                    }}
                  >
                    {team.short_name}
                  </div>

                  <span
                    style={{
                      color: "var(--text-muted)",
                      fontSize: "12px",
                    }}
                  >
                    TEAM
                  </span>
                </div>

                <h2
                  style={{
                    fontSize: "23px",
                    marginBottom: "8px",
                  }}
                >
                  {team.name}
                </h2>

                <p
                  style={{
                    color: "var(--text-muted)",
                    fontSize: "13px",
                    marginBottom: "18px",
                  }}
                >
                  {team.short_name} • Cricket Team
                </p>

                <div
                  style={{
                    borderTop:
                      "1px solid var(--border-subtle)",
                    paddingTop: "14px",
                    display: "flex",
                    justifyContent: "space-between",
                    alignItems: "center",
                  }}
                >
                  <span
                    style={{
                      color: "var(--text-muted)",
                      fontSize: "13px",
                    }}
                  >
                    View squad
                  </span>

                  <span
                    style={{
                      color: "var(--accent-cyan)",
                      fontSize: "18px",
                    }}
                  >
                    →
                  </span>
                </div>
              </Link>
            ))}
          </div>
        </>
      )}
    </div>
  );
}

export default TeamsPage;