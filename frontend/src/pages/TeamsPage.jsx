import { useEffect, useState } from "react";
import { Link } from "react-router-dom";

function TeamsPage() {
  const [teams, setTeams] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch("http://127.0.0.1:8000/api/teams")
      .then((response) => response.json())
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
    <div style={{ padding: "40px" }}>
      <h1>Teams</h1>

      {loading ? (
        <p>Loading teams...</p>
      ) : teams.length === 0 ? (
        <p>No teams found.</p>
      ) : (
        <div>
          {teams.map((team) => (
            <div
              key={team.id}
              style={{
                border: "1px solid #ddd",
                borderRadius: "8px",
                padding: "16px",
                marginBottom: "12px",
              }}
            >
              <h2>
  <Link
    to={`/teams/${team.id}`}
    style={{ textDecoration: "none" }}
  >
    {team.name}
  </Link>
</h2>
              <p>Short Name: {team.short_name}</p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default TeamsPage;