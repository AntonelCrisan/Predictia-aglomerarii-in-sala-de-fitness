from fastapi import FastAPI
from pydantic import BaseModel
import pandas as pd
import joblib
from fastapi.middleware.cors import CORSMiddleware
import datetime

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Încarcă modelul RandomForest salvat
rf_model = joblib.load("rf_model.pkl")

class PredictRequest(BaseModel):
    date: str  # format: "2025-08-01"
    hour: str  

@app.post("/predict")
def predict_people(req: PredictRequest):
    dt = datetime.datetime.strptime(req.date + " " + req.hour, "%Y-%m-%d %H:%M")

    # Construim EXACT cele 8 features folosite la antrenare, în ordinea corectă:
    day_of_week = dt.weekday()
    is_weekend = 1 if day_of_week >= 5 else 0
    is_holiday = 0  # nu ai date; rămâne 0
    temperature = 71.76  # poți integra API meteo ca să fie real
    is_start_of_semester = 0
    is_during_semester = 0
    month = dt.month
    hour = dt.hour

    features = pd.DataFrame([[
        day_of_week,
        is_weekend,
        is_holiday,
        temperature,
        is_start_of_semester,
        is_during_semester,
        month,
        hour
    ]])

    prediction = rf_model.predict(features)[0]

    return {"predicted_people": round(float(prediction))}
