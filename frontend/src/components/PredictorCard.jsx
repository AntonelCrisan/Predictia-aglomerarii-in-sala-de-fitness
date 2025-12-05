import { useState } from "react";
import DatePicker from "react-datepicker";
import TimePicker from "react-time-picker";
import "react-datepicker/dist/react-datepicker.css";
import "react-time-picker/dist/TimePicker.css";
import "react-clock/dist/Clock.css";
import "./Predictor.css";

function PredictorCard() {
  const [date, setDate] = useState(null);
  const [hour, setHour] = useState(null);
  const [prediction, setPrediction] = useState(null);
  const [loading, setLoading] = useState(false);

  const formatDate = (d) => {
    if (!d) return "";
    return d.toISOString().split("T")[0];
  };

  const getPrediction = async () => {
    if (!date || !hour) return;

    setLoading(true);
    setPrediction(null);

    const response = await fetch("http://localhost:8000/predict", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        date: formatDate(date),
        hour: hour
      })
    });

    const data = await response.json();
    setPrediction(data.predicted_people);
    setLoading(false);
  };

  return (
    <div className="predictor-container">
      <div className="predictor-card">
        <h2>Predicție Aglomerare Sala de Fitness</h2>
        <p className="subtitle">Alege data și ora în stil modern.</p>

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
