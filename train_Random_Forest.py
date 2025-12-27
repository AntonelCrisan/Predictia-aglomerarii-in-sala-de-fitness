import pymysql
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error
import joblib

# -----------------------------------------
# 1. CONECTARE LA BAZA DE DATE
# -----------------------------------------
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "root",
    "database": "aglomerare_sali",
    "charset": "utf8mb4"
}

connection = pymysql.connect(**DB_CONFIG)
print("Conectat la MySQL.")

# -----------------------------------------
# 2. QUERY CORECT (JOIN PE SCHEMA REALĂ)
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
    dc.id_sala,

    (
        ap.leg_press +
        ap.hack_squat +
        ap.leg_extension +
        ap.leg_curl +
        ap.hip_thrust +
        ap.abductor_machine +
        ap.adductor_machine
    ) AS ocupare_picioare,

    (
        asp.lat_pulldown +
        asp.seated_row_machine +
        asp.back_extension
    ) AS ocupare_spate,

    (
        api.chest_press +
        api.pec_deck +
        api.incline_chest_press
    ) AS ocupare_piept,

    (
        au.shoulder_press +
        au.lateral_raises
    ) AS ocupare_umeri,

    (
        ab.biceps_curl +
        ab.triceps_push_down
    ) AS ocupare_brate,

    (
        aa.ab_crunch +
        aa.rotary_torso
    ) AS ocupare_abdomen,

    af.cable_crossover AS ocupare_full_body

FROM date_colectate dc

JOIN sala_aparate sa
    ON sa.id_sala = dc.id_sala

JOIN aparate_picioare ap
    ON ap.id = sa.id_aparate_picioare

JOIN aparate_spate asp
    ON asp.id = sa.id_aparate_spate

JOIN aparate_piept api
    ON api.id = sa.id_aparate_piept

JOIN aparate_umeri au
    ON au.id = sa.id_aparate_umeri

JOIN aparate_brate ab
    ON ab.id = sa.id_aparate_brate

JOIN aparate_abdomen aa
    ON aa.id = sa.id_aparate_abdomen

JOIN aparate_full_body af
    ON af.id = sa.id_aparate_full_body;
"""

df = pd.read_sql(query, connection)
connection.close()

print(f"Am incarcat {len(df)} inregistrari din baza de date.")

# -----------------------------------------
# 3. VERIFICARE DATE
# -----------------------------------------
print("\nPreview date:")
print(df.head())

print("\nValori lipsa pe coloane:")
print(df.isnull().sum())

if df.isnull().any().any():
    raise ValueError("Exista valori NULL in date. Verifica datele din DB.")

# -----------------------------------------
# 4. DEFINIRE FEATURES (X) SI TINTE (y)
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
    "ocupare_full_body"
]

X = df[feature_cols]
y = df[target_cols]

print("\nStructura X:", X.shape)
print("Structura y:", y.shape)

# -----------------------------------------
# 5. SPLIT TRAIN / TEST
# -----------------------------------------
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42
)

# -----------------------------------------
# 6. RANDOM FOREST MULTI-OUTPUT
# -----------------------------------------
rf_model = RandomForestRegressor(
    n_estimators=200,
    random_state=42,
    n_jobs=-1
)

print("\nAntrenez modelul Random Forest...")
rf_model.fit(X_train, y_train)
print("Antrenare finalizata.")

# -----------------------------------------
# 7. EVALUARE MODEL
# -----------------------------------------
r2_score = rf_model.score(X_test, y_test)
print(f"\nR² global (medie pe toate tintele): {r2_score:.4f}")

preds = rf_model.predict(X_test)

y_test_df = pd.DataFrame(y_test, columns=target_cols)
preds_df = pd.DataFrame(preds, columns=target_cols)

print("\nMetrici per tinta:")
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

print(f"\nModelul a fost salvat in fisierul: {model_path}")
