from pydantic import BaseModel

class User(BaseModel):
    id: int
    nume: str
    email: str
    telefon: str
    cnp: str
    parola: str
    rol: str  # "admin", "antrenor", "cursant"
