import { useState } from "react";
import { api } from "./api";
import { LogIn, UserPlus } from "lucide-react";

function AuthPanel({ onLogin }) {
  const [mode, setMode] = useState("login");
  const [email, setEmail] = useState("test@example.com");
  const [password, setPassword] = useState("password123");
  const [message, setMessage] = useState("");
  const [cost, setCost] = useState(null);
  async function handleSubmit(e) {
    e.preventDefault();
    setMessage("");

    try {
      if (mode === "register") {
        await api.post("/auth/register", {
          email,
          password,
        });

        setMessage("Account created. You can now log in.");
        setMode("login");
        return;
      }

      const response = await api.post("/auth/login", {
        email,
        password,
      });

      localStorage.setItem("access_token", response.data.access_token);
      localStorage.setItem("user_email", response.data.email);

      onLogin(response.data);
    } catch (error) {
      setMessage(error.response?.data?.detail || "Authentication failed.");
    }
  }

  return (
    <div className="auth-card">
      <div className="auth-toggle">
        <button
          type="button"
          className={mode === "login" ? "active" : ""}
          onClick={() => setMode("login")}
        >
          <LogIn size={16} />
          Login
        </button>

        <button
          type="button"
          className={mode === "register" ? "active" : ""}
          onClick={() => setMode("register")}
        >
          <UserPlus size={16} />
          Sign up
        </button>
      </div>

      <form onSubmit={handleSubmit} className="chat-form">
        <label>
          Email
          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
          />
        </label>

        <label>
          Password
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />
        </label>

        <button type="submit">
          {mode === "login" ? "Login" : "Create Account"}
        </button>
      </form>

      {message && <p className="auth-message">{message}</p>}
    </div>
  );
}

export default AuthPanel;