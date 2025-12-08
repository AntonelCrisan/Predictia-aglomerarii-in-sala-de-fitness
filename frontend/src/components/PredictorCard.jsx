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
    return d ? d.toISOString().split("T")[0] : "";
  };

  // Culoare pe baza procentului
  const getColor = (pct) => {
    if (pct < 25) return "#76c893"; // verde
    if (pct < 55) return "#f9c74f"; // galben
    return "#e63946"; // roșu
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
    const res = data?.predictie || {};

    // === OAMENI ===
    const rawPeople =
      res.number_people !== undefined
        ? res.number_people
        : res.numar_oameni;

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
        color: getColor(pct)
      };
    });

    setPredictionMachines(machines);
    setLoading(false);
  };

  return (
    <div
      className={`predictor-layout ${
        predictionPeople !== null ? "with-results" : ""
      }`}
    >
      {/* ====== LEFT SIDE – FORM ====== */}
      <div className="predictor-left">
        <div className="predictor-card">
          <h1>Predicție Aglomerare Sala de Fitness</h1>
          <p className="subtitle">
            Alege data și ora pentru a afla câte persoane vor fi în sală.
          </p>

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

      {/* ====== RIGHT SIDE – DASHBOARD ====== */}
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

          <div className="heatmap-container">
            <h3>Distribuție utilizare aparate</h3>

            <div className="heatmap-grid">
              {Object.entries(predictionMachines).map(([name, obj]) => (
                <div className="heatmap-item" key={name}>
                  
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

                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default PredictorCard;
