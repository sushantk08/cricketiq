import { useEffect, useState } from "react";

function PlayersPage() {
  const [players, setPlayers] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch("http://127.0.0.1:8000/api/players")
      .then((response) => response.json())
      .then((data) => {
        setPlayers(data);
        setLoading(false);
      })
      .catch(() => {
        setPlayers([]);
        setLoading(false);
      });
  }, []);

  return (
    <div style={{ padding: "40px" }}>
      <h1>Players</h1>

      {loading ? (
        <p>Loading players...</p>
      ) : players.length === 0 ? (
        <p>No players found.</p>
      ) : (
        <div>
          {players.map((player) => (
            <div
              key={player.id}
              style={{
                border: "1px solid #ddd",
                borderRadius: "8px",
                padding: "16px",
                marginBottom: "12px",
              }}
            >
              <h2>{player.name}</h2>
              <p>Role: {player.role}</p>
              <p>Batting: {player.batting_style}</p>
              <p>
                Bowling: {player.bowling_style || "Not available"}
              </p>
              <p>Team ID: {player.team_id}</p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default PlayersPage;