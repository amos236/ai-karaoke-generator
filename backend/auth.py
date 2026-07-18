from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException

from sqlalchemy.orm import Session

from passlib.context import CryptContext

from database import get_db
from models import User

router = APIRouter()

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

    # Username already exists
    user = db.query(User).filter(
        User.username == username
    ).first()

    if user:
        raise HTTPException(
            status_code=400,
            detail="Username already exists."
        )

    # Email already exists
    email_user = db.query(User).filter(
        User.email == email
    ).first()

    if email_user:
        raise HTTPException(
            status_code=400,
            detail="Email already exists."
        )

    hashed_password = pwd_context.hash(password)

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