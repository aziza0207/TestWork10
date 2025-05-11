from __future__ import annotations
import datetime
from sqlalchemy import DateTime, ForeignKey, Integer, String, Enum, Text, func, select
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


class Service(MappedAsDataclass, Base, unsafe_hash=True):
    __tablename__ = "service"

    title: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)

    id: Mapped[int] = mapped_column(Integer, init=False, primary_key=True)

    owner_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("user.id", ondelete="CASCADE"),
        nullable=False,
        init=False,
    )

    user: Mapped["User"] = relationship(
        "User",
        backref=backref("services", passive_deletes=True)
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
    def get_all(session: Session) -> Sequence[Service] | None:
        return (session.scalars(select(Service))).all()
