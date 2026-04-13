import { useEffect, useState } from "react";

function DashboardPage() {
  const [health, setHealth] = useState(null);

  useEffect(() => {
    fetch("http://127.0.0.1:8000/health")
      .then((response) => response.json())
      .then((data) => setHealth(data))
      .catch(() => setHealth(null));
  }, []);

  return (
    <div>
      <h1>CricketIQ Dashboard</h1>

      <p>Welcome to your cricket intelligence dashboard.</p>

      <div>
        <h2>System Status</h2>

        {health ? (
          <p>
            Backend: <strong>Connected</strong>
          </p>
        ) : (
          <p>
            Backend: <strong>Not Connected</strong>
          </p>
        )}
      </div>
    </div>
  );
}

export default DashboardPage;