import { useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";

function PlayersPage() {
  const [players, setPlayers] = useState([]);
  const [teams, setTeams] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");
  const [roleFilter, setRoleFilter] = useState("ALL");
  const [teamFilter, setTeamFilter] = useState("ALL");

  useEffect(() => {
    Promise.all([
      fetch("http://127.0.0.1:8000/api/players").then((response) =>
        response.json()
      ),
      fetch("http://127.0.0.1:8000/api/teams").then((response) =>
        response.json()
      ),
    ])
      .then(([playersData, teamsData]) => {
        setPlayers(playersData);
        setTeams(teamsData);
        setLoading(false);
      })
      .catch(() => {
        setPlayers([]);
        setTeams([]);
        setLoading(false);
      });
  }, []);

  const getTeamName = (teamId) => {
    const team = teams.find((item) => item.id === teamId);
    return team ? team.name : "No team";
  };

  const filteredPlayers = useMemo(() => {
    return players.filter((player) => {
      const matchesSearch = player.name
        .toLowerCase()
        .includes(search.toLowerCase());

      const matchesRole =
        roleFilter === "ALL" || player.role === roleFilter;

      const matchesTeam =
        teamFilter === "ALL" || String(player.team_id) === teamFilter;

      return matchesSearch && matchesRole && matchesTeam;
    });
  }, [players, search, roleFilter, teamFilter]);

  const roles = [...new Set(players.map((player) => player.role))];

  return (
    <div
      style={{
        padding: "40px 48px",
        maxWidth: "1500px",
        margin: "0 auto",
      }}
    >
      <div style={{ marginBottom: "28px" }}>
        <h1
          style={{
            fontSize: "38px",
            fontWeight: 800,
            marginBottom: "8px",
          }}
        >
          Players
        </h1>

        <p style={{ color: "var(--text-muted)", fontSize: "16px" }}>
          Explore player profiles, roles, and cricket attributes.
        </p>
      </div>

      <div
        className="glass-card"
        style={{
          display: "flex",
          gap: "14px",
          flexWrap: "wrap",
          alignItems: "center",
          marginBottom: "28px",
        }}
      >
        <input
          type="text"
          placeholder="Search players..."
          value={search}
          onChange={(event) => setSearch(event.target.value)}
          style={{
            flex: "1 1 280px",
            minWidth: "240px",
            background: "var(--bg-main)",
            border: "1px solid var(--border-subtle)",
            borderRadius: "8px",
            padding: "12px 14px",
            color: "var(--text-main)",
            outline: "none",
            fontSize: "14px",
          }}
        />

        <select
          value={roleFilter}
          onChange={(event) => setRoleFilter(event.target.value)}
          style={{
            background: "var(--bg-main)",
            border: "1px solid var(--border-subtle)",
            borderRadius: "8px",
            padding: "12px 14px",
            color: "var(--text-main)",
            fontSize: "14px",
          }}
        >
          <option value="ALL">All Roles</option>
          {roles.map((role) => (
            <option key={role} value={role}>
              {role.replace("_", " ")}
            </option>
          ))}
        </select>

        <select
          value={teamFilter}
          onChange={(event) => setTeamFilter(event.target.value)}
          style={{
            background: "var(--bg-main)",
            border: "1px solid var(--border-subtle)",
            borderRadius: "8px",
            padding: "12px 14px",
            color: "var(--text-main)",
            fontSize: "14px",
          }}
        >
          <option value="ALL">All Teams</option>

          {teams.map((team) => (
            <option key={team.id} value={String(team.id)}>
              {team.name}
            </option>
          ))}
        </select>
      </div>

      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          marginBottom: "18px",
        }}
      >
        <h2 style={{ fontSize: "20px" }}>Player Directory</h2>

        <span
          style={{
            color: "var(--text-muted)",
            fontSize: "14px",
          }}
        >
          {filteredPlayers.length} players
        </span>
      </div>

      {loading ? (
        <p style={{ color: "var(--text-muted)" }}>Loading players...</p>
      ) : filteredPlayers.length === 0 ? (
        <div
          className="glass-card"
          style={{
            textAlign: "center",
            padding: "50px 20px",
          }}
        >
          <h3 style={{ marginBottom: "8px" }}>No players found</h3>
          <p style={{ color: "var(--text-muted)" }}>
            Try changing your search or filters.
          </p>
        </div>
      ) : (
        <div
          style={{
            display: "grid",
            gridTemplateColumns:
              "repeat(auto-fill, minmax(300px, 1fr))",
            gap: "18px",
          }}
        >
          {filteredPlayers.map((player) => (
            <Link
              key={player.id}
              to={`/players/${player.id}`}
              className="glass-card"
              style={{
                display: "block",
                padding: "22px",
                transition: "transform 0.2s ease",
              }}
            >
              <div
                style={{
                  display: "flex",
                  justifyContent: "space-between",
                  alignItems: "flex-start",
                  gap: "12px",
                  marginBottom: "18px",
                }}
              >
                <div>
                  <h3
                    style={{
                      fontSize: "20px",
                      marginBottom: "5px",
                    }}
                  >
                    {player.name}
                  </h3>

                  <p
                    style={{
                      color: "var(--accent-cyan)",
                      fontSize: "13px",
                      fontWeight: 700,
                    }}
                  >
                    {player.role.replace("_", " ")}
                  </p>
                </div>

                <span
                  style={{
                    background: "rgba(0, 210, 255, 0.08)",
                    border: "1px solid rgba(0, 210, 255, 0.2)",
                    borderRadius: "999px",
                    padding: "5px 9px",
                    color: "var(--accent-cyan)",
                    fontSize: "11px",
                    fontWeight: 600,
                  }}
                >
                  {getTeamName(player.team_id)}
                </span>
              </div>

              <div
                style={{
                  borderTop: "1px solid var(--border-subtle)",
                  paddingTop: "14px",
                }}
              >
                <p
                  style={{
                    color: "var(--text-muted)",
                    fontSize: "13px",
                    marginBottom: "8px",
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

export default PlayersPage;