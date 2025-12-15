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
# POPULARE DATE REALISTE PENTRU PREDICTII
# -------------------------------------------------------
print("Incep popularea bazei de date cu date realiste...")

import random
from datetime import datetime, timedelta

# Generare date pentru ultimele 6 luni
start_date = datetime.now() - timedelta(days=180)
end_date = datetime.now()

current_date = start_date
while current_date <= end_date:
    for ora in range(6, 22):  # de la 6 dimineata la 21 seara
        for sala_id in range(1, 7):  # 6 sali
            # Factorii care influenteaza ocuparea
            zi_saptamana = current_date.weekday()  # 0=luni, 6=duminica
            e_weekend = 1 if zi_saptamana >= 5 else 0
            e_vacanta = 0  # presupunem nu e vacanta

            # Baza ocupare in functie de ora
            if ora < 9:  # dimineata devreme
                base_ocupare = random.uniform(0.1, 0.3)
            elif ora < 12:  # dimineata
                base_ocupare = random.uniform(0.4, 0.7)
            elif ora < 15:  # pranz
                base_ocupare = random.uniform(0.2, 0.5)
            elif ora < 18:  # dupa-amiaza
                base_ocupare = random.uniform(0.5, 0.8)
            else:  # seara
                base_ocupare = random.uniform(0.6, 0.95)

            # Ajustare pentru weekend
            if e_weekend:
                base_ocupare *= random.uniform(0.8, 1.2)

            # Numar oameni proportional cu ocuparea
            numar_oameni = int(base_ocupare * 30 * random.uniform(0.8, 1.2))
            numar_oameni = max(0, min(50, numar_oameni))  # limita 0-50

            # Temperatura random
            temperatura = random.uniform(10, 25)

            # Ocupare echipamente - distribuita pe grupe musculare
            ocupare_picioare = min(100, base_ocupare * 100 * random.uniform(0.8, 1.2))
            ocupare_spate = min(100, base_ocupare * 100 * random.uniform(0.7, 1.1))
            ocupare_piept = min(100, base_ocupare * 100 * random.uniform(0.8, 1.15))
            ocupare_umeri = min(100, base_ocupare * 100 * random.uniform(0.6, 1.0))
            ocupare_brate = min(100, base_ocupare * 100 * random.uniform(0.6, 1.1))
            ocupare_abdomen = min(100, base_ocupare * 100 * random.uniform(0.5, 0.9))
            ocupare_full_body = min(100, base_ocupare * 100 * random.uniform(0.9, 1.3))

            # Inserare in date_colectate
            cursor.execute("""
                INSERT INTO date_colectate
                (numar_oameni, zi, luna, an, e_weekend, e_vacanta, temperatura,
                 e_inceput_de_semestru, e_semestru_in_derulare, ora, id_sala)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            """, (
                numar_oameni,
                current_date.day,
                current_date.month,
                current_date.year,
                e_weekend,
                e_vacanta,
                temperatura,
                0,  # e_inceput_de_semestru
                1,  # e_semestru_in_derulare
                f"{ora:02d}:00:00",
                sala_id
            ))

    current_date += timedelta(days=1)

print("Am populat date_colectate cu date realiste pentru predictii.")

# -------------------------------------------------------
# ADAUGARE SĂLI SAMPLE
# -------------------------------------------------------
sali_sample = [
    ("Sala Fitness Central", "Bucuresti", "Bucuresti", "Strada Victoriei 10"),
    ("Gym Power", "Cluj-Napoca", "Cluj", "Calea Victoriei 25"),
    ("FitZone", "Timisoara", "Timis", "Piața Unirii 5"),
    ("BodyBuilder Gym", "Iasi", "Iasi", "Strada Palat 12"),
    ("Energy Fitness", "Constanta", "Constanta", "Bulevardul Tomis 8"),
    ("ProGym", "Brasov", "Brasov", "Strada Republicii 15")
]

for sala in sali_sample:
    cursor.execute("""
        INSERT INTO sali (nume, localitate, judet, adresa)
        VALUES (%s, %s, %s, %s)
    """, sala)

print("Am adaugat sali sample.")

# -------------------------------------------------------
# ADAUGARE UTILIZATOR ADMIN
# -------------------------------------------------------
import bcrypt

admin_password = bcrypt.hashpw("admin123".encode(), bcrypt.gensalt()).decode()

cursor.execute("""
    INSERT INTO utilizatori (nume, email, parola, telefon, cnp, rol)
    VALUES (%s, %s, %s, %s, %s, %s)
""", ("Administrator", "admin@example.com", admin_password, "0712345678", "1234567890123", "administrator"))

print("Am adaugat utilizator admin: admin@example.com / admin123")

connection.close()
