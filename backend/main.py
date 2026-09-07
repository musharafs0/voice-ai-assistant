from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel
from pwdlib import PasswordHash
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend import models
from backend.database import Base, engine, get_db


Base.metadata.create_all(bind=engine)

app = FastAPI()

password_hasher = PasswordHash.recommended()


class SignupRequest(BaseModel):
    name: str
    email: str
    password: str


@app.get("/")
def root():
    return {"message": "Voice AI API is running"}


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