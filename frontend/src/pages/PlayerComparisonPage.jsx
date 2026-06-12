import { useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import {
  fetchPlayers,
  fetchPlayerComparison,
} from "../services/api";

function PlayerComparisonPage() {
  const [players, setPlayers] = useState([]);

  const [player1Id, setPlayer1Id] = useState("");
  const [player2Id, setPlayer2Id] = useState("");

  const [comparison, setComparison] = useState(null);
  const [loadingPlayers, setLoadingPlayers] = useState(true);
  const [loadingComparison, setLoadingComparison] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    const loadPlayers = async () => {
      try {
        setLoadingPlayers(true);
        setError("");

        const data = await fetchPlayers();
        setPlayers(data);
      } catch (err) {
        setError("Failed to load players.");
      } finally {
        setLoadingPlayers(false);
      }
    };

    loadPlayers();
  }, []);

  const selectedPlayer1 = useMemo(
    () => players.find((player) => String(player.id) === String(player1Id)),
    [players, player1Id]
  );

  const selectedPlayer2 = useMemo(
    () => players.find((player) => String(player.id) === String(player2Id)),
    [players, player2Id]
  );

  const handleCompare = async () => {
    if (!player1Id || !player2Id) {
      setError("Please select both players.");
      return;
    }

    if (player1Id === player2Id) {
      setError("Please select two different players.");
      return;
    }

    try {
      setLoadingComparison(true);
      setError("");
      setComparison(null);

      const data = await fetchPlayerComparison(
        player1Id,
        player2Id
      );

      setComparison(data);
    } catch (err) {
      setError(err.message || "Failed to compare players.");
    } finally {
      setLoadingComparison(false);
    }
  };

  const cardStyle = {
    background: "var(--bg-main)",
    border: "1px solid var(--border-subtle)",
    borderRadius: "10px",
    padding: "18px",
  };

  const metricRow = (label, value1, value2) => (
    <div
      style={{
        display: "grid",
        gridTemplateColumns: "1fr 160px 1fr",
        gap: "16px",
        alignItems: "center",
        padding: "12px 0",
        borderBottom: "1px solid var(--border-subtle)",
      }}
    >
      <div
        style={{
          textAlign: "right",
          fontWeight: 700,
        }}
      >
        {value1 ?? "—"}
      </div>

      <div
        style={{
          textAlign: "center",
          color: "var(--text-muted)",
          fontSize: "12px",
          fontWeight: 700,
          textTransform: "uppercase",
        }}
      >
        {label}
      </div>

      <div
        style={{
          fontWeight: 700,
        }}
      >
        {value2 ?? "—"}
      </div>
    </div>
  );

  const battingRows = comparison
    ? [
        metricRow(
          "Innings",
          comparison.player1_stats?.batting?.innings_batted,
          comparison.player2_stats?.batting?.innings_batted
        ),
        metricRow(
          "Runs",
          comparison.player1_stats?.batting?.total_runs,
          comparison.player2_stats?.batting?.total_runs
        ),
        metricRow(
          "Average",
          comparison.player1_stats?.batting?.average,
          comparison.player2_stats?.batting?.average
        ),
        metricRow(
          "Strike Rate",
          comparison.player1_stats?.batting?.strike_rate,
          comparison.player2_stats?.batting?.strike_rate
        ),
        metricRow(
          "Fours",
          comparison.player1_stats?.batting?.fours,
          comparison.player2_stats?.batting?.fours
        ),
        metricRow(
          "Sixes",
          comparison.player1_stats?.batting?.sixes,
          comparison.player2_stats?.batting?.sixes
        ),
        metricRow(
          "Dot Ball %",
          comparison.player1_stats?.batting?.dot_ball_pct,
          comparison.player2_stats?.batting?.dot_ball_pct
        ),
      ]
    : [];

  const bowlingRows = comparison
    ? [
        metricRow(
          "Innings",
          comparison.player1_stats?.bowling?.innings_bowled,
          comparison.player2_stats?.bowling?.innings_bowled
        ),
        metricRow(
          "Overs",
          comparison.player1_stats?.bowling?.overs_bowled,
          comparison.player2_stats?.bowling?.overs_bowled
        ),
        metricRow(
          "Wickets",
          comparison.player1_stats?.bowling?.wickets,
          comparison.player2_stats?.bowling?.wickets
        ),
        metricRow(
          "Economy",
          comparison.player1_stats?.bowling?.economy,
          comparison.player2_stats?.bowling?.economy
        ),
        metricRow(
          "Bowling SR",
          comparison.player1_stats?.bowling?.bowling_strike_rate,
          comparison.player2_stats?.bowling?.bowling_strike_rate
        ),
        metricRow(
          "Dot Ball %",
          comparison.player1_stats?.bowling?.dot_ball_pct,
          comparison.player2_stats?.bowling?.dot_ball_pct
        ),
      ]
    : [];

  if (loadingPlayers) {
    return (
      <div
        style={{
          maxWidth: "1200px",
          margin: "0 auto",
          padding: "40px 48px",
        }}
      >
        <p style={{ color: "var(--text-muted)" }}>
          Loading players...
        </p>
      </div>
    );
  }

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

      <div style={{ marginBottom: "28px" }}>
        <h1
          style={{
            fontSize: "38px",
            fontWeight: 800,
            marginBottom: "8px",
          }}
        >
          Player Comparison
        </h1>

        <p
          style={{
            color: "var(--text-muted)",
            fontSize: "16px",
          }}
        >
          Compare two players using CricketIQ historical
          performance data.
        </p>
      </div>

      <div
        className="glass-card"
        style={{
          display: "grid",
          gridTemplateColumns: "1fr 1fr auto",
          gap: "16px",
          alignItems: "end",
          marginBottom: "28px",
        }}
      >
        <div>
          <label
            style={{
              display: "block",
              color: "var(--text-muted)",
              fontSize: "12px",
              marginBottom: "7px",
            }}
          >
            Player 1
          </label>

          <select
            value={player1Id}
            onChange={(event) => setPlayer1Id(event.target.value)}
            style={{
              width: "100%",
              background: "var(--bg-main)",
              border: "1px solid var(--border-subtle)",
              borderRadius: "8px",
              padding: "12px 14px",
              color: "var(--text-main)",
              fontSize: "14px",
            }}
          >
            <option value="">Select player</option>

            {players.map((player) => (
              <option key={player.id} value={player.id}>
                {player.name}
              </option>
            ))}
          </select>
        </div>

        <div>
          <label
            style={{
              display: "block",
              color: "var(--text-muted)",
              fontSize: "12px",
              marginBottom: "7px",
            }}
          >
            Player 2
          </label>

          <select
            value={player2Id}
            onChange={(event) => setPlayer2Id(event.target.value)}
            style={{
              width: "100%",
              background: "var(--bg-main)",
              border: "1px solid var(--border-subtle)",
              borderRadius: "8px",
              padding: "12px 14px",
              color: "var(--text-main)",
              fontSize: "14px",
            }}
          >
            <option value="">Select player</option>

            {players.map((player) => (
              <option key={player.id} value={player.id}>
                {player.name}
              </option>
            ))}
          </select>
        </div>

        <button
          type="button"
          onClick={handleCompare}
          disabled={loadingComparison}
          style={{
            border: "none",
            borderRadius: "8px",
            padding: "12px 24px",
            background: "var(--accent-cyan)",
            color: "#061018",
            fontWeight: 800,
            cursor: loadingComparison ? "not-allowed" : "pointer",
            opacity: loadingComparison ? 0.7 : 1,
          }}
        >
          {loadingComparison ? "Comparing..." : "Compare"}
        </button>
      </div>

      {selectedPlayer1 && selectedPlayer2 && (
        <div
          style={{
            display: "grid",
            gridTemplateColumns: "1fr 1fr",
            gap: "18px",
            marginBottom: "28px",
          }}
        >
          <div className="glass-card" style={cardStyle}>
            <p
              style={{
                color: "var(--accent-cyan)",
                fontSize: "11px",
                fontWeight: 700,
                textTransform: "uppercase",
                marginBottom: "6px",
              }}
            >
              Player 1
            </p>

            <h2 style={{ fontSize: "24px", marginBottom: "5px" }}>
              {selectedPlayer1.name}
            </h2>

            <p style={{ color: "var(--text-muted)" }}>
              {selectedPlayer1.role?.replace("_", " ")}
            </p>
          </div>

          <div className="glass-card" style={cardStyle}>
            <p
              style={{
                color: "var(--accent-cyan)",
                fontSize: "11px",
                fontWeight: 700,
                textTransform: "uppercase",
                marginBottom: "6px",
              }}
            >
              Player 2
            </p>

            <h2 style={{ fontSize: "24px", marginBottom: "5px" }}>
              {selectedPlayer2.name}
            </h2>

            <p style={{ color: "var(--text-muted)" }}>
              {selectedPlayer2.role?.replace("_", " ")}
            </p>
          </div>
        </div>
      )}

      {error && (
        <div
          className="glass-card"
          style={{
            marginBottom: "24px",
            border: "1px solid rgba(255, 80, 80, 0.3)",
          }}
        >
          <p style={{ color: "#ff8080", margin: 0 }}>{error}</p>
        </div>
      )}

      {comparison && (
        <>
          <div
            className="glass-card"
            style={{
              marginBottom: "24px",
              padding: "24px",
            }}
          >
            <h2 style={{ marginBottom: "10px" }}>
              Comparison Summary
            </h2>

            <p
              style={{
                color: "var(--text-muted)",
                lineHeight: 1.7,
                marginBottom: "18px",
              }}
            >
              {comparison.comparison_summary}
            </p>

            <p
              style={{
                color: "var(--text-muted)",
                fontSize: "12px",
                margin: 0,
              }}
            >
              {comparison.uncertainty_note}
            </p>
          </div>

          <div
            style={{
              display: "grid",
              gridTemplateColumns: "1fr 1fr",
              gap: "18px",
              marginBottom: "24px",
            }}
          >
            <div className="glass-card" style={cardStyle}>
              <p
                style={{
                  color: "var(--text-muted)",
                  fontSize: "12px",
                  marginBottom: "6px",
                }}
              >
                Stronger historical batter
              </p>

              <h2 style={{ fontSize: "24px" }}>
                {comparison.better_batter || "Insufficient data"}
              </h2>
            </div>

            <div className="glass-card" style={cardStyle}>
              <p
                style={{
                  color: "var(--text-muted)",
                  fontSize: "12px",
                  marginBottom: "6px",
                }}
              >
                Stronger historical bowler
              </p>

              <h2 style={{ fontSize: "24px" }}>
                {comparison.better_bowler || "Insufficient data"}
              </h2>
            </div>
          </div>

          <div
            className="glass-card"
            style={{
              marginBottom: "24px",
              padding: "24px",
              overflowX: "auto",
            }}
          >
            <h2 style={{ marginBottom: "6px" }}>Batting Comparison</h2>

            <p
              style={{
                color: "var(--text-muted)",
                fontSize: "13px",
                marginBottom: "12px",
              }}
            >
              Historical batting metrics
            </p>

            {!comparison.player1_stats?.batting &&
            !comparison.player2_stats?.batting ? (
              <p style={{ color: "var(--text-muted)" }}>
                No batting data available for either player.
              </p>
            ) : (
              battingRows
            )}
          </div>

          <div
            className="glass-card"
            style={{
              marginBottom: "24px",
              padding: "24px",
              overflowX: "auto",
            }}
          >
            <h2 style={{ marginBottom: "6px" }}>Bowling Comparison</h2>

            <p
              style={{
                color: "var(--text-muted)",
                fontSize: "13px",
                marginBottom: "12px",
              }}
            >
              Historical bowling metrics
            </p>

            {!comparison.player1_stats?.bowling &&
            !comparison.player2_stats?.bowling ? (
              <p style={{ color: "var(--text-muted)" }}>
                No bowling data available for either player.
              </p>
            ) : (
              bowlingRows
            )}
          </div>
        </>
      )}
    </div>
  );
}

export default PlayerComparisonPage;