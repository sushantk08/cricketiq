import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";

function TeamDetailPage() {
  const { id } = useParams();

  const [team, setTeam] = useState(null);
  const [players, setPlayers] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      fetch("http://127.0.0.1:8000/api/teams").then((response) =>
        response.json()
      ),
      fetch(`http://127.0.0.1:8000/api/players?team_id=${id}`).then(
        (response) => response.json()
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
    return <div style={{ padding: "40px" }}>Loading team...</div>;
  }

  if (!team) {
    return <div style={{ padding: "40px" }}>Team not found.</div>;
  }

  return (
    <div style={{ padding: "40px" }}>
      <h1>{team.name}</h1>

      <p>Short Name: {team.short_name}</p>
      <p>Players: {players.length}</p>

      <h2>Squad</h2>

      {players.length === 0 ? (
        <p>No players found for this team.</p>
      ) : (
        players.map((player) => (
          <div
            key={player.id}
            style={{
              border: "1px solid #ddd",
              borderRadius: "8px",
              padding: "16px",
              marginBottom: "12px",
            }}
          >
            <h3>{player.name}</h3>
            <p>Role: {player.role}</p>
            <p>Batting: {player.batting_style}</p>
            <p>
              Bowling: {player.bowling_style || "Not available"}
            </p>
          </div>
        ))
      )}
    </div>
  );
}

export default TeamDetailPage;