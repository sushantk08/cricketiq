import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";

function PlayerDetailPage() {
  const { id } = useParams();

  const [player, setPlayer] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    const fetchPlayer = async () => {
      try {
        setLoading(true);
        setError("");

        const response = await fetch(
          `http://127.0.0.1:8000/api/players/${id}/stats`
        );

        if (!response.ok) {
          throw new Error("Failed to fetch player data.");
        }

        const data = await response.json();
        setPlayer(data);
      } catch (err) {
        setError(err.message);
        setPlayer(null);
      } finally {
        setLoading(false);
      }
    };

    fetchPlayer();
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
        <p style={{ color: "var(--text-muted)" }}>Loading player...</p>
      </div>
    );
  }

  if (error || !player) {
    return (
      <div
        style={{
          maxWidth: "1200px",
          margin: "0 auto",
          padding: "40px 48px",
        }}
      >
        <div className="glass-card">
          <h1 style={{ marginBottom: "10px" }}>Player Not Found</h1>
          <p style={{ color: "var(--text-muted)" }}>
            {error || "Unable to load player information."}
          </p>
        </div>
      </div>
    );
  }

  const batting = player.batting;
  const bowling = player.bowling;

  const phaseData = batting?.phases || {};

  const phaseCards = [
    {
      name: "Powerplay",
      key: "powerplay",
    },
    {
      name: "Middle Overs",
      key: "middle",
    },
    {
      name: "Death Overs",
      key: "death",
    },
  ];

  const statCard = (label, value) => (
    <div
      style={{
        background: "var(--bg-main)",
        border: "1px solid var(--border-subtle)",
        borderRadius: "10px",
        padding: "16px",
      }}
    >
      <p
        style={{
          color: "var(--text-muted)",
          fontSize: "12px",
          marginBottom: "6px",
        }}
      >
        {label}
      </p>

      <p
        style={{
          fontSize: "22px",
          fontWeight: 700,
        }}
      >
        {value}
      </p>
    </div>
  );

  return (
    <div
      style={{
        maxWidth: "1200px",
        margin: "0 auto",
        padding: "40px 48px",
      }}
    >
      <Link
        to="/players"
        style={{
          display: "inline-block",
          color: "var(--accent-cyan)",
          fontSize: "14px",
          marginBottom: "20px",
        }}
      >
        ← Back to Players
      </Link>

      <div
        className="glass-card"
        style={{
          marginBottom: "24px",
          padding: "28px",
        }}
      >
        <p
          style={{
            color: "var(--accent-cyan)",
            fontSize: "13px",
            fontWeight: 700,
            marginBottom: "8px",
          }}
        >
          PLAYER PROFILE
        </p>

        <h1
          style={{
            fontSize: "34px",
            fontWeight: 800,
            marginBottom: "12px",
          }}
        >
          {player.name}
        </h1>

        <div
          style={{
            display: "flex",
            gap: "12px",
            flexWrap: "wrap",
          }}
        >
          <span
            style={{
              background: "rgba(0, 210, 255, 0.08)",
              border: "1px solid rgba(0, 210, 255, 0.2)",
              borderRadius: "999px",
              padding: "7px 12px",
              color: "var(--accent-cyan)",
              fontSize: "12px",
              fontWeight: 700,
            }}
          >
            {player.role.replace("_", " ")}
          </span>

          <span
            style={{
              background: "var(--bg-main)",
              border: "1px solid var(--border-subtle)",
              borderRadius: "999px",
              padding: "7px 12px",
              color: "var(--text-muted)",
              fontSize: "12px",
            }}
          >
            {player.team_name || "No team"}
          </span>
        </div>
      </div>

      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fit, minmax(300px, 1fr))",
          gap: "20px",
          marginBottom: "24px",
        }}
      >
        {batting && (
          <div className="glass-card">
            <p
              style={{
                color: "var(--accent-cyan)",
                fontSize: "12px",
                fontWeight: 700,
                marginBottom: "6px",
              }}
            >
              BATTING
            </p>

            <h2 style={{ fontSize: "22px", marginBottom: "18px" }}>
              Batting Performance
            </h2>

            <div
              style={{
                display: "grid",
                gridTemplateColumns:
                  "repeat(2, minmax(0, 1fr))",
                gap: "12px",
              }}
            >
              {statCard("Runs", batting.total_runs)}
              {statCard("Average", batting.average)}
              {statCard("Strike Rate", batting.strike_rate)}
              {statCard("Innings", batting.innings_batted)}
              {statCard("Fours", batting.fours)}
              {statCard("Sixes", batting.sixes)}
            </div>
          </div>
        )}

        {bowling && (
          <div className="glass-card">
            <p
              style={{
                color: "var(--accent-cyan)",
                fontSize: "12px",
                fontWeight: 700,
                marginBottom: "6px",
              }}
            >
              BOWLING
            </p>

            <h2 style={{ fontSize: "22px", marginBottom: "18px" }}>
              Bowling Performance
            </h2>

            <div
              style={{
                display: "grid",
                gridTemplateColumns:
                  "repeat(2, minmax(0, 1fr))",
                gap: "12px",
              }}
            >
              {statCard("Wickets", bowling.wickets)}
              {statCard("Economy", bowling.economy)}
              {statCard("Overs", bowling.overs_bowled)}
              {statCard("Runs Conceded", bowling.runs_conceded)}
              {statCard(
                "Dot Ball %",
                bowling.dot_ball_pct
              )}
              {statCard(
                "Strike Rate",
                bowling.bowling_strike_rate ?? "N/A"
              )}
            </div>
          </div>
        )}
      </div>

      {batting && (
        <div className="glass-card" style={{ marginBottom: "24px" }}>
          <div style={{ marginBottom: "20px" }}>
            <p
              style={{
                color: "var(--accent-cyan)",
                fontSize: "12px",
                fontWeight: 700,
                marginBottom: "6px",
              }}
            >
              PHASE ANALYSIS
            </p>

            <h2 style={{ fontSize: "22px" }}>
              Batting Phase Performance
            </h2>
          </div>

          <div
            style={{
              display: "grid",
              gridTemplateColumns:
                "repeat(auto-fit, minmax(220px, 1fr))",
              gap: "16px",
            }}
          >
            {phaseCards.map((phase) => {
              const data = phaseData[phase.key];

              return (
                <div
                  key={phase.key}
                  style={{
                    background: "var(--bg-main)",
                    border: "1px solid var(--border-subtle)",
                    borderRadius: "10px",
                    padding: "18px",
                  }}
                >
                  <h3
                    style={{
                      fontSize: "16px",
                      marginBottom: "16px",
                    }}
                  >
                    {phase.name}
                  </h3>

                  <p
                    style={{
                      color: "var(--text-muted)",
                      fontSize: "13px",
                      marginBottom: "8px",
                    }}
                  >
                    Runs:{" "}
                    <strong style={{ color: "var(--text-main)" }}>
                      {data?.runs ?? 0}
                    </strong>
                  </p>

                  <p
                    style={{
                      color: "var(--text-muted)",
                      fontSize: "13px",
                      marginBottom: "8px",
                    }}
                  >
                    Balls:{" "}
                    <strong style={{ color: "var(--text-main)" }}>
                      {data?.balls ?? 0}
                    </strong>
                  </p>

                  <p
                    style={{
                      color: "var(--text-muted)",
                      fontSize: "13px",
                    }}
                  >
                    Strike Rate:{" "}
                    <strong style={{ color: "var(--text-main)" }}>
                      {data?.strike_rate ?? 0}
                    </strong>
                  </p>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {bowling && (
  <div className="glass-card" style={{ marginBottom: "24px" }}>
    <div style={{ marginBottom: "20px" }}>
      <p
        style={{
          color: "var(--accent-cyan)",
          fontSize: "12px",
          fontWeight: 700,
          marginBottom: "6px",
        }}
      >
        PHASE ANALYSIS
      </p>

      <h2 style={{ fontSize: "22px" }}>
        Bowling Phase Performance
      </h2>
    </div>

    <div
      style={{
        display: "grid",
        gridTemplateColumns:
          "repeat(auto-fit, minmax(220px, 1fr))",
        gap: "16px",
      }}
    >
      {phaseCards.map((phase) => {
        const data = bowling.phases?.[phase.key];

        return (
          <div
            key={phase.key}
            style={{
              background: "var(--bg-main)",
              border: "1px solid var(--border-subtle)",
              borderRadius: "10px",
              padding: "18px",
            }}
          >
            <h3
              style={{
                fontSize: "16px",
                marginBottom: "16px",
              }}
            >
              {phase.name}
            </h3>

            <p
              style={{
                color: "var(--text-muted)",
                fontSize: "13px",
                marginBottom: "8px",
              }}
            >
              Overs:{" "}
              <strong style={{ color: "var(--text-main)" }}>
                {data?.overs ?? 0}
              </strong>
            </p>

            <p
              style={{
                color: "var(--text-muted)",
                fontSize: "13px",
                marginBottom: "8px",
              }}
            >
              Runs:{" "}
              <strong style={{ color: "var(--text-main)" }}>
                {data?.runs ?? 0}
              </strong>
            </p>

            <p
              style={{
                color: "var(--text-muted)",
                fontSize: "13px",
                marginBottom: "8px",
              }}
            >
              Wickets:{" "}
              <strong style={{ color: "var(--text-main)" }}>
                {data?.wickets ?? 0}
              </strong>
            </p>

            <p
              style={{
                color: "var(--text-muted)",
                fontSize: "13px",
              }}
            >
              Economy:{" "}
              <strong style={{ color: "var(--text-main)" }}>
                {data?.economy ?? 0}
              </strong>
            </p>
          </div>
        );
      })}
    </div>
  </div>
)}

      {!batting && !bowling && (
        <div className="glass-card">
          <h2 style={{ marginBottom: "8px" }}>
            No Performance Data
          </h2>

          <p style={{ color: "var(--text-muted)" }}>
            No batting or bowling statistics are available for
            this player.
          </p>
        </div>
      )}
    </div>
  );
}

export default PlayerDetailPage;