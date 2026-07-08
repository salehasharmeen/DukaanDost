from sqlalchemy import Column, Integer, String, Float, DateTime, Enum, ForeignKey
from sqlalchemy.sql import func
from database.database import Base
import enum


class TransactionType(str, enum.Enum):
    CREDIT = "credit"
    DEBIT = "debit"


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)

    person_name = Column(String, index=True)

    amount = Column(Float)

    transaction_type = Column(
        Enum(TransactionType),
        default=TransactionType.DEBIT
    )

    date = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    description = Column(String, nullable=True)

    transcript = Column(String, nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)