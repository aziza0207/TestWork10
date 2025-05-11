from __future__ import annotations

from typing import List

from sqlalchemy.orm import Mapped, MappedAsDataclass, mapped_column, relationship
from ..database import Base
from sqlalchemy import Integer, String



class User(MappedAsDataclass, Base, unsafe_hash=True):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(Integer, init=False, primary_key=True)
    name: Mapped[str | None] = mapped_column(String, nullable=True, default=None)
    password: Mapped[str | None] = mapped_column(String(255), nullable=True, default=None)




    def __repr__(self) -> str:
        return f"<User(id={self.id}, email={self.name})>"