from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import DateTime
from sqlalchemy import ForeignKey
from sqlalchemy import Float

from datetime import datetime

from database import Base


# ==========================================
# User Table
# ==========================================

class User(Base):

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)

    username = Column(
        String(100),
        unique=True,
        nullable=False
    )

    email = Column(
        String(200),
        unique=True,
        nullable=False
    )

    password = Column(
        String(255),
        nullable=False
    )

    role = Column(
        String(20),
        default="user"
    )

    subscription_status = Column(
        String(20),
        default="inactive"
    )

    subscription_start = Column(
        DateTime,
        nullable=True
    )

    subscription_end = Column(
        DateTime,
        nullable=True
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )


# ==========================================
# Payment Table
# ==========================================

class Payment(Base):

    __tablename__ = "payments"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    )

    transaction_id = Column(
        String(100),
        unique=True,
        nullable=False
    )

    amount = Column(
        Float,
        default=10.0
    )

    payment_status = Column(
        String(30),
        default="Pending"
    )

    payment_date = Column(
        DateTime,
        default=datetime.utcnow
    )

    subscription_start = Column(
        DateTime,
        nullable=True
    )

    subscription_end = Column(
        DateTime,
        nullable=True
    )


# ==========================================
# Karaoke History
# ==========================================

class History(Base):

    __tablename__ = "history"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    user_id = Column(
        Integer,
        ForeignKey("users.id")
    )

    original_song = Column(
        String(255)
    )

    karaoke_song = Column(
        String(255)
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )