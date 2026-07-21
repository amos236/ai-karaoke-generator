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


@router.post("/register")
def register(
    username: str,
    email: str,
    password: str,
    db: Session = Depends(get_db)
):

    # -----------------------------------------
    # 1. Check if username already exists
    # -----------------------------------------
    user = db.query(User).filter(
        User.username == username
    ).first()

    if user:
        raise HTTPException(
            status_code=400,
            detail="Username already exists."
        )


    # -----------------------------------------
    # 2. Check if email already exists
    # -----------------------------------------
    email_user = db.query(User).filter(
        User.email == email
    ).first()

    if email_user:
        raise HTTPException(
            status_code=400,
            detail="Email already exists."
        )


    # -----------------------------------------
    # 3. Limit password to 72 bytes
    # bcrypt supports a maximum of 72 bytes
    # -----------------------------------------
    password = password[:72]


    # -----------------------------------------
    # 4. Hash password
    # -----------------------------------------
    hashed_password = pwd_context.hash(password)


    # -----------------------------------------
    # 5. Create new user
    # -----------------------------------------
    new_user = User(
        username=username,
        email=email,
        password=hashed_password
    )


    # -----------------------------------------
    # 6. Save user to database
    # -----------------------------------------
    db.add(new_user)

    db.commit()

    db.refresh(new_user)


    # -----------------------------------------
    # 7. Return success response
    # -----------------------------------------
    return {
        "success": True,
        "message": "Registration Successful"
    }