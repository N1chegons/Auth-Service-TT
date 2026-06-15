import datetime
from typing import List

from sqlalchemy import text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.auth.models import Role
from src.database import Base


class Task(Base):
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(unique=True)
    description: Mapped[str] = mapped_column(nullable=True)
    created_by: Mapped[int] = mapped_column(ForeignKey("users.id"))

    role_id: Mapped[int] = mapped_column(ForeignKey("roles.id"))
    view_role: Mapped['Role'] = relationship()

    created_at: Mapped[datetime.datetime] = mapped_column(
        server_default=text(
            "TIMEZONE('utc', now())")
    )
    updated_at: Mapped[datetime.datetime] = mapped_column(nullable=True)


