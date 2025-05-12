from __future__ import annotations
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
from typing import Annotated
from sqlalchemy import Integer, String, select
from sqlalchemy.orm import Mapped, MappedAsDataclass, mapped_column, relationship
from fastapi import Depends, HTTPException
from starlette import status
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from jose import jwt, JWTError
from ..database import Base
from .. import schemas


SECRET_KEY = "197b2c37c391bed93fe80344fe73b806947a65e36206e05a1a23c2fa12702fe3"
ALGORITHM = "HS256"

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_bearer = OAuth2PasswordBearer(tokenUrl="auth/token")


class User(MappedAsDataclass, Base, unsafe_hash=True):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(Integer, init=False, primary_key=True)
    email: Mapped[str | None] = mapped_column(String, nullable=True, default=None)
    name: Mapped[str | None] = mapped_column(String, nullable=True, default=None)
    password: Mapped[str | None] = mapped_column(
        String(255), nullable=True, default=None
    )

    @staticmethod
    def create_user(session: Session, user: schemas.UserCreate) -> User:
        new_user = User(
            email=user.email,
            name=user.name,
            password=bcrypt_context.hash(user.password),
        )
        session.add(new_user)
        session.commit()
        session.refresh(new_user)
        return new_user

    def __repr__(self) -> str:
        return f"<User(id={self.id}, email={self.name})>"

    @staticmethod
    def create_token(email: str, user_id: int, expires_delta: timedelta, token_type: str) -> str:
        expire = datetime.now(timezone.utc) + expires_delta
        payload = {
            "sub": email,
            "id": user_id,
            "type": token_type,
            "exp": expire
        }
        return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

    @staticmethod
    def create_token_pair(email: str, user_id: int):
        access_token_expires = timedelta(minutes=15)
        refresh_token_expires = timedelta(days=7)

        access_token = User.create_token(email, user_id, access_token_expires, token_type="access")
        refresh_token = User.create_token(email, user_id, refresh_token_expires, token_type="refresh")

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer"
        }



    # @staticmethod
    # def create_access_token(email: str, user_id: int, expires_delta: timedelta):
    #     to_encode = {"sub": email, "id": user_id}
    #     if expires_delta:
    #         expire = datetime.now(timezone.utc) + expires_delta
    #     else:
    #         expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    #     to_encode.update({"exp": expire})
    #     encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    #     return encoded_jwt

    @staticmethod
    def verify_password(password, hashed_password):
        return bcrypt_context.verify(password, hashed_password)

    @staticmethod
    def authenticate_user(email: str, password: str, session: Session) -> User | bool:
        user = session.scalar(select(User).where(User.email == email))
        if not user:
            return False
        if not User.verify_password(password, user.password):
            return False
        return user

    @staticmethod
    async def get_current_user(token: Annotated[str, Depends(oauth2_bearer)]):

        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            email: str = payload.get("sub")
            user_id: int = payload.get("id")
            if email is None or user_id is None:
                raise credentials_exception
            return {"email": email, "id": user_id}
        except JWTError:
            raise credentials_exception







