import { useNavigate } from "react-router-dom";
import "./GymList.css";

function GymsList() {
  const navigate = useNavigate();

  const gyms = [
    { id: 1, name: "FitZone Arena", location: "Bd. Unirii 21, București" },
    { id: 2, name: "PowerGym Pro", location: "Str. Victoriei 9, Ploiești" },
    { id: 3, name: "IronTemple", location: "Str. Mureșului 12, Cluj-Napoca" },
    { id: 4, name: "Urban Fitness Club", location: "Str. Libertății 33, Iași" },
    { id: 5, name: "Titanium Gym", location: "Calea Brașovului 40, Brașov" },
    { id: 6, name: "EnergyFit Studio", location: "Str. Dunării 8, Constanța" },
    { id: 7, name: "Athletic Pro Center", location: "Str. Centrală 4, Timișoara" }
  ];

  return (
    <div className="gyms-container">
      <h1 className="gyms-title">Săli de Fitness Disponibile</h1>
      <p className="gyms-subtitle">Selectează o sală pentru detalii.</p>

      <div className="gyms-grid">
        {gyms.map((gym) => (
          <div className="gym-card" key={gym.id}>
            <h2>{gym.name}</h2>
            <p>{gym.location}</p>

            <button
              className="gym-btn"
              onClick={() =>
                navigate(`/predict?gym=${encodeURIComponent(gym.name)}`)
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
