# API Endpoint Snippet (FastAPI)

from app.models import UserLogin
from fastapi import APIRouter, HTTPException

router = APIRouter()

@router.post("/auth/login")
def login(user: UserLogin):
    token = auth_service.authenticate(user.email, user.password)
    if not token:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return {"access_token": token}
