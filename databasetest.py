from models import User

# baza de date temporară în memorie
users_db = [
    {
        "id": 1,
        "nume": "Admin Principal",
        "email": "admin@admin.com",
        "telefon": "0700000000",
        "cnp": "1980000000000",
        "parola": "admin123",
        "rol": "admin"
    }
]

def next_id():
    return max([u["id"] for u in users_db]) + 1 if users_db else 1
