from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from argon2 import PasswordHasher

from database import get_db
from models import User

router = APIRouter()

pwd_hasher = PasswordHasher()


@router.post("/register")
def register(
    username: str,
    email: str,
    password: str,
    db: Session = Depends(get_db)
):

    username = username.strip()

    if not username:
        raise HTTPException(status_code=400, detail="Username is required.")

    email = email.strip().lower()

    if not email:
        raise HTTPException(status_code=400, detail="Email is required.")

    if not password:
        raise HTTPException(status_code=400, detail="Password is required.")

    if len(password) < 4:
        raise HTTPException(
            status_code=400,
            detail="Password must contain at least 4 characters."
        )

    existing_username = db.query(User).filter(
        User.username == username
    ).first()

    if existing_username:
        raise HTTPException(
            status_code=400,
            detail="Username already exists."
        )

    existing_email = db.query(User).filter(
        User.email == email
    ).first()

    if existing_email:
        raise HTTPException(
            status_code=400,
            detail="Email already exists."
        )

    hashed_password = pwd_hasher.hash(password)

    new_user = User(
        username=username,
        email=email,
        password=hashed_password
    )

    try:
        db.add(new_user)
        db.commit()
        db.refresh(new_user)

    except Exception:
        db.rollback()

        raise HTTPException(
            status_code=500,
            detail="Registration failed."
        )

    return {
        "success": True,
        "message": "Registration Successful",
        "user_id": new_user.id,
        "username": new_user.username,
        "email": new_user.email
    }