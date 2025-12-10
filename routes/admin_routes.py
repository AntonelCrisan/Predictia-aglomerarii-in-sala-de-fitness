from fastapi import APIRouter, HTTPException
from database import users_db

router = APIRouter(prefix="/admin", tags=["Admin"])

@router.get("/users")
def get_users():
    return users_db

@router.delete("/users/{user_id}")
def delete_user(user_id: int):
    for u in users_db:
        if u["id"] == user_id:
            users_db.remove(u)
            return {"status": "deleted"}
    raise HTTPException(status_code=404, detail="User not found")
