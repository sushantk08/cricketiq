import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";

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
      <div style={{ padding: "40px" }}>
        <h1>Loading player...</h1>
      </div>
    );
  }

  if (error || !player) {
    return (
      <div style={{ padding: "40px" }}>
        <h1>Player Not Found</h1>
        <p>{error || "Unable to load player information."}</p>
      </div>
    );
  }

  const batting = player.batting;
  const bowling = player.bowling;

  return (
    <div style={{ padding: "40px", maxWidth: "1000px", margin: "0 auto" }}>
      <div
        style={{
          border: "1px solid #ddd",
          borderRadius: "12px",
          padding: "24px",
          marginBottom: "24px",
        }}
      >
        <h1>{player.name}</h1>
        <p>
          <strong>Role:</strong> {player.role}
        </p>
        <p>
          <strong>Team:</strong> {player.team_name}
        </p>
      </div>

      <div
        style={{
          border: "1px solid #ddd",
          borderRadius: "12px",
          padding: "24px",
          marginBottom: "24px",
        }}
      >
        <h2>Batting Statistics</h2>

        {batting ? (
          <>
            <p>
              <strong>Innings:</strong> {batting.innings_batted}
            </p>
            <p>
              <strong>Runs:</strong> {batting.total_runs}
            </p>
            <p>
              <strong>Average:</strong> {batting.average}
            </p>
            <p>
              <strong>Strike Rate:</strong> {batting.strike_rate}
            </p>
            <p>
              <strong>Fours:</strong> {batting.fours}
            </p>
            <p>
              <strong>Sixes:</strong> {batting.sixes}
            </p>
            <p>
              <strong>Dot Ball %:</strong> {batting.dot_ball_pct}
            </p>
            <p>
              <strong>Boundary Run %:</strong>{" "}
              {batting.boundary_run_pct}
            </p>
          </>
        ) : (
          <p>No batting data available for this player.</p>
        )}
      </div>

      {batting?.phases && (
        <div
          style={{
            border: "1px solid #ddd",
            borderRadius: "12px",
            padding: "24px",
            marginBottom: "24px",
          }}
        >
          <h2>Batting Phase Performance</h2>

          <h3>Powerplay</h3>
          <p>
            <strong>Runs:</strong>{" "}
            {batting.phases.powerplay?.runs ?? 0}
          </p>
          <p>
            <strong>Balls:</strong>{" "}
            {batting.phases.powerplay?.balls ?? 0}
          </p>
          <p>
            <strong>Strike Rate:</strong>{" "}
            {batting.phases.powerplay?.strike_rate ?? 0}
          </p>

          <h3>Middle Overs</h3>
          <p>
            <strong>Runs:</strong>{" "}
            {batting.phases.middle?.runs ?? 0}
          </p>
          <p>
            <strong>Balls:</strong>{" "}
            {batting.phases.middle?.balls ?? 0}
          </p>
          <p>
            <strong>Strike Rate:</strong>{" "}
            {batting.phases.middle?.strike_rate ?? 0}
          </p>

          <h3>Death Overs</h3>
          <p>
            <strong>Runs:</strong>{" "}
            {batting.phases.death?.runs ?? 0}
          </p>
          <p>
            <strong>Balls:</strong>{" "}
            {batting.phases.death?.balls ?? 0}
          </p>
          <p>
            <strong>Strike Rate:</strong>{" "}
            {batting.phases.death?.strike_rate ?? 0}
          </p>
        </div>
      )}

      <div
        style={{
          border: "1px solid #ddd",
          borderRadius: "12px",
          padding: "24px",
          marginBottom: "24px",
        }}
      >
        <h2>Bowling Statistics</h2>

        {bowling ? (
          <>
            <p>
              <strong>Innings:</strong>{" "}
              {bowling.innings_bowled ?? 0}
            </p>
            <p>
              <strong>Overs:</strong> {bowling.overs_bowled ?? 0}
            </p>
            <p>
              <strong>Runs Conceded:</strong>{" "}
              {bowling.runs_conceded ?? 0}
            </p>
            <p>
              <strong>Wickets:</strong> {bowling.wickets ?? 0}
            </p>
            <p>
              <strong>Economy:</strong> {bowling.economy ?? 0}
            </p>
            <p>
              <strong>Bowling Strike Rate:</strong>{" "}
              {bowling.bowling_strike_rate ?? "N/A"}
            </p>
            <p>
              <strong>Dot Ball %:</strong>{" "}
              {bowling.dot_ball_pct ?? 0}
            </p>
          </>
        ) : (
          <p>No bowling data available for this player.</p>
        )}
      </div>
    </div>
  );
}

export default PlayerDetailPage;