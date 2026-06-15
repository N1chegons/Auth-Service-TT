from passlib.context import CryptContext
from pydantic import EmailStr
from sqlalchemy import select, insert, update, delete
from sqlalchemy.orm import joinedload

from src.auth.models import User, Role
from src.database import async_session


class AuthRepository:
    PWD_CON = CryptContext(
        schemes=["bcrypt"],
        deprecated="auto",
        bcrypt__rounds=12,
        bcrypt__ident="2b"
    )

    @classmethod
    async def register(cls, values: dict, password: str):
        async with async_session() as session:
            hashed_password = cls.PWD_CON.hash(password)

            stmt = insert(User).values(**values, role_id=1, password=hashed_password)
            await session.execute(stmt)
            await session.commit()

class UserRepository:
    @classmethod
    async def get_user(cls, email: EmailStr):
        async with async_session() as session:
            query = select(User).filter_by(email=email)
            result = await session.execute(query)
            user = result.scalar_one_or_none()
            return user

    @classmethod
    async def get_users_by_role(cls, role_id: int):
        async with async_session() as session:
            query = select(User).filter_by(role_id=role_id)
            result = await session.execute(query)
            users = result.scalar_one_or_none()
            return users

    @classmethod
    async def get_user_by_id(cls, user_id: int):
        async with async_session() as session:
            query = select(User).options(joinedload(User.role)).filter_by(id=user_id)
            result = await session.execute(query)
            user = result.scalar_one_or_none()
            return user

    @classmethod
    async def get_user_by_role_id(cls, role_id: int):
        async with async_session() as session:
            query = select(User).filter_by(role_id=role_id)
            result = await session.execute(query)
            user = result.scalar_one_or_none()
            return user

    @classmethod
    async def update_user(cls, user_id: int, values: dict) -> bool:
        async with async_session() as session:
            # noinspection PyUnresolvedReferences
            schema = values.model_dump(exclude_unset=True)
            data = {k: v for k, v in schema.items() if v is not None}

            if not data:
                return False

            stmt = (
                update(User)
                .where(User.id == user_id)
                .values(**data)
                .returning(User.id)
            )
            await session.execute(stmt)
            await session.commit()
            return True

    @classmethod
    async def update_user_role(cls, user_id: int, role_id: int):
        async with async_session() as session:
            stmt = update(User).values(role_id=role_id).filter_by(id=user_id)
            await session.execute(stmt)
            await session.commit()

    @classmethod
    async def delete_user_imitation(cls, user_id: int):
        async with async_session() as session:
            stmt = update(User).values(is_active=False).filter_by(id=user_id)
            await session.execute(stmt)
            await session.commit()

    @classmethod
    async def delete_user(cls, user_id: int):
        async with async_session() as session:
            exists_user = await cls.get_user_by_id(user_id)
            if not exists_user:
                return False

            stmt = delete(User).filter_by(id=user_id)
            await session.execute(stmt)
            await session.commit()
            return True

class RoleRepository:
    @classmethod
    async def get_roles(cls):
        async with async_session() as session:
            query = select(Role)
            result = await session.execute(query)
            roles = result.scalars().all()
            return roles

    @classmethod
    async def get_role_by_id(cls, role_id: int):
        async with async_session() as session:
            query = select(Role).filter_by(id=role_id)
            result = await session.execute(query)
            role = result.scalar_one()
            return role

    @classmethod
    async def get_role_by_title(cls, title: str):
        async with async_session() as session:
            query = select(Role).filter_by(title=title)
            result = await session.execute(query)
            role = result.scalar_one_or_none()
            return role

    @classmethod
    async def create_role(cls, title: str):
        async with async_session() as session:
            stmt = insert(Role).values(title=title)
            result = await session.execute(stmt)
            await session.commit()
            role = result.one_or_none()
            return role

    @classmethod
    async def update_role(cls, role_id: int, title: str):
        async with async_session() as session:
            exists_role = await cls.get_role_by_id(role_id)
            if not exists_role:
                return False

            stmt = update(Role).values(title=title).filter_by(id=role_id)
            await session.execute(stmt)
            await session.commit()
            return True

    @classmethod
    async def delete_role(cls, role_id: int):
        async with async_session() as session:
            exists_role = await UserRepository.get_user_by_role_id(role_id)
            if exists_role:
                return False

            stmt = delete(Role).filter_by(id=role_id)
            await session.execute(stmt)
            await session.commit()
            return True