import datetime
from enum import Enum
from typing import List

from sqlalchemy import text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database import Base



class Role(Base):
    __tablename__ = "roles"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(unique=True)

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    surname: Mapped[str]
    patronymic: Mapped[str] = mapped_column(nullable=True)

    email: Mapped[str]
    password: Mapped[str]
    role_id: Mapped[int] = mapped_column(ForeignKey("roles.id"), nullable=True)

    registered_at: Mapped[datetime.datetime] = mapped_column(
        server_default=text(
            "TIMEZONE('utc', now())")
    )

    is_active: Mapped[bool] = mapped_column(default=True)

    role: Mapped['Role'] = relationship(lazy="joined")