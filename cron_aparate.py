import pymysql
import random
from datetime import datetime

DB = {
    "host": "localhost",
    "user": "root",
    "password": "root",
    "database": "aglomerare_sali",
    "charset": "utf8mb4",
    "autocommit": False
}

SALAS = range(1, 7)

def get_connection():
    return pymysql.connect(**DB)

def is_vacanta(dt: datetime) -> bool:
    return dt.month in (2, 7, 8)

def temperatura_simulata_int(dt: datetime) -> int:
    if dt.month in (12, 1, 2):
        return random.randint(-5, 8)
    elif dt.month in (3, 4, 5):
        return random.randint(8, 18)
    elif dt.month in (6, 7, 8):
        return random.randint(22, 35)
    else:
        return random.randint(10, 22)

def numar_oameni_simulat(dt: datetime, temperatura: int) -> int:
    ora = dt.hour
    weekend = dt.weekday() >= 5
    vacanta = is_vacanta(dt)

    if 17 <= ora <= 20:
        base = random.randint(22, 40)
    elif 10 <= ora < 17:
        base = random.randint(10, 22)
    elif 6 <= ora < 10:
        base = random.randint(5, 14)
    else:
        base = random.randint(0, 5)

    if weekend:
        base *= 0.75
    if vacanta:
        base *= 0.7
    if temperatura < 0:
        base *= 0.85
    if temperatura > 30:
        base *= 0.9

    return max(0, int(base))

def get_last_people(conn, id_sala: int) -> int | None:
    with conn.cursor() as cursor:
        cursor.execute("""
            SELECT numar_oameni
            FROM date_colectate
            WHERE id_sala = %s
            ORDER BY an DESC, luna DESC, zi DESC, ora DESC, id DESC
            LIMIT 1
        """, (id_sala,))
        row = cursor.fetchone()
        return int(row[0]) if row else None

def distributie_aparate(numar_oameni: int) -> dict:
    if numar_oameni <= 0:
        return {"picioare": 0, "spate": 0, "piept": 0, "umeri": 0, "brate": 0, "abdomen": 0, "full_body": 0}

    d = {
        "picioare": int(numar_oameni * random.uniform(0.18, 0.22)),
        "spate": int(numar_oameni * random.uniform(0.13, 0.17)),
        "piept": int(numar_oameni * random.uniform(0.16, 0.20)),
        "umeri": int(numar_oameni * random.uniform(0.10, 0.14)),
        "brate": int(numar_oameni * random.uniform(0.12, 0.16)),
        "abdomen": int(numar_oameni * random.uniform(0.08, 0.12)),
        "full_body": int(numar_oameni * random.uniform(0.06, 0.10)),
    }

    total = sum(d.values())
    if total > numar_oameni and total > 0:
        factor = numar_oameni / total
        for k in d:
            d[k] = int(d[k] * factor)

    return d

def aparat_activ(nr: int) -> int:
    # simplu: daca exista oameni in grupa, consideram utilizare 1
    return 1 if nr > 0 else 0

def insert_usage_for_sala(conn, id_sala: int, dt: datetime):
    last_people = get_last_people(conn, id_sala)

    # fallback daca nu exista inca people
    if last_people is None:
        temp = temperatura_simulata_int(dt)
        last_people = numar_oameni_simulat(dt, temp)

    aparate = distributie_aparate(last_people)

    with conn.cursor() as cursor:
        # 1) insert aparate_picioare
        cursor.execute("""
            INSERT INTO aparate_picioare
            (leg_press, hack_squat, leg_extension, leg_curl, hip_thrust, abductor_machine, adductor_machine)
            VALUES (%s,%s,%s,%s,%s,%s,%s)
        """, tuple([aparat_activ(aparate["picioare"])] * 7))
        id_picioare = cursor.lastrowid

        # 2) insert aparate_spate
        cursor.execute("""
            INSERT INTO aparate_spate
            (lat_pulldown, seated_row_machine, back_extension)
            VALUES (%s,%s,%s)
        """, tuple([aparat_activ(aparate["spate"])] * 3))
        id_spate = cursor.lastrowid

        # 3) insert aparate_piept
        cursor.execute("""
            INSERT INTO aparate_piept
            (chest_press, pec_deck, incline_chest_press)
            VALUES (%s,%s,%s)
        """, tuple([aparat_activ(aparate["piept"])] * 3))
        id_piept = cursor.lastrowid

        # 4) insert aparate_umeri
        cursor.execute("""
            INSERT INTO aparate_umeri
            (shoulder_press, lateral_raises)
            VALUES (%s,%s)
        """, tuple([aparat_activ(aparate["umeri"])] * 2))
        id_umeri = cursor.lastrowid

        # 5) insert aparate_brate
        cursor.execute("""
            INSERT INTO aparate_brate
            (biceps_curl, triceps_push_down)
            VALUES (%s,%s)
        """, tuple([aparat_activ(aparate["brate"])] * 2))
        id_brate = cursor.lastrowid

        # 6) insert aparate_abdomen
        cursor.execute("""
            INSERT INTO aparate_abdomen
            (ab_crunch, rotary_torso)
            VALUES (%s,%s)
        """, tuple([aparat_activ(aparate["abdomen"])] * 2))
        id_abdomen = cursor.lastrowid

        # 7) insert aparate_full_body
        cursor.execute("""
            INSERT INTO aparate_full_body
            (cable_crossover)
            VALUES (%s)
        """, (aparat_activ(aparate["full_body"]),))
        id_full = cursor.lastrowid

        # 8) leaga totul in sala_aparate
        cursor.execute("""
            INSERT INTO sala_aparate
            (id_aparate_picioare, id_aparate_spate, id_aparate_piept, id_aparate_umeri,
             id_aparate_brate, id_aparate_abdomen, id_aparate_full_body, id_sala)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
        """, (id_picioare, id_spate, id_piept, id_umeri, id_brate, id_abdomen, id_full, id_sala))

def main():
    dt = datetime.now().replace(second=0, microsecond=0)
    conn = get_connection()

    try:
        for sala_id in SALAS:
            insert_usage_for_sala(conn, sala_id, dt)
        conn.commit()
        print(f"[OK] Usage inserted @ {dt} for salas {SALAS.start}-{SALAS.stop-1}")
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    main()
