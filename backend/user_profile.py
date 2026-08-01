from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException

from sqlalchemy.orm import Session

from database import get_db
from models import User

from datetime import datetime

router = APIRouter(tags=["Profile"])


@router.get("/profile/{user_id}")
def profile(

    user_id: int,

    db: Session = Depends(get_db)

):

    user = db.query(User).filter(

        User.id == user_id

    ).first()

    if user is None:

        raise HTTPException(

            status_code=404,

            detail="User not found."

        )

    # Automatically expire subscription

    if (

        user.subscription_status == "active"

        and

        user.subscription_end is not None

        and

        datetime.utcnow() > user.subscription_end

    ):

        user.subscription_status = "inactive"

        db.commit()

    return {

        "username": user.username,

        "email": user.email,

        "subscription_status": user.subscription_status,

        "expiry_date": user.subscription_end

    }