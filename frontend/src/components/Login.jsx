import { useState, useContext } from "react";
import { useNavigate } from "react-router-dom";
import { AuthContext } from "./AuthContext";
import "./Auth.css";

export default function Login() {
  const nav = useNavigate();
  const { login } = useContext(AuthContext);

  const [form, setForm] = useState({
    email: "",
    parola: "",
    rol: "cursant"
  });

  const [showPassword, setShowPassword] = useState(false);

  function updateField(e) {
    setForm({ ...form, [e.target.name]: e.target.value });
  }

  async function handleLogin(e) {
    e.preventDefault();

    const res = await fetch("http://localhost:8000/auth/login", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(form)
    });

    const data = await res.json();

    if (res.ok) {
      alert("Autentificare reușită!");
      login(data); // Setează utilizatorul în context

      // Forțează reîncărcarea paginii pentru a actualiza contextul
      if (data.rol === "admin") window.location.href = "/admin-dashboard";
      else window.location.href = "/";

    } else {
      alert(data.detail || "Credențiale invalide");
    }
  }

  return (
    <div className="auth-container">
      <div className="auth-card">
        <h2>Autentificare</h2>

        <form onSubmit={handleLogin}>

          <div className="field-group">
            <input
              className="auth-input"
              name="email"
              type="email"
              placeholder="Email"
              value={form.email}
              onChange={updateField}
              required
            />
          </div>

          <div className="field-group">
            <div className="password-wrapper">
              <input
                className="auth-input"
                name="parola"
                type={showPassword ? "text" : "password"}
                placeholder="Parolă"
                value={form.parola}
                onChange={updateField}
                required
              />
              <span
                className="toggle-pass"
                onClick={() => setShowPassword(!showPassword)}
              >
                {showPassword ? "🙈" : "👁️"}
              </span>
            </div>
          </div>

          <div className="field-group">
            <select className="auth-select" name="rol" value={form.rol} onChange={updateField}>
              <option value="cursant">Cursant</option>
              <option value="antrenor">Antrenor personal</option>
              <option value="admin">Administrator</option>
            </select>
          </div>

          <button className="auth-btn">Login</button>
        </form>
      </div>
    </div>
  );
}
