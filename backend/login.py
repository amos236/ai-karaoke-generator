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


@router.post("/login")
def login(

    username: str,

    password: str,

    db: Session = Depends(get_db)

):

    user = db.query(User).filter(
        User.username == username
    ).first()

    if user is None:

        raise HTTPException(
            status_code=401,
            detail="Invalid Username."
        )

    if not pwd_context.verify(
        password,
        user.password
    ):

        raise HTTPException(
            status_code=401,
            detail="Invalid Password."
        )

    return {

        "success": True,

        "message": "Login Successful",

        "user_id": user.id,

        "username": user.username,

        "role": user.role,

        "subscription_status": user.subscription_status

    }