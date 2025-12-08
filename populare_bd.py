import pymysql
import pandas as pd
from dateutil import parser
import random

# -------------------------------------------------------
# 1. CONNECT TO DATABASE
# -------------------------------------------------------
connection = pymysql.connect(
    host="localhost",
    user="root",
    password="root",    # pune parola ta aici
    database="aglomerare_sali",
    autocommit=True
)

cursor = connection.cursor()


# -------------------------------------------------------
# 2. HELPER FUNCTION TO PARSE DATE
# -------------------------------------------------------
def parse_row(row):
    """Transformă o linie din dataset în format pentru date_colectate."""
    number_people = int(row[0])
    date_str = row[1].replace("'", "")

    dt = parser.parse(date_str)

    timestamp = int(row[2])
    day = dt.day
    month = dt.month
    year = dt.year
    hour = dt.hour

    day_of_week = int(row[3])
    is_weekend = int(row[4])
    is_holiday = int(row[5])
    temperature = float(row[6])
    is_start_sem = int(row[7])
    is_during_sem = int(row[8])

    return {
        "numar_oameni": number_people,
        "zi": day,
        "luna": month,
        "an": year,
        "e_weekend": is_weekend,
        "e_vacanta": is_holiday,
        "temperatura": temperature,
        "e_inceput_de_semestru": is_start_sem,
        "e_semestru_in_derulare": is_during_sem,
        "ora": f"{hour:02d}:00:00"
    }


# -------------------------------------------------------
# 3. INSERT FUNCTION
# -------------------------------------------------------
def insert_date(data, sala_id):
    sql = """
        INSERT INTO date_colectate
        (numar_oameni, zi, luna, an, e_weekend, e_vacanta, temperatura,
         e_inceput_de_semestru, e_semestru_in_derulare, ora, id_sala)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
    """
    cursor.execute(sql, (
        data["numar_oameni"],
        data["zi"],
        data["luna"],
        data["an"],
        data["e_weekend"],
        data["e_vacanta"],
        data["temperatura"],
        data["e_inceput_de_semestru"],
        data["e_semestru_in_derulare"],
        data["ora"],
        sala_id
    ))


# -------------------------------------------------------
# 4. LOAD DATASET
# -------------------------------------------------------
df = pd.read_csv("dataset.csv", header=None)

print("→ Am încărcat dataset-ul cu", len(df), "linii")


# -------------------------------------------------------
# 5. POPULARE SĂLI
# Sala 1 = date reale
# Sălile 2–6 = date artificiale cu zgomot ±5
# -------------------------------------------------------
for index, row in df.iterrows():
    # date reale -> sala 1
    d = parse_row(row)
    insert_date(d, sala_id=1)

    # date artificiale pentru sălile 2–6
    for sala in range(2, 7):
        new_d = d.copy()
        noise = random.randint(-5, 5)
        new_people = max(0, d["numar_oameni"] + noise)
        new_d["numar_oameni"] = new_people
        insert_date(new_d, sala)

print("✔ Gata! Am populat tabela date_colectate pentru toate sălile.")

connection.close()
