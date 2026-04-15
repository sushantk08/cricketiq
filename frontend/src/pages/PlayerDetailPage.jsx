import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";

function PlayerDetailPage() {
  const { id } = useParams();
  const [player, setPlayer] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch(`http://127.0.0.1:8000/api/players/${id}/stats`)
      .then((response) => response.json())
      .then((data) => {
        setPlayer(data);
        setLoading(false);
      })
      .catch(() => {
        setPlayer(null);
        setLoading(false);
      });
  }, [id]);

  if (loading) {
    return <div style={{ padding: "40px" }}>Loading player...</div>;
  }

  if (!player) {
    return <div style={{ padding: "40px" }}>Player not found.</div>;
  }

  return (
    <div style={{ padding: "40px" }}>
      <h1>{player.name}</h1>
      <p>{player.role}</p>
      <p>Team: {player.team_name}</p>

      <hr />

      <h2>Batting Statistics</h2>

      <p>Innings: {player.batting.innings_batted}</p>
      <p>Runs: {player.batting.total_runs}</p>
      <p>Average: {player.batting.average}</p>
      <p>Strike Rate: {player.batting.strike_rate}</p>
      <p>Fours: {player.batting.fours}</p>
      <p>Sixes: {player.batting.sixes}</p>
      <p>Dot Ball %: {player.batting.dot_ball_pct}</p>
      <p>Boundary Run %: {player.batting.boundary_run_pct}</p>

      <h2>Phase Performance</h2>

      <h3>Powerplay</h3>
      <p>Runs: {player.batting.phases.powerplay.runs}</p>
      <p>Balls: {player.batting.phases.powerplay.balls}</p>
      <p>Strike Rate: {player.batting.phases.powerplay.strike_rate}</p>

      <h3>Middle Overs</h3>
      <p>Runs: {player.batting.phases.middle.runs}</p>
      <p>Balls: {player.batting.phases.middle.balls}</p>
      <p>Strike Rate: {player.batting.phases.middle.strike_rate}</p>

      <h3>Death Overs</h3>
      <p>Runs: {player.batting.phases.death.runs}</p>
      <p>Balls: {player.batting.phases.death.balls}</p>
      <p>Strike Rate: {player.batting.phases.death.strike_rate}</p>
    </div>
  );
}

export default PlayerDetailPage;