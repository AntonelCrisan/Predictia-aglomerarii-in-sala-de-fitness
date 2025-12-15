from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
import joblib
import numpy as np
import pymysql
from datetime import datetime, timedelta
from fastapi.middleware.cors import CORSMiddleware
import bcrypt
import jwt

# ----------------------------------------------------
# JWT CONFIG
# ----------------------------------------------------
SECRET_KEY = "schimba_acest_secret_lung_urgent"
ALGORITHM = "HS256"

# ----------------------------------------------------
# INITIALIZARE APP
# ----------------------------------------------------
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ----------------------------------------------------
# ÎNCĂRCARE MODEL ML
# ----------------------------------------------------
bundle = joblib.load("rf_multioutput_mysql.pkl")
model = bundle["model"]

print("Model ML incarcat cu succes.")

# ----------------------------------------------------
# CONECTARE MYSQL
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
# MODELE SCHEMA
# ----------------------------------------------------
class PredictRequest(BaseModel):
    data: str
    ora: str
    id_sala: int

class RegisterRequest(BaseModel):
    nume: str
    email: str
    telefon: str
    cnp: str
    parola: str
    rol: str

class LoginRequest(BaseModel):
    email: str
    parola: str

class GymRequest(BaseModel):
    nume: str
    localitate: str
    judet: str
    adresa: str

# ----------------------------------------------------
# JWT - GENERARE TOKEN
# ----------------------------------------------------
def create_token(user_id, nume, rol):
    payload = {
        "id": user_id,
        "nume": nume,
        "rol": rol,
        "exp": datetime.utcnow() + timedelta(hours=8),
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

# ----------------------------------------------------
# JWT - VERIFICARE TOKEN
# ----------------------------------------------------
def get_current_user(request: Request):
    auth = request.headers.get("Authorization")
    if not auth:
        raise HTTPException(401, "Missing token")

    token = auth.replace("Bearer ", "")

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except:
        raise HTTPException(401, "Token invalid sau expirat")

# ----------------------------------------------------
# REGISTER
# ----------------------------------------------------
@app.post("/auth/register")
def register(req: RegisterRequest):
    conn = get_connection()
    cursor = conn.cursor()

    # Verificare email existent
    cursor.execute("SELECT id FROM utilizatori WHERE email=%s", (req.email,))
    if cursor.fetchone():
        raise HTTPException(400, "Email deja folosit!")

    # Hash parola
    hashed = bcrypt.hashpw(req.parola.encode(), bcrypt.gensalt()).decode()

    cursor.execute("""
        INSERT INTO utilizatori (nume, email, parola, telefon, cnp, rol)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (req.nume, req.email, hashed, req.telefon, req.cnp, req.rol))

    user_id = cursor.lastrowid

    # Get the created user data
    cursor.execute("SELECT id, nume, email, rol FROM utilizatori WHERE id=%s", (user_id,))
    user_data = cursor.fetchone()

    conn.commit()
    cursor.close()
    conn.close()

    user_dict = {
        "id": user_data[0],
        "nume": user_data[1],
        "email": user_data[2],
        "rol": user_data[3]
    }

    return {"status": "success", "message": "Cont creat cu succes!", "data": user_dict}

# ----------------------------------------------------
# LOGIN
# ----------------------------------------------------
@app.post("/auth/login")
def login(req: LoginRequest):
    conn = get_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)

    cursor.execute("SELECT * FROM utilizatori WHERE email=%s", (req.email,))
    user = cursor.fetchone()

    if not user:
        raise HTTPException(404, "Email invalid.")

    if not bcrypt.checkpw(req.parola.encode(), user["parola"].encode()):
        raise HTTPException(400, "Parola greșită.")

    token = create_token(user["id"], user["nume"], user["rol"])

    return {
        "user": {
            "id": user["id"],
            "nume": user["nume"],
            "email": user["email"],
            "rol": user["rol"]
        },
        "token": token
    }

# ----------------------------------------------------
# ADMIN — LISTARE UTILIZATORI
# ----------------------------------------------------
@app.get("/admin/users")
def admin_list_users(request: Request):
    user = get_current_user(request)
    if user["rol"] != "administrator":
        raise HTTPException(403, "Doar administratorii pot vizualiza utilizatorii!")

    conn = get_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)

    cursor.execute("SELECT id, nume, email, telefon, cnp, rol FROM utilizatori")
    users = cursor.fetchall()

    cursor.close()
    conn.close()
    return users

# ----------------------------------------------------
# ADMIN — ȘTERGERE UTILIZATOR
# ----------------------------------------------------
@app.delete("/admin/delete/{user_id}")
def admin_delete_user(user_id: int, request: Request):
    user = get_current_user(request)
    if user["rol"] != "administrator":
        raise HTTPException(403, "Doar administratorii pot șterge utilizatori!")

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM utilizatori WHERE id=%s", (user_id,))
    conn.commit()

    cursor.close()
    conn.close()
# ----------------------------------------------------
# ADMIN — MODIFICARE ROL UTILIZATOR
# ----------------------------------------------------
@app.put("/admin/users/{user_id}")
def admin_update_user_role(user_id: int, rol: str, request: Request):
    user = get_current_user(request)
    if user["rol"] != "administrator":
        raise HTTPException(403, "Doar administratorii pot modifica rolurile utilizatorilor!")

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("UPDATE utilizatori SET rol=%s WHERE id=%s", (rol, user_id))
    conn.commit()

    cursor.close()
    conn.close()
    return {"status": "success", "message": "Rol actualizat."}
    return {"status": "success", "message": "User șters."}

# ----------------------------------------------------
# FEATURE EXTRACTOR
# ----------------------------------------------------
def extract_features(data_str, ora_str, id_sala):
    dt = datetime.strptime(f"{data_str} {ora_str}", "%Y-%m-%d %H:%M")

    zi = dt.day
    luna = dt.month
    an = dt.year
    ora = dt.hour

    e_weekend = 1 if dt.weekday() >= 5 else 0

    return np.array([[zi, luna, an, ora,
                      e_weekend, 0, 20, 0, 1, id_sala]])

# ----------------------------------------------------
# PREZICERE
# ----------------------------------------------------
@app.post("/predict")
def predict(req: PredictRequest):
    X = extract_features(req.data, req.ora, req.id_sala)
    preds = model.predict(X)[0]

    number_people = max(0, float(preds[0]))
    max_people = 30
    base_pct = (number_people / max_people) * 100

    import random
    # Logica realista pentru ocuparea echipamentelor in functie de numarul de oameni
    # Folosim predictia numarului de oameni si aplicam distributie tipica pentru sali de fitness
    if number_people == 0:
        usage = {k: 0 for k in ["ocupare_picioare", "ocupare_spate", "ocupare_piept", "ocupare_umeri", "ocupare_brate", "ocupare_abdomen", "ocupare_full_body"]}
    else:
        # Distributie tipica pentru echipamente intr-o sala de fitness
        base_dist = {
            "ocupare_picioare": 0.20,  # populare pentru picioare
            "ocupare_spate": 0.15,     # spate
            "ocupare_piept": 0.18,     # piept
            "ocupare_umeri": 0.12,     # umeri
            "ocupare_brate": 0.15,     # brate
            "ocupare_abdomen": 0.10,   # abdomen
            "ocupare_full_body": 0.10, # full body
        }

        # Factor de aglomerare bazat pe ora
        ora_int = int(req.ora.split(':')[0])  # extragem ora din "HH:MM"
        hour_factor = 1.0
        if 17 <= ora_int <= 20:  # ore de varf
            hour_factor = 1.2
        elif ora_int < 10:  # dimineata devreme
            hour_factor = 0.7

        usage = {}
        for eq, base_ratio in base_dist.items():
            # Ocupare proportionala cu numarul de oameni, bazata pe distributie realista
            predicted_occupancy = base_pct * base_ratio * hour_factor
            usage[eq] = max(0, min(100, round(predicted_occupancy)))

    usage = {k: min(100, max(0, round(v))) for k, v in usage.items()}

    return {
        "status": "success",
        "sala": req.id_sala,
        "input": {"data": req.data, "ora": req.ora},
        "predictie": {"numar_oameni": round(number_people), **usage}
    }

# ----------------------------------------------------
# SALI
# ----------------------------------------------------
@app.get("/sali")
def get_sali():
    conn = get_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)

    cursor.execute("SELECT id, nume, localitate, judet, adresa FROM sali")
    results = cursor.fetchall()

    cursor.close()
    conn.close()
    return results

# ----------------------------------------------------
# ADMIN — LISTARE SALI
# ----------------------------------------------------
@app.get("/admin/sali")
def admin_list_sali(request: Request):
    user = get_current_user(request)
    if user["rol"] != "administrator":
        raise HTTPException(403, "Doar administratorii pot vizualiza sălile!")

    conn = get_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)

    cursor.execute("SELECT id, nume, localitate, judet, adresa FROM sali")
    results = cursor.fetchall()

    cursor.close()
    conn.close()
    return results

# ----------------------------------------------------
# ADMIN — ADAUGARE SALA
# ----------------------------------------------------
@app.post("/admin/sali")
def admin_add_sala(req: GymRequest, request: Request):
    user = get_current_user(request)
    if user["rol"] != "administrator":
        raise HTTPException(403, "Doar administratorii pot adăuga săli!")

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO sali (nume, localitate, judet, adresa)
        VALUES (%s, %s, %s, %s)
    """, (req.nume, req.localitate, req.judet, req.adresa))

    sala_id = cursor.lastrowid

    conn.commit()
    cursor.close()
    conn.close()

    return {"status": "success", "message": "Sală adăugată cu succes!", "id": sala_id}

# ----------------------------------------------------
# ADMIN — ȘTERGERE SALA
# ----------------------------------------------------
@app.delete("/admin/sali/{sala_id}")
def admin_delete_sala(sala_id: int, request: Request):
    user = get_current_user(request)
    if user["rol"] != "administrator":
        raise HTTPException(403, "Doar administratorii pot șterge săli!")

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM sali WHERE id=%s", (sala_id,))
    conn.commit()

    cursor.close()
    conn.close()
    return {"status": "success", "message": "Sală ștearsă."}
