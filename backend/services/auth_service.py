"""
Authentication service — password hashing, JWT token creation/verification.
Place this file at: fyp-backend/services/auth_service.py
"""
import os
from datetime import datetime, timedelta
from passlib.context import CryptContext
from jose import jwt, JWTError
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from database.database import get_db
from models.user import User

# ------------------------------------------------------------------ #
# CONFIG
# ------------------------------------------------------------------ #
# In production, load this from an environment variable.
# For FYP purposes, a fixed secret is fine, but DON'T commit a
# real production secret to a public repo.
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "fyp-dukan-dost-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_DAYS = 30  # long-lived so the app doesn't log out often

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


# ------------------------------------------------------------------ #
# PASSWORD HASHING
# ------------------------------------------------------------------ #
def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


# ------------------------------------------------------------------ #
# JWT TOKEN CREATION / VERIFICATION
# ------------------------------------------------------------------ #
def create_access_token(user_id: int, email: str) -> str:
    expire = datetime.utcnow() + timedelta(days=ACCESS_TOKEN_EXPIRE_DAYS)
    payload = {"sub": str(user_id), "email": email, "exp": expire}
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def decode_access_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )


# ------------------------------------------------------------------ #
# DEPENDENCY — use this in any endpoint that needs the logged-in user
# ------------------------------------------------------------------ #
def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    payload = decode_access_token(token)
    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(status_code=401, detail="Invalid token payload")

    user = db.query(User).filter(User.id == int(user_id)).first()
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")

    return user