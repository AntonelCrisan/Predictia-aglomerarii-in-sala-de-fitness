import pymysql
import random
from datetime import datetime, timedelta

# ============================
# CONFIGURARE BAZA DE DATE
# ============================
DB = {
    "host": "localhost",
    "user": "root",
    "password": "root",
    "database": "aglomerare_sali",
    "charset": "utf8mb4"
}

def get_connection():
    return pymysql.connect(**DB)


# ============================
# FUNCTII CONTEXT CALENDARISTIC
# ============================

def is_vacanta(dt):
    """
    Simulare vacante:
    - iulie, august
    - februarie (vacanta intersemestriala)
    """
    return dt.month in [2, 7, 8]

def temperatura_simulata(dt):
    """
    Temperatura REALISTA in functie de luna.
    Evitam aberatii (30°C iarna).
    """
    if dt.month in [12, 1, 2]:
        return round(random.uniform(-5, 8), 1)
    elif dt.month in [3, 4, 5]:
        return round(random.uniform(8, 18), 1)
    elif dt.month in [6, 7, 8]:
        return round(random.uniform(22, 35), 1)
    else:
        return round(random.uniform(10, 22), 1)


# ============================
# NUMAR OAMENI - LOGICA REALISTA
# ============================

def numar_oameni_simulat(dt, temperatura):
    """
    Numarul de oameni depinde de:
    - ora
    - weekend
    - vacanta
    - temperatura
    """
    ora = dt.hour
    weekend = dt.weekday() >= 5
    vacanta = is_vacanta(dt)

    # baza pe interval orar
    if 17 <= ora <= 20:
        base = random.randint(22, 40)
    elif 10 <= ora < 17:
        base = random.randint(10, 22)
    elif 6 <= ora < 10:
        base = random.randint(5, 14)
    else:
        base = random.randint(0, 5)

    # ajustari context
    if weekend:
        base *= 0.75
    if vacanta:
        base *= 0.7
    if temperatura < 0:
        base *= 0.85
    if temperatura > 30:
        base *= 0.9

    return max(0, int(base))


# ============================
# DISTRIBUTIE APARATE
# ============================

def distributie_aparate(numar_oameni):
    """
    Distribuie oamenii pe grupe musculare
    in mod REALIST (nu toti peste tot).
    """
    if numar_oameni == 0:
        return {
            "picioare": 0,
            "spate": 0,
            "piept": 0,
            "umeri": 0,
            "brate": 0,
            "abdomen": 0,
            "full_body": 0
        }

    distributie = {
        "picioare": int(numar_oameni * random.uniform(0.18, 0.22)),
        "spate": int(numar_oameni * random.uniform(0.13, 0.17)),
        "piept": int(numar_oameni * random.uniform(0.16, 0.20)),
        "umeri": int(numar_oameni * random.uniform(0.10, 0.14)),
        "brate": int(numar_oameni * random.uniform(0.12, 0.16)),
        "abdomen": int(numar_oameni * random.uniform(0.08, 0.12)),
        "full_body": int(numar_oameni * random.uniform(0.06, 0.10)),
    }

    # Corectie: suma sa NU depaseasca numarul de oameni
    total = sum(distributie.values())
    if total > numar_oameni:
        factor = numar_oameni / total
        for k in distributie:
            distributie[k] = int(distributie[k] * factor)

    return distributie


# ============================
# INSERARE DATE
# ============================

def insert_date(conn, dt, id_sala):
    cursor = conn.cursor()

    temperatura = temperatura_simulata(dt)
    oameni = numar_oameni_simulat(dt, temperatura)
    aparate = distributie_aparate(oameni)

    cursor.execute("""
        INSERT INTO date_colectate
        (numar_oameni, zi, luna, an, e_weekend, e_vacanta,
         temperatura, e_inceput_de_semestru, e_semestru_in_derulare,
         ora, id_sala)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
    """, (
        oameni,
        dt.day,
        dt.month,
        dt.year,
        int(dt.weekday() >= 5),
        int(is_vacanta(dt)),
        temperatura,
        0,
        1,
        dt.strftime("%H:%M:%S"),
        id_sala
    ))

    # Aparatele (1 = folosit, 0 = liber)
    def aparat_activ(nr):
        return 1 if nr > 0 else 0

    cursor.execute("""
        INSERT INTO aparate_picioare
        (leg_press, hack_squat, leg_extension, leg_curl,
         hip_thrust, abductor_machine, adductor_machine)
        VALUES (%s,%s,%s,%s,%s,%s,%s)
    """, tuple([aparat_activ(aparate["picioare"])] * 7))

    cursor.execute("""
        INSERT INTO aparate_spate
        (lat_pulldown, seated_row_machine, back_extension)
        VALUES (%s,%s,%s)
    """, tuple([aparat_activ(aparate["spate"])] * 3))

    cursor.execute("""
        INSERT INTO aparate_piept
        (chest_press, pec_deck, incline_chest_press)
        VALUES (%s,%s,%s)
    """, tuple([aparat_activ(aparate["piept"])] * 3))

    cursor.execute("""
        INSERT INTO aparate_umeri
        (shoulder_press, lateral_raises)
        VALUES (%s,%s)
    """, tuple([aparat_activ(aparate["umeri"])] * 2))

    cursor.execute("""
        INSERT INTO aparate_brate
        (biceps_curl, triceps_push_down)
        VALUES (%s,%s)
    """, tuple([aparat_activ(aparate["brate"])] * 2))

    cursor.execute("""
        INSERT INTO aparate_abdomen
        (ab_crunch, rotary_torso)
        VALUES (%s,%s)
    """, tuple([aparat_activ(aparate["abdomen"])] * 2))

    cursor.execute("""
        INSERT INTO aparate_full_body
        (cable_crossover)
        VALUES (%s)
    """, (aparat_activ(aparate["full_body"]),))

    conn.commit()
    cursor.close()


# ============================
# SIMULARE MULTI-SALI
# ============================

def run_simulation():
    conn = get_connection()

    start = datetime(2024, 1, 1, 6, 0)
    end = datetime(2025, 12, 31, 22, 0)

    current = start

    while current <= end:
        for sala_id in range(1, 7):  # 6 sali
            insert_date(conn, current, sala_id)

        current += timedelta(minutes=15)  # rezolutie senzori

    conn.close()
    print("Simulare finalizata cu succes.")


# ============================
# MAIN
# ============================

if __name__ == "__main__":
    run_simulation()
