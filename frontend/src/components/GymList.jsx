import { useNavigate } from "react-router-dom";
import { useEffect, useState } from "react";
import "./GymList.css";

function GymsList() {
  const navigate = useNavigate();
  const [gyms, setGyms] = useState([]);

  useEffect(() => {
    fetch("http://localhost:8000/sali")
      .then((res) => res.json())
      .then((data) => setGyms(data))
      .catch((err) => console.error("Eroare la preluarea sălilor:", err));
  }, []);

  return (
    <div className="gyms-container">
      <h1 className="gyms-title">Săli de Fitness Disponibile</h1>
      <p className="gyms-subtitle">Selectează o sală pentru detalii.</p>

      <div className="gyms-grid">
        {gyms.map((gym) => (
          <div className="gym-card" key={gym.id}>
            <h2>{gym.nume}</h2>
            <p>{gym.localitate}, {gym.judet}</p>
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
