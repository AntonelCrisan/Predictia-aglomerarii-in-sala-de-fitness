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

  const formatDate = (d) => {
    if (!d) return "";
    return d.toISOString().split("T")[0];
  };

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
        id_sala: Number(selectedGym)
      }),
    });

    const data = await response.json();
    console.log("RESPONSE FROM BACKEND:", data);

    const res = data?.predictie || {};

    // -----------------------------
    // 1. EXTRAGERE NUMĂR OAMENI
    // -----------------------------
    const rawPeople =
      typeof res.number_people !== "undefined"
        ? res.number_people
        : res.numar_oameni;

    let peopleParsed = Number(rawPeople);

    if (!rawPeople || isNaN(peopleParsed)) {
      console.error("Nu am găsit field-ul pentru numărul de oameni:", res);
      setPredictionPeople("Eroare");
    } else {
      setPredictionPeople(Math.round(peopleParsed));
    }

    // -----------------------------
    // 2. APARATE — extragem DOAR restul cheilor
    // -----------------------------
    const machines = {};

    Object.entries(res).forEach(([name, value]) => {
      if (name === "number_people" || name === "numar_oameni") return;

      let v = Number(value);
      if (isNaN(v)) v = 0;

      // normalizare la 0–100%
      let pct = v <= 1 ? v * 100 : v;
      pct = Math.max(0, Math.min(100, pct));

      machines[name] = pct / 100; // salvăm intern ca 0–1
    });

    setPredictionMachines(machines);
    setLoading(false);
  };

  return (
    <div className="predictor-container">
      <div className="predictor-card">

        <h1>Predicție Aglomerare Sala de Fitness</h1>
        <p className="subtitle">
          Alege data și ora pentru a afla câte persoane vor fi în sală.
        </p>

        {/* DATA */}
        <div className="input-group">
          <label>Data</label>
          <DatePicker
            selected={date}
            onChange={(d) => setDate(d)}
            className="modern-input"
            placeholderText="Selectează data"
            calendarClassName="glass-calendar"
          />
        </div>

        {/* ORA */}
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

        {/* BUTTON */}
        <button className="predict-btn" onClick={getPrediction}>
          {loading ? "Se calculează…" : "Predict"}
        </button>

        {/* REZULTAT OAMENI */}
        {predictionPeople !== null && (
          <div className="result-box">
            <h3>{isNaN(predictionPeople) ? "Eroare" : predictionPeople + " persoane"}</h3>
            <p>estimare pentru perioada selectată</p>
          </div>
        )}

        {/* APARATE */}
        {Object.keys(predictionMachines).length > 0 && (
          <div className="machines-box">
            <h2>Disponibilitate aparate</h2>

            <div className="machines-grid">
              {Object.entries(predictionMachines).map(([name, value]) => (
                <div className="machine-card" key={name}>
                  <div className="machine-name">{name.replace(/_/g, " ")}</div>

                  <div className="machine-bar">
                    <div
                      className="machine-bar-fill"
                      style={{ width: `${Math.round(value * 100)}%` }}
                    ></div>
                  </div>

                  <div className="machine-percent">
                    {Math.round(value * 100)}%
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

      </div>
    </div>
  );
}

export default PredictorCard;
