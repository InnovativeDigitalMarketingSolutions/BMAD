# API Template voor FullstackDeveloper

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
import jwt
from datetime import datetime, timedelta

app = FastAPI(title="BMAD API", version="1.0.0")

# Pydantic models
class UserLogin(BaseModel):
    email: str
    password: str

class UserResponse(BaseModel):
    id: int
    email: str
    name: str
    created_at: datetime

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

# Authentication service
class AuthService:
    def __init__(self):
        self.secret_key = "your-secret-key"
        self.algorithm = "HS256"
    
    def authenticate(self, email: str, password: str) -> str:
        # Simulate authentication
        if email == "test@test.com" and password == "secret":
            return self.create_token({"sub": email})
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    def create_token(self, data: dict) -> str:
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(minutes=30)
        to_encode.update({"exp": expire})
        return jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)

auth_service = AuthService()

# API Endpoints
@app.post("/auth/login", response_model=TokenResponse)
async def login(user: UserLogin):
    """User login endpoint"""
    try:
        token = auth_service.authenticate(user.email, user.password)
        return TokenResponse(access_token=token)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/users", response_model=List[UserResponse])
async def get_users():
    """Get all users"""
    # Simulate user data
    users = [
        UserResponse(id=1, email="user1@example.com", name="User 1", created_at=datetime.now()),
        UserResponse(id=2, email="user2@example.com", name="User 2", created_at=datetime.now())
    ]
    return users

@app.get("/api/users/{user_id}", response_model=UserResponse)
async def get_user(user_id: int):
    """Get user by ID"""
    # Simulate user lookup
    if user_id == 1:
        return UserResponse(id=1, email="user1@example.com", name="User 1", created_at=datetime.now())
    raise HTTPException(status_code=404, detail="User not found")

# Health check
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now()}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 