import { useState } from "react";
import "./Predictor.css";

function PredictorCard() {
  const [date, setDate] = useState("");
  const [hour, setHour] = useState("");
  const [prediction, setPrediction] = useState(null);
  const [loading, setLoading] = useState(false);

  const getPrediction = async () => {
    if (!date || !hour) return;

    setLoading(true);
    setPrediction(null);

    const response = await fetch("http://localhost:8000/predict", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ date, hour })
    });

    const data = await response.json();
    setPrediction(data.predicted_people);
    setLoading(false);
  };

  return (
    <div className="predictor-container">
      <div className="predictor-card">
        <h2>Predicție Aglomerare Sala de Fitness</h2>
        <p className="subtitle">
          Alege ziua și ora pentru a vedea câte persoane vor fi în sală.
        </p>

        <div className="input-group">
          <label>Data</label>
          <input
            type="date"
            className="modern-input"
            value={date}
            onChange={(e) => setDate(e.target.value)}
          />
        </div>

        <div className="input-group">
          <label>Ora</label>
          <input
            type="time"
            className="modern-input"
            value={hour}
            onChange={(e) => setHour(e.target.value)}
          />
        </div>

        <button className="predict-btn" onClick={getPrediction}>
          {loading ? "Se calculează..." : "Predict"}
        </button>

        {prediction !== null && (
          <div className="result-box">
            <h3>{prediction} persoane</h3>
            <p>estimare pentru perioada selectată</p>
          </div>
        )}
      </div>
    </div>
  );
}

export default PredictorCard;
