from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

from database import get_db
from models import User


router = APIRouter()

# Password hashing
pwd_hasher = PasswordHasher()


@router.post("/register")
def register(
    username: str,
    email: str,
    password: str,
    db: Session = Depends(get_db)
):

    # Check username
    user = db.query(User).filter(
        User.username == username
    ).first()

    if user:
        raise HTTPException(
            status_code=400,
            detail="Username already exists."
        )

    # Check email
    email_user = db.query(User).filter(
        User.email == email
    ).first()

    if email_user:
        raise HTTPException(
            status_code=400,
            detail="Email already exists."
        )

    # Hash password using Argon2
    hashed_password = pwd_hasher.hash(password)

    # Create new user
    new_user = User(
        username=username,
        email=email,
        password=hashed_password
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {
        "success": True,
        "message": "Registration Successful"
    }