from fastapi import FastAPI
from pydantic import BaseModel
import joblib
import numpy as np
import pymysql
from datetime import datetime
from fastapi.middleware.cors import CORSMiddleware
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
# ----------------------------------------------------
# 1. ÎNCĂRCARE MODEL SALVAT
# ----------------------------------------------------
bundle = joblib.load("rf_multioutput_mysql.pkl")
model = bundle["model"]
feature_cols = bundle["feature_cols"]
target_cols = bundle["target_cols"]

print("✔ Model încărcat cu succes.")

# ----------------------------------------------------
# 2. CONECTARE LA BAZA DE DATE (opțional)
# ----------------------------------------------------
DB = {
    "host": "localhost",
    "user": "root",
    "password": "root",
    "database": "aglomerare_sali",
    "charset": "utf8mb4"
}

def get_connection():
    return pymysql.connect(**DB)

# ----------------------------------------------------
# 3. DEFINIRE API + SCHEMA REQUEST
# ----------------------------------------------------
class PredictRequest(BaseModel):
    data: str       # ex: "2025-12-18"
    ora: str        # ex: "17:30"
    id_sala: int    # din dropdown-ul tău

# ----------------------------------------------------
# 4. FUNCTIE PENTRU PREPROCESARE FEATURES
# ----------------------------------------------------
def extract_features(data_str, ora_str, id_sala):
    """
    Primește data & ora selectate în frontend
    => extrage toate feature-urile necesare modelului
    """

    dt = datetime.strptime(f"{data_str} {ora_str}", "%Y-%m-%d %H:%M")

    zi = dt.day
    luna = dt.month
    an = dt.year
    ora = dt.hour

    # Derivate
    e_weekend = 1 if dt.weekday() >= 5 else 0
    e_vacanta = 0  # poți adăuga logici reale
    temperatura = 20  # placeholder — dacă vrei putem integra API METEO
    e_inceput = 0
    e_derulare = 1

    return np.array([[zi, luna, an, ora, 
                      e_weekend, e_vacanta, temperatura,
                      e_inceput, e_derulare, id_sala]])

# ----------------------------------------------------
# 5. ENDPOINT DE PREZICERE
# ----------------------------------------------------
@app.post("/predict")
async def predict(req: PredictRequest):

    # extragere features
    X = extract_features(req.data, req.ora, req.id_sala)

    # predicția modelului
    preds = model.predict(X)[0]

    # prima coloană = număr oameni
    number_people = max(0, float(preds[0]))

    # calculăm procentajele LOGIC, nu din ML
    max_people = 30  # poți ajusta în funcție de sală
    base_pct = (number_people / max_people) * 100

    import random

    usage = {
        "ocupare_picioare": base_pct * random.uniform(0.8, 1.2),
        "ocupare_spate": base_pct * random.uniform(0.75, 1.1),
        "ocupare_piept": base_pct * random.uniform(0.85, 1.15),
        "ocupare_umeri": base_pct * random.uniform(0.7, 1.05),
        "ocupare_brate": base_pct * random.uniform(0.7, 1.1),
        "ocupare_abdomen": base_pct * random.uniform(0.6, 1.0),
        "ocupare_full_body": base_pct * random.uniform(1.0, 1.3),
    }

    # limitare valori între 0–100%
    usage = {k: min(100, max(0, round(v))) for k, v in usage.items()}

    return {
        "status": "success",
        "sala": req.id_sala,
        "input": {
            "data": req.data,
            "ora": req.ora
        },
        "predictie": {
            "numar_oameni": round(number_people),
            **usage
        }
    }


#Endpoint pentru afisarea salilor din baza de date
@app.get("/sali")
def get_sali():
    conn = get_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    
    cursor.execute("SELECT id, nume, localitate, judet, adresa FROM sali")
    results = cursor.fetchall()

    cursor.close()
    conn.close()
    return results
