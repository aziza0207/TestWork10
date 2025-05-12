from typing import Annotated, List, Optional
from fastapi import Query
from sqlalchemy import select, or_
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from fastapi import APIRouter, Depends, HTTPException, Body, Path
from fastapi.security import OAuth2PasswordRequestForm
from starlette import status
from ..models import Service, User
from ..dependencies import get_db_session
from ..schemas import ServiceBase, ServiceUpdate, ServiceList

router = APIRouter(prefix="/tasks", tags=["tasks"])

user_dependency = Annotated[dict, Depends(User.get_current_user)]


@router.get("/", response_model=List[ServiceList], status_code=status.HTTP_200_OK)
async def get_tasks(
    session: Session = Depends(get_db_session),
    user: dict = Depends(User.get_current_user),
):

    db_user = session.scalar(select(User).where(User.id == user["id"]))
    if not db_user:
        raise HTTPException(status_code=404, detail="Authentication Failed")

    services = Service.get_all(session, user["id"])
    return services


@router.patch(
    "/{task_id}/", response_model=ServiceUpdate, status_code=status.HTTP_200_OK
)
async def update_task(
    session: Session = Depends(get_db_session),
    user: dict = Depends(User.get_current_user),
    task_id: int = Path(gt=0),
    service: ServiceUpdate = Body(),
):

    db_service = Service.get_by_id(session=session, id=task_id, owner_id=user["id"])

    db_user = session.scalar(select(User).where(User.id == user["id"]))
    if not db_user:
        raise HTTPException(status_code=404, detail="Authentication Failed")

    if db_service is None:
        raise HTTPException(status_code=404, detail="Service not found!")

    try:

        for field, value in service.model_dump(exclude_unset=True).items():
            setattr(db_service, field, value)

        session.add(db_service)
        session.commit()
        session.refresh(db_service)
        return db_service

    except Exception as e:
        session.rollback()
        raise HTTPException(
            status_code=500, detail="Unexpected server error: " + str(e)
        )


@router.post("/", response_model=ServiceBase, status_code=status.HTTP_201_CREATED)
async def create_task(
    session: Session = Depends(get_db_session),
    user: dict = Depends(User.get_current_user),
    service: ServiceBase = Body(),
):

    db_user = session.scalar(select(User).where(User.id == user["id"]))
    if not db_user:
        raise HTTPException(status_code=404, detail="Authentication Failed")

    user = session.scalar(select(User).where(User.id == user["id"]))

    existing_service = session.scalar(
        select(Service).where(Service.title == service.title)
    )

    if existing_service:
        raise HTTPException(
            status_code=400, detail="Service with this title already exists"
        )

    try:
        new_service = Service.create_task(
            session=session, owner_id=user.id, service=service, user=user
        )
        return new_service

    except Exception as e:
        session.rollback()
        raise HTTPException(
            status_code=500, detail="Unexpected server error: " + str(e)
        )


@router.get(
    "/search/", response_model=List[ServiceList], status_code=status.HTTP_200_OK
)
async def search_tasks(
    session: Session = Depends(get_db_session),
    user: dict = Depends(User.get_current_user),
    q: Optional[str] = Query(None, min_length=1),
):

    db_user = session.scalar(select(User).where(User.id == user["id"]))
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    stmt = select(Service).where(Service.owner_id == db_user.id)

    if q:
        stmt = stmt.where(Service.title.ilike(f"%{q}%"))

    results = session.scalars(stmt).all()
    return results
