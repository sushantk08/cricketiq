import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";

function TeamDetailPage() {
  const { id } = useParams();

  const [team, setTeam] = useState(null);
  const [players, setPlayers] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      fetch("http://127.0.0.1:8000/api/teams").then((response) => {
        if (!response.ok) {
          throw new Error("Failed to fetch teams.");
        }

        return response.json();
      }),
      fetch(`http://127.0.0.1:8000/api/players?team_id=${id}`).then(
        (response) => {
          if (!response.ok) {
            throw new Error("Failed to fetch team players.");
          }

          return response.json();
        }
      ),
    ])
      .then(([teams, teamPlayers]) => {
        const selectedTeam = teams.find(
          (item) => item.id === Number(id)
        );

        setTeam(selectedTeam || null);
        setPlayers(teamPlayers);
        setLoading(false);
      })
      .catch(() => {
        setTeam(null);
        setPlayers([]);
        setLoading(false);
      });
  }, [id]);

  if (loading) {
    return (
      <div
        style={{
          maxWidth: "1200px",
          margin: "0 auto",
          padding: "40px 48px",
        }}
      >
        <p style={{ color: "var(--text-muted)" }}>Loading team...</p>
      </div>
    );
  }

  if (!team) {
    return (
      <div
        style={{
          maxWidth: "1200px",
          margin: "0 auto",
          padding: "40px 48px",
        }}
      >
        <div className="glass-card">
          <h1 style={{ marginBottom: "8px" }}>Team Not Found</h1>

          <p style={{ color: "var(--text-muted)" }}>
            Unable to load this team.
          </p>

          <Link
            to="/teams"
            style={{
              display: "inline-block",
              marginTop: "18px",
              color: "var(--accent-cyan)",
            }}
          >
            ← Back to Teams
          </Link>
        </div>
      </div>
    );
  }

  const roleCounts = players.reduce((counts, player) => {
    counts[player.role] = (counts[player.role] || 0) + 1;
    return counts;
  }, {});

  return (
    <div
      style={{
        maxWidth: "1200px",
        margin: "0 auto",
        padding: "40px 48px",
      }}
    >
      <Link
        to="/teams"
        style={{
          display: "inline-block",
          color: "var(--accent-cyan)",
          fontSize: "14px",
          marginBottom: "20px",
        }}
      >
        ← Back to Teams
      </Link>

      <div
        className="glass-card"
        style={{
          padding: "28px",
          marginBottom: "24px",
        }}
      >
        <div
          style={{
            display: "flex",
            justifyContent: "space-between",
            alignItems: "flex-start",
            gap: "20px",
            flexWrap: "wrap",
          }}
        >
          <div>
            <p
              style={{
                color: "var(--accent-cyan)",
                fontSize: "12px",
                fontWeight: 700,
                letterSpacing: "0.08em",
                marginBottom: "8px",
              }}
            >
              TEAM PROFILE
            </p>

            <h1
              style={{
                fontSize: "34px",
                fontWeight: 800,
                marginBottom: "10px",
              }}
            >
              {team.name}
            </h1>

            <p
              style={{
                color: "var(--text-muted)",
                fontSize: "14px",
              }}
            >
              {team.short_name} • Cricket Team
            </p>
          </div>

          <div
            style={{
              width: "70px",
              height: "70px",
              borderRadius: "16px",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              background: "rgba(0, 210, 255, 0.08)",
              border: "1px solid rgba(0, 210, 255, 0.2)",
              color: "var(--accent-cyan)",
              fontSize: "20px",
              fontWeight: 800,
            }}
          >
            {team.short_name}
          </div>
        </div>
      </div>

      <div
        style={{
          display: "grid",
          gridTemplateColumns:
            "repeat(auto-fit, minmax(180px, 1fr))",
          gap: "14px",
          marginBottom: "28px",
        }}
      >
        <div className="glass-card">
          <p
            style={{
              color: "var(--text-muted)",
              fontSize: "12px",
              marginBottom: "6px",
            }}
          >
            Squad Size
          </p>

          <p style={{ fontSize: "26px", fontWeight: 800 }}>
            {players.length}
          </p>
        </div>

        <div className="glass-card">
          <p
            style={{
              color: "var(--text-muted)",
              fontSize: "12px",
              marginBottom: "6px",
            }}
          >
            Batters
          </p>

          <p style={{ fontSize: "26px", fontWeight: 800 }}>
            {roleCounts.BATTER || 0}
          </p>
        </div>

        <div className="glass-card">
          <p
            style={{
              color: "var(--text-muted)",
              fontSize: "12px",
              marginBottom: "6px",
            }}
          >
            Bowlers
          </p>

          <p style={{ fontSize: "26px", fontWeight: 800 }}>
            {roleCounts.BOWLER || 0}
          </p>
        </div>

        <div className="glass-card">
          <p
            style={{
              color: "var(--text-muted)",
              fontSize: "12px",
              marginBottom: "6px",
            }}
          >
            All-Rounders
          </p>

          <p style={{ fontSize: "26px", fontWeight: 800 }}>
            {roleCounts.ALL_ROUNDER || 0}
          </p>
        </div>
      </div>

      <div style={{ marginBottom: "18px" }}>
        <h2 style={{ fontSize: "22px", marginBottom: "6px" }}>
          Squad
        </h2>

        <p
          style={{
            color: "var(--text-muted)",
            fontSize: "14px",
          }}
        >
          Players currently registered under {team.name}.
        </p>
      </div>

      {players.length === 0 ? (
        <div className="glass-card">
          <h3 style={{ marginBottom: "8px" }}>
            No players found
          </h3>

          <p style={{ color: "var(--text-muted)" }}>
            This team currently has no registered players.
          </p>
        </div>
      ) : (
        <div
          style={{
            display: "grid",
            gridTemplateColumns:
              "repeat(auto-fit, minmax(280px, 1fr))",
            gap: "16px",
          }}
        >
          {players.map((player) => (
            <Link
              key={player.id}
              to={`/players/${player.id}`}
              className="glass-card"
              style={{
                display: "block",
                padding: "20px",
              }}
            >
              <div
                style={{
                  display: "flex",
                  justifyContent: "space-between",
                  alignItems: "flex-start",
                  gap: "12px",
                  marginBottom: "16px",
                }}
              >
                <div>
                  <h3
                    style={{
                      fontSize: "19px",
                      marginBottom: "5px",
                    }}
                  >
                    {player.name}
                  </h3>

                  <p
                    style={{
                      color: "var(--accent-cyan)",
                      fontSize: "12px",
                      fontWeight: 700,
                    }}
                  >
                    {player.role.replace("_", " ")}
                  </p>
                </div>

                <span
                  style={{
                    color: "var(--text-muted)",
                    fontSize: "11px",
                  }}
                >
                  VIEW
                </span>
              </div>

              <div
                style={{
                  borderTop:
                    "1px solid var(--border-subtle)",
                  paddingTop: "14px",
                }}
              >
                <p
                  style={{
                    color: "var(--text-muted)",
                    fontSize: "13px",
                    marginBottom: "7px",
                  }}
                >
                  <strong style={{ color: "var(--text-main)" }}>
                    Batting
                  </strong>{" "}
                  {player.batting_style || "Not available"}
                </p>

                <p
                  style={{
                    color: "var(--text-muted)",
                    fontSize: "13px",
                  }}
                >
                  <strong style={{ color: "var(--text-main)" }}>
                    Bowling
                  </strong>{" "}
                  {player.bowling_style || "Not available"}
                </p>
              </div>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}

export default TeamDetailPage;