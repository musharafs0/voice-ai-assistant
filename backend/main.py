from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel
from pwdlib import PasswordHash
from sqlalchemy import select
from sqlalchemy.orm import Session
from backend.auth import (create_access_token,verify_access_token,security)
from fastapi.security import HTTPAuthorizationCredentials

from backend import models
from backend.database import Base, engine, get_db


Base.metadata.create_all(bind=engine)

app = FastAPI()

password_hasher = PasswordHash.recommended()


class SignupRequest(BaseModel):
    name: str
    email: str
    password: str

class LoginRequest(BaseModel):
    email: str
    password: str

class ChatRequest(BaseModel):
    message: str


@app.post("/chat")
def chat(
    request: ChatRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    token = credentials.credentials

    user_id = verify_access_token(token)

    db_user = db.get(models.User, user_id)

    if db_user is None:
        raise HTTPException(
            status_code=401,
            detail="User not found"
        )

    return {
        "user_id": db_user.id,
        "message": request.message,
        "response": "AI will be connected next"
    }


@app.get("/")
def root():
    return {"message": "Voice AI API is running"}


@app.get("/me")
def get_me(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    token = credentials.credentials

    user_id = verify_access_token(token)

    db_user = db.get(models.User, user_id)

    if db_user is None:
        raise HTTPException(
            status_code=401,
            detail="User not found"
        )

    return {
        "id": db_user.id,
        "name": db_user.name,
        "email": db_user.email
    }



@app.post("/signup")
def signup(user: SignupRequest, db: Session = Depends(get_db)):

    existing_user = db.scalar(
        select(models.User).where(models.User.email == user.email)
    )

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )

    hashed_password = password_hasher.hash(user.password)

    new_user = models.User(
        name=user.name,
        email=user.email,
        password_hash=hashed_password
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {
        "message": "User created successfully",
        "id": new_user.id,
        "name": new_user.name,
        "email": new_user.email
    }


@app.post("/login")
def login(user: LoginRequest, db: Session = Depends(get_db)):

    db_user = db.scalar(
        select(models.User).where(models.User.email == user.email)
    )

    if not db_user:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    password_valid = password_hasher.verify(
        user.password,
        db_user.password_hash
    )

    if not password_valid:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    access_token = create_access_token(db_user.id)

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }