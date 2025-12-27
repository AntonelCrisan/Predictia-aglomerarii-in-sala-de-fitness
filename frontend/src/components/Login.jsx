import { useState, useContext } from "react";
import { useNavigate } from "react-router-dom";
import { AuthContext } from "./AuthContext";
import { Eye, EyeOff, Mail, Lock, User } from "lucide-react";
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
  const [errors, setErrors] = useState({});

  function updateField(e) {
    setForm({ ...form, [e.target.name]: e.target.value });
    // Clear error when user starts typing
    if (errors[e.target.name]) {
      setErrors({ ...errors, [e.target.name]: "" });
    }
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
      login(data);
      if (data.user.rol === "administrator") window.location.href = "/admin-dashboard";
      else window.location.href = "/";
    } else {
      setErrors({ general: data.detail || "Credențiale invalide" });
    }
  }

  return (
    <div className="auth-container">
      <div className="auth-card">
        <h2>Autentificare</h2>

        <form onSubmit={handleLogin}>
          
          {errors.general && (
            <div className="error-message">{errors.general}</div>
          )}

          <div className="auth-group">
            <label>Email</label>
            <div className="input-with-icon">
              <Mail className="input-icon" size={20} />
              <input
                className="auth-input"
                name="email"
                type="email"
                placeholder="adresa@email.com"
                value={form.email}
                onChange={updateField}
                required
              />
            </div>
          </div>

          <div className="auth-group">
            <label>Parolă</label>
            <div className="input-with-icon">
              <Lock className="input-icon" size={20} />
              <input
                className="auth-input with-toggle"
                name="parola"
                type={showPassword ? "text" : "password"}
                placeholder="Introduceți parola"
                value={form.parola}
                onChange={updateField}
                required
              />
              <button
                type="button"
                className="toggle-pass-btn"
                onClick={() => setShowPassword(!showPassword)}
                aria-label={showPassword ? "Ascunde parola" : "Arată parola"}
              >
                {showPassword ? <EyeOff size={20} /> : <Eye size={20} />}
              </button>
            </div>
          </div>

          <div className="auth-group">
            <label>Rol</label>
            <div className="input-with-icon">
              <User className="input-icon" size={20} />
              <select 
                className="auth-select" 
                name="rol" 
                value={form.rol} 
                onChange={updateField}
              >
                <option value="cursant">Cursant</option>
                <option value="antrenor">Antrenor personal</option>
                <option value="administrator">Administrator</option>
              </select>
            </div>
          </div>

          <button className="auth-btn" type="submit">
            Autentificare
          </button>

          <div className="auth-footer">
            <p>Nu ai cont? <span className="link" onClick={() => nav("/register")}>Înregistrează-te</span></p>
          </div>
        </form>
      </div>
    </div>
  );
}