from __future__ import annotations
from datetime import timedelta
from typing import Annotated
from starlette import status
from fastapi import Depends, APIRouter, HTTPException, Path
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from ..models import User
from ..dependencies import get_db_session
from .. import schemas
from ..utils.auth_service import AuthService

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

    tokens = AuthService.create_token_pair(email=user.email, user_id=user.id)
    user_data = schemas.UserRead(id=user.id, email=user.email, name=user.name)

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
    user = AuthService.authenticate_user(form_data.username, form_data.password, session)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        )

    token = AuthService.create_token_pair(email=user.email, user_id=user.id)

    return token




@router.post("/refresh")
def refresh_token(payload: schemas.RefreshTokenRequest):
    token_data = AuthService.decode_token(payload.refresh_token)

    if not token_data or token_data.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
        )

    user_id = token_data.get("id")
    email = token_data.get("sub")

    if not user_id or not email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid token payload",
        )


    access_token = User.create_token(
        email=email,
        user_id=user_id,
        expires_delta=timedelta(minutes=15),
        token_type="access",
    )

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }