from fastapi import FastAPI, HTTPException
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

print("✔ Model ML încărcat cu succes.")

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
class DetaliiAparateRequest(BaseModel):
    categorie: str      # ex: "picioare"
    procent: float      # ex: 35 (%)
    id_sala: int        # sala selectată
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
        "id": user["id"],
        "nume": user["nume"],
        "email": user["email"],
        "rol": user["rol"]
    }

# ----------------------------------------------------
# ADMIN — LISTARE UTILIZATORI
# ----------------------------------------------------
@app.get("/admin/users")
def admin_list_users():
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
def admin_delete_user(user_id: int):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM utilizatori WHERE id=%s", (user_id,))
    conn.commit()

    cursor.close()
    conn.close()
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
    usage = {
        "ocupare_picioare": base_pct * random.uniform(0.8, 1.2),
        "ocupare_spate": base_pct * random.uniform(0.75, 1.1),
        "ocupare_piept": base_pct * random.uniform(0.85, 1.15),
        "ocupare_umeri": base_pct * random.uniform(0.7, 1.05),
        "ocupare_brate": base_pct * random.uniform(0.7, 1.1),
        "ocupare_abdomen": base_pct * random.uniform(0.6, 1.0),
        "ocupare_full_body": base_pct * random.uniform(1.0, 1.3),
    }

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


@app.post("/detalii_aparate")
def detalii_aparate(req: DetaliiAparateRequest):

    categorie = req.categorie.lower()  # ex: "picioare"
    procent = req.procent              # procent de ocupare
    id_sala = req.id_sala              # id sală

    # 1. Determinăm tabela în funcție de categorie
    table = f"aparate_{categorie}"     # ex: "aparate_picioare"

    conn = get_connection()
    cursor = conn.cursor()

    try:
        # 2. Preluăm LISTA APARATELOR VALIDE din tabelul categoriei
        cursor.execute(f"SELECT * FROM {table} LIMIT 1")
        row = cursor.fetchone()

        if not row:
            return {
                "aparate": [],
                "estimare": {}
            }

        # coloane: skip prima coloană (ID)
        col_names = [desc[0] for desc in cursor.description][1:]
        values = row[1:]

        aparate = [
            col for col, val in zip(col_names, values)
            if val == 1
        ]

        # 3. Generăm o estimare foarte simplă pentru fiecare aparat
        # exemplu: fix 1 persoană dacă procentul > 0
        estimare = {
            aparat: (1 if procent > 0 else 0)
            for aparat in aparate
        }

        return {
            "aparate": aparate,
            "estimare": estimare
        }

    except Exception as e:
        print("EROARE /detalii_aparate:", e)
        return {"aparate": [], "estimare": {}}

    finally:
        cursor.close()
        conn.close()