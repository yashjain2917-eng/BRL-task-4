
import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import api from "../api/axios";

function Register() {
  const navigate = useNavigate();
  const [form, setForm] = useState({
    username: "",
    email: "",
    password: "",
  });
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setLoading(true);

    try {
      await api.post("auth/register/", form);
      navigate("/login", {
        state: { message: "Registration successful. Please log in." },
      });
    } catch (err) {
      setError(JSON.stringify(err.response?.data || "Registration failed."));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-container">
      <form className="auth-card" onSubmit={handleSubmit}>
        <h1>Create Account</h1>
        <p>Register for the Real-Time Support Desk.</p>

        <label>Username</label>
        <input
          name="username"
          value={form.username}
          onChange={handleChange}
          required
        />

        <label>Email</label>
        <input
          type="email"
          name="email"
          value={form.email}
          onChange={handleChange}
          required
        />

        <label>Password</label>
        <input
          type="password"
          name="password"
          value={form.password}
          onChange={handleChange}
          minLength={8}
          required
        />

        {error && <p className="error">{error}</p>}

        <button type="submit" disabled={loading}>
          {loading ? "Registering..." : "Register"}
        </button>

        <p>
          Already registered? <Link to="/login">Login</Link>
        </p>
      </form>
    </div>
  );
}

export default Register;
