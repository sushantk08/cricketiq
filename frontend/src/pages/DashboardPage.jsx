import { useEffect, useState } from "react";

function DashboardPage() {
  const [matches, setMatches] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch("http://127.0.0.1:8000/api/matches")
      .then((response) => response.json())
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

  return (
    <div style={{ padding: "40px" }}>
      <h1>CricketIQ Dashboard</h1>

      <p>Cricket intelligence at a glance.</p>

      <div style={{ marginTop: "30px" }}>
        <h2>Match Overview</h2>

        {loading ? (
          <p>Loading matches...</p>
        ) : (
          <div>
            <p>Total Matches: {matches.length}</p>
            <p>Live Matches: {liveMatches.length}</p>
            <p>Completed Matches: {completedMatches.length}</p>
          </div>
        )}
      </div>

      <div style={{ marginTop: "30px" }}>
        <h2>Live Matches</h2>

        {loading ? (
          <p>Loading...</p>
        ) : liveMatches.length === 0 ? (
          <p>No live matches available.</p>
        ) : (
          liveMatches.slice(0, 5).map((match) => (
            <div
              key={match.id}
              style={{
                border: "1px solid #ddd",
                borderRadius: "8px",
                padding: "16px",
                marginBottom: "12px",
              }}
            >
              <h3>{match.title}</h3>
              <p>Type: {match.match_type}</p>
              <p>Status: {match.status}</p>
              <p>Venue: {match.venue?.name}</p>
            </div>
          ))
        )}
      </div>
    </div>
  );
}

export default DashboardPage;