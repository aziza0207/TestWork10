from typing import Annotated
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends
from starlette import status
from ..models import Service
from ..dependencies import get_db_session

router = APIRouter(prefix="/services", tags=["services"])

@router.get("/", status_code=status.HTTP_200_OK)
async def get_services(session: Session = Depends(get_db_session)):
    services = Service.get_all(session)
    return services
