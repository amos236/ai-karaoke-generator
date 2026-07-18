from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException

from sqlalchemy.orm import Session

from database import get_db
from models import User, Payment

from datetime import datetime, timedelta

router = APIRouter(
    prefix="/admin",
    tags=["Admin"]
)

# ==========================================
# Admin Login
# ==========================================

@router.post("/login")
def admin_login(
    username: str,
    password: str,
    db: Session = Depends(get_db)
):

    admin = db.query(User).filter(
        User.username == username,
        User.password == password,
        User.role == "admin"
    ).first()

    if admin is None:

        raise HTTPException(
            status_code=401,
            detail="Invalid Admin Username or Password."
        )

    return {

        "success": True,

        "user_id": admin.id,

        "username": admin.username,

        "role": admin.role

    }


# ==========================================
# Dashboard Statistics
# ==========================================

@router.get("/dashboard")
def dashboard(
    db: Session = Depends(get_db)
):

    total_users = db.query(User).count()

    active_subscribers = db.query(User).filter(
        User.subscription_status == "active"
    ).count()

    pending_payments = db.query(Payment).filter(
        Payment.payment_status == "Pending"
    ).count()

    return {

        "total_users": total_users,

        "active_subscribers": active_subscribers,

        "pending_payments": pending_payments

    }


# ==========================================
# Pending Payments
# ==========================================

@router.get("/pending-payments")
def pending_payments(
    db: Session = Depends(get_db)
):

    payments = db.query(Payment).filter(
        Payment.payment_status == "Pending"
    ).all()

    data = []

    for payment in payments:

        data.append({

            "id": payment.id,

            "user_id": payment.user_id,

            "transaction_id": payment.transaction_id,

            "amount": payment.amount,

            "payment_status": payment.payment_status

        })

    return data

    # ==========================================
# Approve Payment
# ==========================================

@router.post("/approve/{payment_id}")
def approve_payment(
    payment_id: int,
    db: Session = Depends(get_db)
):

    payment = db.query(Payment).filter(
        Payment.id == payment_id
    ).first()

    if payment is None:

        raise HTTPException(
            status_code=404,
            detail="Payment not found."
        )

    if payment.payment_status == "Approved":

        return {
            "message": "Payment already approved."
        }

    user = db.query(User).filter(
        User.id == payment.user_id
    ).first()

    if user is None:

        raise HTTPException(
            status_code=404,
            detail="User not found."
        )

    # ===============================
    # Subscription Dates
    # ===============================

    start_date = datetime.utcnow()

    end_date = start_date + timedelta(days=31)

    # ===============================
    # Update Payment
    # ===============================

    payment.payment_status = "Approved"

    payment.subscription_start = start_date

    payment.subscription_end = end_date

    # ===============================
    # Update User
    # ===============================

    user.subscription_status = "active"

    user.subscription_start = start_date

    user.subscription_end = end_date

    db.commit()

    return {

        "success": True,

        "message": "Subscription Activated Successfully.",

        "expiry_date": end_date.strftime("%d-%m-%Y")

    }

    # ==========================================
# Reject Payment
# ==========================================

@router.post("/reject/{payment_id}")
def reject_payment(
    payment_id: int,
    db: Session = Depends(get_db)
):

    payment = db.query(Payment).filter(
        Payment.id == payment_id
    ).first()

    if payment is None:

        raise HTTPException(
            status_code=404,
            detail="Payment not found."
        )

    payment.payment_status = "Rejected"

    db.commit()

    return {

        "success": True,

        "message": "Payment Rejected."

    }