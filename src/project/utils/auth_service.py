from __future__ import annotations
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
from typing import Annotated, Dict, Any
from sqlalchemy import Integer, String, select
from sqlalchemy.orm import Mapped, MappedAsDataclass, mapped_column, relationship
from fastapi import Depends, HTTPException
from starlette import status
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from jose import jwt, JWTError
from ..database import Base
from .. import schemas
from ..models import User

SECRET_KEY = "197b2c37c391bed93fe80344fe73b806947a65e36206e05a1a23c2fa12702fe3"
ALGORITHM = "HS256"

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_bearer = OAuth2PasswordBearer(tokenUrl="auth/token")




class AuthService:
    @staticmethod
    def create_token(email: str, user_id: int, expires_delta: timedelta, token_type: str) -> str:
        expire = datetime.now(timezone.utc) + expires_delta
        payload = {"sub": email, "id": user_id, "type": token_type, "exp": expire}
        return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

    @staticmethod
    def create_token_pair(email: str, user_id: int):
        access_token_expires = timedelta(minutes=15)
        refresh_token_expires = timedelta(days=7)

        access_token = AuthService.create_token(
            email, user_id, access_token_expires, token_type="access"
        )
        refresh_token = AuthService.create_token(
            email, user_id, refresh_token_expires, token_type="refresh"
        )

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
        }

    @staticmethod
    def verify_password(password: str, hashed_password: str) -> bool:
        return bcrypt_context.verify(password, hashed_password)

    @staticmethod
    def authenticate_user(email: str, password: str, session: Session) -> User | bool:
        user = session.scalar(select(User).where(User.email == email))
        if not user:
            return False
        if not AuthService.verify_password(password, user.password):
            return False
        return user

    @staticmethod
    def decode_token(token: str) -> Dict[str, Any]:
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            return payload
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token or expired token",
            )
