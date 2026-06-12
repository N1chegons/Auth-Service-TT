from sqlalchemy.orm import Mapped, mapped_column

from src.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    surname: Mapped[str]
    patronymic: Mapped[str] = mapped_column(nullable=True, default=None)

    email: Mapped[str]
    password: Mapped[str]

    is_active: Mapped[bool] = mapped_column(default=True)
    is_superuser: Mapped[bool] = mapped_column(default=False)