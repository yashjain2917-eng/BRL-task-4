
import { useEffect, useRef, useState } from "react";
import { Link, useParams } from "react-router-dom";
import api from "../api/axios";

function TicketDetails() {
  const { id } = useParams();
  const [messages, setMessages] = useState([]);
  const [content, setContent] = useState("");
  const [error, setError] = useState("");
  const [connected, setConnected] = useState(false);
  const socketRef = useRef(null);
  const bottomRef = useRef(null);

  useEffect(() => {
    let socket;
    let active = true;

    async function loadMessages() {
      try {
        const response = await api.get(`tickets/${id}/messages/`);
        if (active) {
          const data = response.data;
          setMessages(Array.isArray(data) ? data : data.results || []);
        }
      } catch (err) {
        if (active) {
          setError(
            JSON.stringify(err.response?.data || "Could not load messages.")
          );
        }
      }
    }

    const token = localStorage.getItem("access_token");

    if (!token) {
      setError("Please log in before opening this ticket.");
      return;
    }

    loadMessages();

    const wsUrl =
      `ws://127.0.0.1:8000/ws/tickets/${id}/?token=${encodeURIComponent(token)}`;

    socket = new WebSocket(wsUrl);
    socketRef.current = socket;

    socket.onopen = () => {
      if (active) setConnected(true);
    };

    socket.onmessage = (event) => {
      if (!active) return;

      const data = JSON.parse(event.data);

      if (data.type === "message") {
        setMessages((previous) => {
          if (previous.some((message) => message.id === data.message.id)) {
            return previous;
          }
          return [...previous, data.message];
        });
      } else if (data.type === "error") {
        setError(data.message);
      } else if (data.type === "typing") {
        // Typing events can be displayed here if needed.
      }
    };

    socket.onerror = () => {
      if (active) setError("WebSocket connection error. Check the backend.");
    };

    socket.onclose = () => {
      if (active) setConnected(false);
    };

    return () => {
      active = false;
      socket?.close();
      socketRef.current = null;
    };
  }, [id]);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const sendMessage = (event) => {
    event.preventDefault();

    const text = content.trim();
    if (!text || !socketRef.current || socketRef.current.readyState !== WebSocket.OPEN) {
      setError("Connect to the chat before sending a message.");
      return;
    }

    socketRef.current.send(
      JSON.stringify({ type: "message", content: text })
    );

    setContent("");
    setError("");
  };

  return (
    <main className="dashboard">
      <p><Link to="/dashboard">← Back to Dashboard</Link></p>

      <section className="ticket-form-card">
        <h1>Ticket #{id} — Conversation</h1>
        <p>
          WebSocket status:{" "}
          <strong>{connected ? "Connected" : "Disconnected"}</strong>
        </p>

        {error && <p className="error">{error}</p>}

        <div className="chat-messages">
          {messages.map((message) => (
            <article className="chat-message" key={message.id}>
              <strong>{message.sender}</strong>
              <p>{message.content}</p>
              <small>{new Date(message.created_at).toLocaleString()}</small>
            </article>
          ))}
          <div ref={bottomRef} />
        </div>

        <form onSubmit={sendMessage}>
          <label>Message</label>
          <textarea
            value={content}
            onChange={(event) => setContent(event.target.value)}
            maxLength={5000}
            rows={3}
            required
            placeholder="Write your message..."
          />
          <button type="submit" disabled={!connected}>
            Send Message
          </button>
        </form>
      </section>
    </main>
  );
}

export default TicketDetails;
