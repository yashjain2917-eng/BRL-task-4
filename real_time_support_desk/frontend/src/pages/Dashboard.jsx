
import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import api from "../api/axios";

function Dashboard() {
  const navigate = useNavigate();

  const [tickets, setTickets] = useState([]);
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [priority, setPriority] = useState("MEDIUM");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);

  const loadTickets = async () => {
    try {
      const response = await api.get("tickets/");
      const data = response.data;

      setTickets(Array.isArray(data) ? data : data.results || []);
      setError("");
    } catch (err) {
      setError(
        err.response?.data
          ? JSON.stringify(err.response.data)
          : "Could not load tickets. Check that the backend is running."
      );
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (!localStorage.getItem("access_token")) {
      navigate("/login", { replace: true });
      return;
    }

    loadTickets();
  }, []);

  const handleCreateTicket = async (e) => {
    e.preventDefault();
    setError("");

    try {
      await api.post("tickets/", {
        title,
        description,
        priority,
      });

      setTitle("");
      setDescription("");
      setPriority("MEDIUM");

      await loadTickets();
    } catch (err) {
      setError(
        err.response?.data
          ? JSON.stringify(err.response.data)
          : "Could not create ticket."
      );
    }
  };

  const handleLogout = async () => {
    const refresh = localStorage.getItem("refresh_token");

    try {
      if (refresh) {
        await api.post("auth/logout/", { refresh });
      }
    } catch (err) {
      console.error("Server logout failed:", err.response?.data || err);
    } finally {
      localStorage.removeItem("access_token");
      localStorage.removeItem("refresh_token");
      navigate("/login", { replace: true });
    }
  };

  return (
    <main className="dashboard">
      <header className="dashboard-header">
        <div>
          <h1>Real-Time Support Desk</h1>
          <p>Manage your support requests.</p>
        </div>

        <button onClick={handleLogout}>Logout</button>
      </header>

      {error && <p className="error">{error}</p>}

      <section className="ticket-form-card">
        <h2>Create a Support Ticket</h2>

        <form onSubmit={handleCreateTicket}>
          <label>Ticket Title</label>
          <input
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            maxLength={200}
            required
            placeholder="Enter ticket title"
          />

          <label>Description</label>
          <textarea
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            required
            placeholder="Describe the problem"
            rows={4}
          />

          <label>Priority</label>
          <select
            value={priority}
            onChange={(e) => setPriority(e.target.value)}
          >
            <option value="LOW">Low</option>
            <option value="MEDIUM">Medium</option>
            <option value="HIGH">High</option>
          </select>

          <button type="submit">Create Ticket</button>
        </form>
      </section>

      <section className="tickets-section">
        <h2>Your Tickets</h2>

        {loading ? (
          <p>Loading tickets...</p>
        ) : tickets.length === 0 ? (
          <p>No tickets found. Create your first ticket above.</p>
        ) : (
          <div className="ticket-list">
            {tickets.map((ticket) => (
              <article className="ticket-card" key={ticket.id}>
                <h3>
                  #{ticket.id} — {ticket.title}
                </h3>

                <p>{ticket.description}</p>

                <p>
                  <strong>Status:</strong> {ticket.status}
                </p>

                <p>
                  <strong>Priority:</strong> {ticket.priority}
                </p>

                <p>
                  <strong>Assigned Agent:</strong>{" "}
                  {ticket.assigned_to || "Not assigned"}
                </p>
                <button onClick={() => navigate(`/tickets/${ticket.id}`)}>
                  Open Conversation
                </button>
              </article>
            ))}
          </div>
        )}

        <button onClick={loadTickets}>Refresh Tickets</button>
      </section>
    </main>
  );
}

export default Dashboard;
