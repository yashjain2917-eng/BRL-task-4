
import { useState } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import api from "../api/axios";

function Login() {
  const navigate = useNavigate();
  const location = useLocation();

  const [form, setForm] = useState({
    username: "",
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
      const response = await api.post("auth/login/", form);

      localStorage.setItem("access_token", response.data.access);

      if (response.data.refresh) {
        localStorage.setItem("refresh_token", response.data.refresh);
      }

      navigate("/dashboard");
    } catch (err) {
      setError(
        JSON.stringify(err.response?.data || "Login failed.")
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-container">
      <form className="auth-card" onSubmit={handleSubmit}>
        <h1>Welcome Back</h1>
        <p>Log in to your support desk account.</p>

        {location.state?.message && (
          <p>{location.state.message}</p>
        )}

        <label>Username</label>
        <input
          name="username"
          value={form.username}
          onChange={handleChange}
          required
        />

        <label>Password</label>
        <input
          type="password"
          name="password"
          value={form.password}
          onChange={handleChange}
          required
        />

        {error && <p className="error">{error}</p>}

        <button type="submit" disabled={loading}>
          {loading ? "Logging in..." : "Login"}
        </button>

        <p>
          Don't have an account? <Link to="/register">Register</Link>
        </p>
      </form>
    </div>
  );
}

export default Login;
