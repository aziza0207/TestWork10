from __future__ import annotations
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from jose import jwt, JWTError
from typing import Annotated
from starlette import status
from fastapi import Depends, APIRouter, HTTPException, Path
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from ..models import User
from ..dependencies import get_db_session
from .. import schemas



router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
    "/register",
    response_model=schemas.AuthResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_user(
    user: schemas.UserCreate, session: Session = Depends(get_db_session)
):
    user = User.create_user(session=session, user=user)

    tokens = User.create_token_pair(email=user.email, user_id=user.id)
    user_data = schemas.UserRead(
        id=user.id,
        email=user.email,
        name=user.name

    )

    return schemas.AuthResponse(
        user=user_data,
        access_token=tokens["access_token"],
        refresh_token=tokens["refresh_token"],
    )


@router.post("/token")
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: Session = Depends(get_db_session),
):
    user = User.authenticate_user(form_data.username, form_data.password, session)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        )

    token = User.create_token_pair(email=user.email, user_id=user.id)

    return token





