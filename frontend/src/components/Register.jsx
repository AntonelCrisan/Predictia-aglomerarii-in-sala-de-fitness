import { useState, useContext } from "react";
import { useNavigate } from "react-router-dom";
import { AuthContext } from "./AuthContext";
import "./Auth.css";

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

  // ============================================
  // UPDATE + VALIDARE
  // ============================================
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

  // ============================================
  // SUBMIT FINAL
  // ============================================
  async function handleSubmit(e) {
    e.preventDefault();

    let valid = true;

    Object.keys(form).forEach(key => {
      validateField(key, form[key]);
      if (errors[key]) valid = false;
    });

    if (!valid) {
      const errorMessages = Object.values(errors).filter(err => err).join("\n");
      alert("Verifică câmpurile introduse:\n" + errorMessages);
      return;
    }

    const res = await fetch("http://localhost:8000/auth/register", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(form)
    });

    const data = await res.json();

    if (res.ok) {
      alert("Cont creat cu succes!");
      login(data.data); // Autentifică automat utilizatorul nou creat
      window.location.href = "/"; // Redirecționează către pagina principală cu reîncărcare
    } else {
      alert(data.detail || "Eroare la înregistrare");
    }
  }

  return (
    <div className="auth-container">
      <div className="auth-card">
        <h2>Înregistrare</h2>

        <form onSubmit={handleSubmit}>

          <div className="field-group">
            <input
              className="auth-input"
              name="nume"
              placeholder="Nume complet"
              value={form.nume}
              onChange={updateField}
              required
            />
            {errors.nume && <p className="error">{errors.nume}</p>}
          </div>

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
            {errors.email && <p className="error">{errors.email}</p>}
          </div>

          <div className="field-group">
            <input
              className="auth-input"
              name="telefon"
              placeholder="Număr de telefon"
              value={form.telefon}
              onChange={updateField}
              required
            />
            {errors.telefon && <p className="error">{errors.telefon}</p>}
          </div>

          <div className="field-group">
            <input
              className="auth-input"
              name="cnp"
              placeholder="CNP (13 cifre)"
              value={form.cnp}
              onChange={updateField}
              required
            />
            {errors.cnp && <p className="error">{errors.cnp}</p>}
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
            {errors.parola && <p className="error">{errors.parola}</p>}
          </div>

          <div className="field-group">
            <select className="auth-select" name="rol" value={form.rol} onChange={updateField}>
              <option value="cursant">Cursant</option>
              <option value="antrenor">Antrenor personal</option>
            </select>
          </div>

          <button className="auth-btn">Creează cont</button>
        </form>
      </div>
    </div>
  );
}
