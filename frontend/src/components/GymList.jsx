import { useNavigate } from "react-router-dom";
import { useEffect, useState, useContext } from "react";
import { AuthContext } from "./AuthContext";
import "./GymList.css";

function GymsList() {
  const navigate = useNavigate();
  const { user, logout } = useContext(AuthContext);
  const [gyms, setGyms] = useState([]);
  const [localUser, setLocalUser] = useState(null);

  useEffect(() => {
    fetch("http://localhost:8000/sali")
      .then((res) => res.json())
      .then((data) => setGyms(data))
      .catch((err) => console.error("Eroare la preluarea sălilor:", err));
  }, []);

  const handleLogout = () => {
    logout();
    navigate("/");
  };

  return (
    <div className="gyms-container">

      {/* 🔹 Bara de navigare */}
      <nav className="top-nav">
        {user ? (
          <div className="user-info">
            <span className="welcome-nav">
              Bun venit, {user.nume || 'Utilizator'}
            </span>
            <button
              onClick={handleLogout}
              className="nav-btn logout-btn"
            >
              Logout
            </button>
          </div>
        ) : (
          <>
            <button
              onClick={() => navigate("/login")}
              className="nav-btn"
            >
              Login
            </button>

            <button
              onClick={() => navigate("/register")}
              className="nav-btn"
            >
              Register
            </button>
          </>
        )}
      </nav>

      <h1 className="gyms-title">Săli de Fitness Disponibile</h1>
      <p className="gyms-subtitle">Selectează o sală pentru detalii.</p>

      {user && (
        <div className="welcome-message">
          <p>Bun venit, <strong>{user.nume || 'Utilizator'}</strong>! ({user.rol || 'N/A'})</p>
        </div>
      )}

      <div className="gyms-grid">
        {gyms.map((gym) => (
          <div className="gym-card" key={gym.id}>
            <h2>{gym.nume}</h2>
            <p>
              {gym.localitate}, {gym.judet}
            </p>
            <p>{gym.adresa}</p>

            <button
              className="gym-btn"
              onClick={() =>
                navigate(`/predict?gym=${encodeURIComponent(gym.id)}`)
              }
            >
              Vezi detalii
            </button>

          </div>
        ))}
      </div>
    </div>
  );
}

export default GymsList;
