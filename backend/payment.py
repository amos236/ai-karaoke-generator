from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException

from pydantic import BaseModel

from sqlalchemy.orm import Session

from database import get_db
from models import Payment, User


router = APIRouter()


# ==========================================
# Payment Request Model
# ==========================================

class PaymentRequest(BaseModel):

    user_id: int
    transaction_id: str
    amount: float


# ==========================================
# Submit Payment
# ==========================================

@router.post("/payment")
def submit_payment(

    request: PaymentRequest,

    db: Session = Depends(get_db)

):

    # --------------------------------------
    # Check User
    # --------------------------------------

    user = db.query(User).filter(

        User.id == request.user_id

    ).first()

    if not user:

        raise HTTPException(

            status_code=404,

            detail="User not found."

        )

    # --------------------------------------
    # Check Duplicate Transaction
    # --------------------------------------

    existing = db.query(Payment).filter(

        Payment.transaction_id == request.transaction_id

    ).first()

    if existing:

        raise HTTPException(

            status_code=400,

            detail="Transaction ID already submitted."

        )

    # --------------------------------------
    # Save Payment
    # --------------------------------------

    payment = Payment(

        user_id=request.user_id,

        transaction_id=request.transaction_id,

        amount=request.amount,

        payment_status="Pending"

    )

    db.add(payment)

    db.commit()

    db.refresh(payment)

    # --------------------------------------
    # Response
    # --------------------------------------

    return {

        "success": True,

        "message": "Payment submitted successfully.",

        "payment_id": payment.id,

        "payment_status": payment.payment_status

    }


# ==========================================
# User Payment History
# ==========================================

@router.get("/payment/{user_id}")
def payment_history(

    user_id: int,

    db: Session = Depends(get_db)

):

    payments = db.query(Payment).filter(

        Payment.user_id == user_id

    ).order_by(

        Payment.id.desc()

    ).all()

    result = []

    for p in payments:

        result.append({

            "id": p.id,

            "transaction_id": p.transaction_id,

            "amount": p.amount,

            "status": p.payment_status,

            "payment_date": p.payment_date,

            "subscription_start": p.subscription_start,

            "subscription_end": p.subscription_end

        })

    return result