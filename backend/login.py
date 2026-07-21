from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from passlib.context import CryptContext

from database import get_db
from models import User


router = APIRouter()


# Password hashing configuration
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)


@router.post("/login")
def login(
    username: str,
    password: str,
    db: Session = Depends(get_db)
):

    # Find user by username
    user = db.query(User).filter(
        User.username == username
    ).first()

    # Username not found
    if user is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid Username."
        )

    # Verify password
    # bcrypt supports a maximum of 72 bytes
    password_to_verify = password[:72]

    if not pwd_context.verify(
        password_to_verify,
        user.password
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid Password."
        )

    # Login successful
    return {
        "success": True,
        "message": "Login Successful",
        "user_id": user.id,
        "username": user.username,
        "role": user.role,
        "subscription_status": user.subscription_status
    }