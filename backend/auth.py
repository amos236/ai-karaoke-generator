from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError, VerificationError

from database import get_db
from models import User


# Create API Router
router = APIRouter()


# ============================================================
# PASSWORD HASHING
# ============================================================

pwd_hasher = PasswordHasher()


# ============================================================
# REGISTER USER
# ============================================================

@router.post("/register")
def register(
    username: str,
    email: str,
    password: str,
    db: Session = Depends(get_db)
):

    # --------------------------------------------------------
    # Validate username
    # --------------------------------------------------------

    username = username.strip()

    if not username:
        raise HTTPException(
            status_code=400,
            detail="Username is required."
        )


    # --------------------------------------------------------
    # Validate email
    # --------------------------------------------------------

    email = email.strip().lower()

    if not email:
        raise HTTPException(
            status_code=400,
            detail="Email is required."
        )


    # --------------------------------------------------------
    # Validate password
    # --------------------------------------------------------

    if not password:
        raise HTTPException(
            status_code=400,
            detail="Password is required."
        )

    if len(password) < 4:
        raise HTTPException(
            status_code=400,
            detail="Password must contain at least 4 characters."
        )


    # --------------------------------------------------------
    # Check if username already exists
    # --------------------------------------------------------

    existing_username = db.query(User).filter(
        User.username == username
    ).first()

    if existing_username:
        raise HTTPException(
            status_code=400,
            detail="Username already exists."
        )


    # --------------------------------------------------------
    # Check if email already exists
    # --------------------------------------------------------

    existing_email = db.query(User).filter(
        User.email == email
    ).first()

    if existing_email:
        raise HTTPException(
            status_code=400,
            detail="Email already exists."
        )


    # --------------------------------------------------------
    # Hash password using Argon2
    # --------------------------------------------------------

    hashed_password = pwd_hasher.hash(password)


    # --------------------------------------------------------
    # Create new user
    # --------------------------------------------------------

    new_user = User(
        username=username,
        email=email,
        password=hashed_password
    )


    # --------------------------------------------------------
    # Save user to database
    # --------------------------------------------------------

    try:

        db.add(new_user)

        db.commit()

        db.refresh(new_user)

    except Exception:

        db.rollback()

        raise HTTPException(
            status_code=500,
            detail="Registration failed. Please try again."
        )


    # --------------------------------------------------------
    # Registration successful
    # --------------------------------------------------------

    return {
        "success": True,
        "message": "Registration Successful",
        "user_id": new_user.id,
        "username": new_user.username,
        "email": new_user.email
    }