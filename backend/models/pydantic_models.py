from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from models.transaction import TransactionType
from pydantic import BaseModel, EmailStr


class TransactionBase(BaseModel):
    person_name: str
    amount: float
    transaction_type: TransactionType
    description: Optional[str] = None
    transcript: Optional[str] = None


class TransactionCreate(TransactionBase):
    pass


class TransactionUpdate(BaseModel):
    person_name: Optional[str] = None
    amount: Optional[float] = None
    transaction_type: Optional[TransactionType] = None
    description: Optional[str] = None
    transcript: Optional[str] = None


class TransactionInDB(TransactionBase):
    id: int
    date: datetime

    class Config:
        from_attributes = True




class SignupRequest(BaseModel):
    email: EmailStr
    password: str
    shop_name: str | None = None


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: int
    email: str
    shop_name: str | None = None