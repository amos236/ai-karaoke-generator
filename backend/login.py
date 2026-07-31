from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError, VerificationError

from database import get_db
from models import User

router = APIRouter()

pwd_hasher = PasswordHasher()


@router.post("/login")
def login(
    username: str,
    password: str,
    db: Session = Depends(get_db)
):

    username = username.strip()

    user = db.query(User).filter(
        User.username == username
    ).first()

    if user is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid Username."
        )

    try:
        pwd_hasher.verify(user.password, password)

    except VerifyMismatchError:
        raise HTTPException(
            status_code=401,
            detail="Invalid Password."
        )

    except VerificationError:
        raise HTTPException(
            status_code=500,
            detail="Password verification failed."
        )

    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Login failed."
        )

    # Rehash password if Argon2 parameters have changed
    if pwd_hasher.check_needs_rehash(user.password):
        user.password = pwd_hasher.hash(password)
        db.commit()

    return {
        "success": True,
        "message": "Login Successful",
        "user_id": user.id,
        "username": user.username,
        "role": user.role,
        "subscription_status": user.subscription_status
    }