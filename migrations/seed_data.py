import asyncio
from sqlalchemy import select
from passlib.context import CryptContext

from src.database import async_session
from src.auth.models import User, Role
from src.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

async def seed():
    async with async_session() as session:
        roles = {
            "user": Role(title="user"),
            "admin": Role(title="admin"),
            "manager": Role(title="manager"),
        }

        for role in roles.values():
            existing = await session.execute(select(Role).where(Role.title == role.title))
            if not existing.scalar_one_or_none():
                session.add(role)

        await session.flush()

        result = await session.execute(select(Role))
        db_roles = {r.title: r.id for r in result.scalars()}

        users = [
            {
                "name": "Гоша",
                "surname": "Базанов",
                "patronymic": "Сергеевич",
                "email": "admin@test.com",
                "password": "testtesttest",
                "role_id": db_roles["admin"],
                "is_active": True,
            },
            {
                "name": "Николай",
                "surname": "Наумов",
                "patronymic": "Владимирович",
                "email": "kolya@mail.com",
                "password": "testtesttest",
                "role_id": db_roles["user"],
                "is_active": True,
            },
            {
                "name": "Владимир",
                "surname": "Селиванов",
                "patronymic": "Викторович",
                "email": "vovasel@gmail.com",
                "password": "testtesttest",
                "role_id": db_roles["user"],
                "is_active": True,
            },
            {
                "name": "Валентиная",
                "surname": "Пастухова",
                "patronymic": "Алексеевна",
                "email": "vvalya@yandex.com",
                "password": "testtesttest",
                "role_id": db_roles["manager"],
                "is_active": True,
            },
            {
                "name": "Валентиная",
                "surname": "Пастухова",
                "patronymic": "Максимовна",
                "email": "vvalya@yandex.com",
                "password": "testtesttest",
                "role_id": db_roles["manager"],
                "is_active": True,
            },
            {
                "name": "Максим",
                "surname": "Гулаев",
                "patronymic": "Маналович",
                "email": "maxgul@yandex.com",
                "password": "testtesttest",
                "role_id": db_roles["manager"],
                "is_active": True,
            },
        ]

        for user_data in users:
            existing = await session.execute(select(User).where(User.email == user_data["email"]))
            if not existing.scalar_one_or_none():
                hashed = pwd_context.hash(user_data["password"])
                user = User(
                    name=user_data["name"],
                    surname=user_data["surname"],
                    patronymic=user_data["patronymic"],
                    email=user_data["email"],
                    password=hashed,
                    role_id=user_data["role_id"],
                    is_active=user_data["is_active"],
                )
                session.add(user)

        await session.commit()

if __name__ == "__main__":
    asyncio.run(seed())