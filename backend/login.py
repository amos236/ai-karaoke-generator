from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from passlib.context import CryptContext

from database import get_db
from models import User


# ============================================================
# ROUTER
# ============================================================

router = APIRouter()


# ============================================================
# PASSWORD HASHING
# ============================================================

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)


# ============================================================
# LOGIN API
# ============================================================

@router.post("/login")
def login(
    username: str,
    password: str,
    db: Session = Depends(get_db)
):

    # --------------------------------------------------------
    # FIND USER BY USERNAME
    # --------------------------------------------------------

    user = db.query(User).filter(
        User.username == username
    ).first()


    # --------------------------------------------------------
    # CHECK USER EXISTS
    # --------------------------------------------------------

    if user is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid Username."
        )


    # --------------------------------------------------------
    # BCRYPT PASSWORD LIMIT
    # bcrypt supports a maximum of 72 bytes
    # --------------------------------------------------------

    password_to_verify = password[:72]


    # --------------------------------------------------------
    # VERIFY PASSWORD
    # --------------------------------------------------------

    password_valid = pwd_context.verify(
        password_to_verify,
        user.password
    )


    # --------------------------------------------------------
    # INVALID PASSWORD
    # --------------------------------------------------------

    if not password_valid:
        raise HTTPException(
            status_code=401,
            detail="Invalid Password."
        )


    # --------------------------------------------------------
    # LOGIN SUCCESSFUL
    # --------------------------------------------------------

    return {
        "success": True,
        "message": "Login Successful",
        "user_id": user.id,
        "username": user.username,
        "role": user.role,
        "subscription_status": user.subscription_status
    }