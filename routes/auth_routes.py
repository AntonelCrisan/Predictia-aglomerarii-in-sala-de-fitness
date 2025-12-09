from fastapi import APIRouter, HTTPException
from models import User, LoginRequest
from database import get_connection

router = APIRouter(prefix="/auth", tags=["Auth"])

# ------------------ REGISTER ------------------
@router.post("/register")
def register(user: User):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        # Check if email already exists
        cursor.execute("SELECT id FROM utilizatori WHERE email = %s", (user.email,))
        if cursor.fetchone():
            raise HTTPException(status_code=400, detail="Email deja folosit")

        # Insert new user
        cursor.execute("""
            INSERT INTO utilizatori (nume, email, telefon, cnp, parola, rol)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (user.nume, user.email, user.telefon, user.cnp, user.parola, user.rol))

        user_id = cursor.lastrowid

        # Get the created user data
        cursor.execute("SELECT * FROM utilizatori WHERE id = %s", (user_id,))
        user_data = cursor.fetchone()

        conn.commit()

        # Convert to dict format
        user_dict = {
            "id": user_data[0],
            "nume": user_data[1],
            "email": user_data[2],
            "telefon": user_data[3],
            "cnp": user_data[4],
            "parola": user_data[5],
            "rol": user_data[6]
        }

        return {"status": "success", "message": "Cont creat", "data": user_dict}

    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Eroare la înregistrare: {str(e)}")
    finally:
        cursor.close()
        conn.close()

# ------------------ LOGIN ------------------
@router.post("/login")
def login(request: LoginRequest):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            SELECT id, nume, email, telefon, cnp, parola, rol
            FROM utilizatori
            WHERE email = %s AND parola = %s
        """, (request.email, request.parola))

        user_data = cursor.fetchone()

        if not user_data:
            raise HTTPException(status_code=401, detail="Email sau parolă greșită")

        # Convert to dict format
        user_dict = {
            "id": user_data[0],
            "nume": user_data[1],
            "email": user_data[2],
            "telefon": user_data[3],
            "cnp": user_data[4],
            "parola": user_data[5],
            "rol": user_data[6]
        }

        return user_dict

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Eroare la autentificare: {str(e)}")
    finally:
        cursor.close()
        conn.close()
