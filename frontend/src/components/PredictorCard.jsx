import { useLocation } from "react-router-dom";
import { useState } from "react";
import DatePicker from "react-datepicker";
import TimePicker from "react-time-picker";

import "react-datepicker/dist/react-datepicker.css";
import "react-time-picker/dist/TimePicker.css";
import "./Predictor.css";

function PredictorCard() {
  const location = useLocation();
  const params = new URLSearchParams(location.search);
  const selectedGym = params.get("gym");

  const [date, setDate] = useState(null);
  const [hour, setHour] = useState(null);
  const [predictionPeople, setPredictionPeople] = useState(null);
  const [predictionMachines, setPredictionMachines] = useState({});
  const [loading, setLoading] = useState(false);
  const [selectedMachine, setSelectedMachine] = useState(null);

  // Definim exercitiile pentru fiecare grupa musculara
  const exercises = {
    "ocupare_picioare": ["Leg Press", "Hack Squat", "Leg Extension", "Leg Curl", "Hip Thrust", "Abductor Machine", "Adductor Machine"],
    "ocupare_spate": ["Lat Pulldown", "Seated Row", "Back Extension"],
    "ocupare_piept": ["Bench Press", "Dumbbell Press", "Machine Chest Press", "Incline Bench", "Cable Flyes"],
    "ocupare_umeri": ["Shoulder Press", "Lateral Raises"],
    "ocupare_brate": ["Biceps Curl", "Triceps Pushdown"],
    "ocupare_abdomen": ["Ab Crunch", "Rotary Torso"],
    "ocupare_full_body": ["Cable Crossover"]
  };

  // Functie pentru distributia persoanelor pe exercitii
  const distributePeople = (totalPeople, exerciseList) => {
    if (totalPeople <= 0) return {};
    const distribution = {};
    let remaining = totalPeople;

    // Distribuim random, dar asiguram ca fiecare exercitiu are cel putin 0
    for (let i = 0; i < exerciseList.length - 1; i++) {
      const maxForThis = Math.min(remaining, Math.max(1, Math.floor(Math.random() * remaining)));
      distribution[exerciseList[i]] = maxForThis;
      remaining -= maxForThis;
    }
    // Ultimul ia restul
    distribution[exerciseList[exerciseList.length - 1]] = remaining;

    return distribution;
  };

  // POPUP
  const [popupData, setPopupData] = useState(null);
  const [selectedCategory, setSelectedCategory] = useState(null);

  const formatDate = (d) => (d ? d.toISOString().split("T")[0] : "");

  // Culoare pe baza procentului
  const getColor = (pct) => {
    if (pct < 25) return "#76c893"; // verde
    if (pct < 55) return "#f9c74f"; // galben
    return "#e63946"; // roșu
  };

  // ====== Fetch Predict ======
  const getPrediction = async () => {
    if (!date || !hour || !selectedGym) {
      alert("Selectează data, ora și sala!");
      return;
    }

    setLoading(true);
    setPredictionPeople(null);
    setPredictionMachines({});

    const response = await fetch("http://localhost:8000/predict", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        data: formatDate(date),
        ora: hour,
        id_sala: Number(selectedGym),
      }),
    });

    const data = await response.json();
    const res = data?.predictie || {};

    // === NUMĂR OAMENI ===
    const rawPeople =
      res.number_people !== undefined ? res.number_people : res.numar_oameni;

    const parsedPeople = Number(rawPeople);
    setPredictionPeople(isNaN(parsedPeople) ? "Eroare" : Math.round(parsedPeople));

    // === APARATE ===
    const machines = {};
    Object.entries(res).forEach(([name, v]) => {
      if (name === "number_people" || name === "numar_oameni") return;

      let pct = Number(v);
      if (pct <= 1) pct = pct * 100;
      pct = Math.max(0, Math.min(100, pct));

      machines[name] = {
        pct,
        color: getColor(pct),
      };
    });

    setPredictionMachines(machines);
    setLoading(false);
  };

  // ====== OPEN POPUP DETALII APARATE ======
 const openMachineDetails = async (category, pct) => {
  const cat = category.replace("ocupare_", "");

  const response = await fetch("http://localhost:8000/detalii_aparate", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      categorie: cat,
      procent: Math.round(pct),
      numar_oameni: predictionPeople,
      id_sala: Number(selectedGym),
    }),
  });

  const data = await response.json();
  setPopupData(data);
};

  return (
    <div
      className={`predictor-layout ${
        predictionPeople !== null ? "with-results" : ""
      }`}
    >
      {/* LEFT SIDE - FORM */}
      <div className="predictor-left">
        <div className="predictor-card">
          <h1>Predicție Aglomerare Sala de Fitness</h1>
          <p className="subtitle">
            Alege data și ora pentru a afla câte persoane vor fi în sală.
          </p>

          {/* Data */}
          <div className="input-group">
            <label>Data</label>
            <DatePicker
              selected={date}
              onChange={setDate}
              minDate={new Date()}
              className="modern-input"
              placeholderText="Selectează data"
              calendarClassName="glass-calendar"
            />
          </div>

          {/* Ora */}
          <div className="input-group">
            <label>Ora</label>
            <TimePicker
              onChange={setHour}
              value={hour}
              className="modern-time"
              disableClock={true}
              clearIcon={null}
              format="HH:mm"
              hourPlaceholder="--"
              minutePlaceholder="--"
            />
          </div>

          <button className="predict-btn" onClick={getPrediction}>
            {loading ? "Se calculează…" : "Predict"}
          </button>
        </div>
      </div>

      {/* RIGHT SIDE - DASHBOARD */}
      {predictionPeople !== null && (
        <div className="predictor-right">
          <div className="result-box">
            <h3>
              {isNaN(predictionPeople)
                ? "Eroare"
                : predictionPeople + " persoane"}
            </h3>
            <p>estimare pentru perioada selectată</p>
          </div>

          {/* Aparatele */}
          <div className="heatmap-container">
            <h3>Distribuție utilizare aparate</h3>

            <div className="heatmap-grid">
              {Object.entries(predictionMachines).map(([name, obj]) => (
                <div
                  className="heatmap-item"
                  key={name}
                  onClick={() => openMachineDetails(name, obj.pct)}
                  style={{ cursor: "pointer" }}
                >
                  <div
                    className="heatmap-color"
                    style={{ backgroundColor: obj.color }}
                  ></div>

                  <div className="heatmap-label">
                    {name.replace(/_/g, " ")}
                  </div>

                  <div className="heatmap-value">
                    {Math.round(obj.pct)}%
                  </div>

                  <button
                    className="detail-btn"
                    onClick={() => {
                      const exerciseList = exercises[name] || [];
                      const totalPeople = Math.round((obj.pct / 100) * predictionPeople);
                      const distribution = Object.entries(distributePeople(totalPeople, exerciseList));
                      setSelectedMachine({ name, pct: obj.pct, people: predictionPeople, distribution });
                    }}
                  >
                    Detalii
                  </button>

                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Modal pentru detalii echipament */}
      {selectedMachine && (
        <div className="modal-overlay" onClick={() => setSelectedMachine(null)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <h4>{selectedMachine.name.replace(/_/g, " ").toUpperCase()}</h4>
            <p>Ocupare totală: {Math.round(selectedMachine.pct)}%</p>
            <p>Număr total de persoane: {Math.round((selectedMachine.pct / 100) * selectedMachine.people)}</p>
            <div className="exercise-breakdown">
              <h5>Distribuție pe exerciții:</h5>
              {selectedMachine.distribution.map(([exercise, count]) => (
                <p key={exercise}>{exercise}: {count} {count === 1 ? 'persoană' : 'persoane'}</p>
              ))}
            </div>
            <button onClick={() => setSelectedMachine(null)}>Închide</button>
          </div>
        </div>
      )}
    </div>
  );
}

export default PredictorCard;
