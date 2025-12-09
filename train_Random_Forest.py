import pymysql
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error
import joblib
import random

# -----------------------------------------
# 1. CONECTARE LA BAZA DE DATE
# -----------------------------------------
DB_CONFIG = {
    "host": "localhost",
    "user": "root",       # modifică dacă ai alt user
    "password": "",       # pune parola ta
    "database": "aglomerare_sali",
    "charset": "utf8mb4"
}

connection = pymysql.connect(**DB_CONFIG)
print("✔ Conectat la MySQL.")

# -----------------------------------------
# 2. CITIRE DATE DIN MySQL
#    (folosim date_colectate ca sursă)
# -----------------------------------------
query = """
SELECT
    dc.numar_oameni,
    dc.zi,
    dc.luna,
    dc.an,
    dc.e_weekend,
    dc.e_vacanta,
    dc.temperatura,
    dc.e_inceput_de_semestru,
    dc.e_semestru_in_derulare,
    HOUR(dc.ora) AS ora,
    dc.id_sala
FROM date_colectate dc;
"""

df = pd.read_sql(query, connection)
connection.close()

print(f" Am încărcat {len(df)} înregistrări din date_colectate.")

# -----------------------------------------
# 3. GENERARE ȚINTE PENTRU APARATE (SINTETIC)
#    - simulăm câți oameni sunt la fiecare zonă
# -----------------------------------------

def add_equipment_targets(df: pd.DataFrame) -> pd.DataFrame:
    """
    Pentru fiecare rând (moment de timp) generăm:
      - ocupare_picioare
      - ocupare_spate
      - ocupare_piept
      - ocupare_umeri
      - ocupare_brate
      - ocupare_abdomen
      - ocupare_full_body
    pe baza numărului de oameni din sală.
    """
    # proporții de bază din totalul de oameni
    ratios = {
        "ocupare_picioare": 0.25,
        "ocupare_spate": 0.15,
        "ocupare_piept": 0.20,
        "ocupare_umeri": 0.10,
        "ocupare_brate": 0.15,
        "ocupare_abdomen": 0.10,
        "ocupare_full_body": 0.05,
    }

    # presupunem un număr maxim rezonabil de oameni pe zonă
    max_by_zone = {
        "ocupare_picioare": 15,
        "ocupare_spate": 12,
        "ocupare_piept": 15,
        "ocupare_umeri": 10,
        "ocupare_brate": 12,
        "ocupare_abdomen": 10,
        "ocupare_full_body": 8,
    }

    for zone, ratio in ratios.items():
        values = []
        for n in df["numar_oameni"]:
            # bază: proporție din numărul total
            base = n * ratio
            # zgomot mic pentru a nu fi liniar perfect
            noise = random.gauss(0, max(1.0, base * 0.1))
            v = int(round(base + noise))
            v = max(0, v)
            v = min(v, max_by_zone[zone])
            values.append(v)
        df[zone] = values

    return df


df = add_equipment_targets(df)
print("✔ Am generat țintele sintetice pentru aparate.")

# -----------------------------------------
# 4. DEFINIRE FEATURES (X) ȘI ȚINTE (y)
# -----------------------------------------

feature_cols = [
    "zi",
    "luna",
    "an",
    "ora",
    "e_weekend",
    "e_vacanta",
    "temperatura",
    "e_inceput_de_semestru",
    "e_semestru_in_derulare",
    "id_sala"
]

target_cols = [
    "numar_oameni",
    "ocupare_picioare",
    "ocupare_spate",
    "ocupare_piept",
    "ocupare_umeri",
    "ocupare_brate",
    "ocupare_abdomen",
    "ocupare_full_body",
]

X = df[feature_cols]
y = df[target_cols]

print("✔ Structura X:", X.shape, "Structura y:", y.shape)

# -----------------------------------------
# 5. ÎMPĂRȚIRE TRAIN / TEST
# -----------------------------------------
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# -----------------------------------------
# 6. MODEL RANDOM FOREST MULTI-OUTPUT
# -----------------------------------------
rf_model = RandomForestRegressor(
    n_estimators=200,
    random_state=42,
    n_jobs=-1
)

print(" Antrenez modelul Random Forest...")
rf_model.fit(X_train, y_train)
print("✔ Antrenare finalizată.")

# -----------------------------------------
# 7. EVALUARE MODEL
# -----------------------------------------
rf_score = rf_model.score(X_test, y_test)
print(f"R² global (medie pe toate țintele): {rf_score:.4f}")

preds = rf_model.predict(X_test)

# convertim în DataFrame pentru metrici per-coloană
y_test_df = pd.DataFrame(y_test, columns=target_cols)
preds_df = pd.DataFrame(preds, columns=target_cols)

print("\n Metrici per țintă:")
for col in target_cols:
    mae = mean_absolute_error(y_test_df[col], preds_df[col])
    mse = mean_squared_error(y_test_df[col], preds_df[col])
    print(f" - {col}: MAE={mae:.3f}, MSE={mse:.3f}")

# -----------------------------------------
# 8. SALVARE MODEL
# -----------------------------------------
model_path = "rf_multioutput_mysql.pkl"
joblib.dump(
    {
        "model": rf_model,
        "feature_cols": feature_cols,
        "target_cols": target_cols
    },
    model_path
)
print(f"\n Modelul a fost salvat în {model_path}")
