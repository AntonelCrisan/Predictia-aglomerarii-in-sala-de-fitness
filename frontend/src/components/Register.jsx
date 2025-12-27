import { useState, useContext } from "react";
import { useNavigate } from "react-router-dom";
import { AuthContext } from "./AuthContext";
import "./Auth.css";

// SVG Icons as components
const UserIcon = () => (
  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path>
    <circle cx="12" cy="7" r="4"></circle>
  </svg>
);

const MailIcon = () => (
  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"></path>
    <polyline points="22,6 12,13 2,6"></polyline>
  </svg>
);

const PhoneIcon = () => (
  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z"></path>
  </svg>
);

const IdCardIcon = () => (
  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <rect x="2" y="4" width="20" height="16" rx="2"></rect>
    <path d="M7 15h0M16 11h2M16 15h2M7 11a2 2 0 1 0 0-4 2 2 0 0 0 0 4z"></path>
  </svg>
);

const LockIcon = () => (
  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <rect x="3" y="11" width="18" height="11" rx="2" ry="2"></rect>
    <path d="M7 11V7a5 5 0 0 1 10 0v4"></path>
  </svg>
);

const BriefcaseIcon = () => (
  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <rect x="2" y="7" width="20" height="14" rx="2" ry="2"></rect>
    <path d="M16 21V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v16"></path>
  </svg>
);

const EyeIcon = () => (
  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"></path>
    <circle cx="12" cy="12" r="3"></circle>
  </svg>
);

const EyeOffIcon = () => (
  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"></path>
    <line x1="1" y1="1" x2="23" y2="23"></line>
  </svg>
);

export default function Register() {
  const nav = useNavigate();
  const { login } = useContext(AuthContext);

  const [form, setForm] = useState({
    nume: "",
    email: "",
    telefon: "",
    cnp: "",
    parola: "",
    rol: "cursant"
  });

  const [errors, setErrors] = useState({});
  const [showPassword, setShowPassword] = useState(false);

  function updateField(e) {
    const { name, value } = e.target;
    setForm(prev => ({ ...prev, [name]: value }));
    validateField(name, value);
  }

  function validateField(name, value) {
    let error = "";

    switch (name) {
      case "email":
        if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value))
          error = "Email invalid (ex: nume@example.com)";
        break;

      case "telefon":
        if (!/^(07\d{8}|0\d{9})$/.test(value))
          error = "Introduceți un număr de telefon valid";
        break;

      case "cnp":
        if (!/^\d{13}$/.test(value))
          error = "CNP-ul trebuie să conțină 13 cifre";
        break;

      case "parola":
        if (!/^(?=.*[0-9])(?=.*[!@#$%^&*]).{6,}$/.test(value))
          error = "Parola trebuie să aibă min. 6 caractere, 1 cifră și 1 simbol";
        break;

      default:
        break;
    }

    setErrors(prev => ({ ...prev, [name]: error }));
  }

  async function handleSubmit(e) {
    e.preventDefault();

    let valid = true;
    const newErrors = {};

    Object.keys(form).forEach(key => {
      validateField(key, form[key]);
      if (errors[key]) {
        valid = false;
        newErrors[key] = errors[key];
      }
    });

    if (!valid) {
      return;
    }

    const res = await fetch("http://localhost:8000/auth/register", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(form)
    });

    const data = await res.json();

    if (res.ok) {
      login(data.data);
      window.location.href = "/";
    } else {
      setErrors({ general: data.detail || "Eroare la înregistrare" });
    }
  }

  return (
    <div className="auth-container">
      <div className="auth-card">
        <h2>Înregistrare</h2>

        <form onSubmit={handleSubmit}>

          {errors.general && (
            <div className="error-message">{errors.general}</div>
          )}

          <div className="auth-group">
            <label>Nume complet</label>
            <div className="input-with-icon">
              <span className="input-icon">
                <UserIcon />
              </span>
              <input
                className="auth-input"
                name="nume"
                placeholder="Prenume Nume"
                value={form.nume}
                onChange={updateField}
                required
              />
            </div>
            {errors.nume && <p className="error">{errors.nume}</p>}
          </div>

          <div className="auth-group">
            <label>Email</label>
            <div className="input-with-icon">
              <span className="input-icon">
                <MailIcon />
              </span>
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
            {errors.email && <p className="error">{errors.email}</p>}
          </div>

          <div className="auth-group">
            <label>Telefon</label>
            <div className="input-with-icon">
              <span className="input-icon">
                <PhoneIcon />
              </span>
              <input
                className="auth-input"
                name="telefon"
                placeholder="07xxxxxxxx"
                value={form.telefon}
                onChange={updateField}
                required
              />
            </div>
            {errors.telefon && <p className="error">{errors.telefon}</p>}
          </div>

          <div className="auth-group">
            <label>CNP</label>
            <div className="input-with-icon">
              <span className="input-icon">
                <IdCardIcon />
              </span>
              <input
                className="auth-input"
                name="cnp"
                placeholder="13 cifre"
                value={form.cnp}
                onChange={updateField}
                required
              />
            </div>
            {errors.cnp && <p className="error">{errors.cnp}</p>}
          </div>

          <div className="auth-group">
            <label>Parolă</label>
            <div className="input-with-icon">
              <span className="input-icon">
                <LockIcon />
              </span>
              <input
                className="auth-input with-toggle"
                name="parola"
                type={showPassword ? "text" : "password"}
                placeholder="Min. 6 caractere, 1 cifră, 1 simbol"
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
                {showPassword ? <EyeOffIcon /> : <EyeIcon />}
              </button>
            </div>
            {errors.parola && <p className="error">{errors.parola}</p>}
          </div>

          <div className="auth-group">
            <label>Rol</label>
            <div className="input-with-icon">
              <span className="input-icon">
                <BriefcaseIcon />
              </span>
              <select 
                className="auth-select" 
                name="rol" 
                value={form.rol} 
                onChange={updateField}
              >
                <option value="cursant">Cursant</option>
                <option value="antrenor">Antrenor personal</option>
              </select>
            </div>
          </div>

          <button className="auth-btn" type="submit">
            Creează cont
          </button>

          <div className="auth-footer">
            <p>Ai deja cont? <span className="link" onClick={() => nav("/login")}>Autentifică-te</span></p>
          </div>
        </form>
      </div>
    </div>
  );
}