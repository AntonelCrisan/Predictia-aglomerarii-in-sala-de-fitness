from pydantic import BaseModel

class User(BaseModel):
    id: int
    nume: str
    email: str
    parola: str
    id_sala: int
    telefon: str
    cnp: str
    rol: str  # "admin", "antrenor", "cursant"
