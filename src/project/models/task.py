from __future__ import annotations
import datetime
from sqlalchemy import (
    DateTime,
    ForeignKey,
    Integer,
    String,
    Enum,
    Text,
    func,
    select,
    desc,
)
from sqlalchemy.orm import (
    Mapped,
    MappedAsDataclass,
    Session,
    mapped_column,
    backref,
    relationship,
)
from collections.abc import Sequence
from ..database import Base
from ..utils.enums import ServiceStatus
from ..models import User
from ..schemas import ServiceBase


class Service(MappedAsDataclass, Base, unsafe_hash=True):
    __tablename__ = "service"

    title: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)

    id: Mapped[int] = mapped_column(Integer, init=False, primary_key=True)

    owner_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("user.id", ondelete="CASCADE"),
        nullable=False,
    )

    user: Mapped["User"] = relationship(
        "User", backref=backref("services", passive_deletes=True)
    )
    status: Mapped[ServiceStatus] = mapped_column(
        Enum(ServiceStatus), default=ServiceStatus.PENDING, nullable=False
    )

    description: Mapped[str | None] = mapped_column(Text, nullable=True, default=None)
    priority: Mapped[int] = mapped_column(Integer, nullable=True, default=0)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False, init=False
    )

    @staticmethod
    def get_all(
        session: Session,
        owner_id: int,
        title: str | None = None,
        status: ServiceStatus | None = None,
        priority: int | None = None,
    ) -> Sequence[Service] | None:

        stmt = (
            select(Service)
            .where(Service.owner_id == owner_id)
            .order_by(desc(Service.created_at))
        )

        if title:
            stmt = stmt.where(Service.status == status)

        if status:
            stmt = stmt.where(Service.status == status)

        if priority:
            stmt = stmt.where(Service.priority == priority)

        return session.scalars(stmt).all()

    @staticmethod
    def get_by_id(session: Session, id: int, owner_id: int) -> Service | None:
        return session.scalar(
            select(Service)
            .where(Service.id == int(id))
            .where(Service.owner_id == owner_id)
        )

    @staticmethod
    def create_task(
        session: Session, service: ServiceBase, owner_id, user: User
    ) -> Service:
        db_service = Service(
            title=service.title,
            description=service.description,
            priority=service.priority,
            status=service.status,
            owner_id=owner_id,
            user=user,
        )
        session.add(db_service)
        session.commit()
        session.refresh(db_service)
        return db_service

    @staticmethod
    def get_by_title(
        session: Session,
        owner_id: int,
        search: str | None = None,
    ) -> Sequence[Service] | None:

        stmt = select(Service).where(Service.owner_id == owner_id)

        if search:
            stmt = stmt.where(Service.title.ilike(f"%{search}%"))

        return session.scalars(stmt).all()
