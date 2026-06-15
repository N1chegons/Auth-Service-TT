from sqlalchemy import select, update
from sqlalchemy.orm import selectinload, joinedload

from src.auth.models import User, Role
from src.database import async_session


class AdminRepository:
    @classmethod
    async def get_users(cls, user_status: bool = False):
        async with async_session() as session:
            query = (
                select(User)
                .options(selectinload(User.role))
                .filter_by(is_active=user_status)
                .where(User.role_id != 2)
                .order_by(User.registered_at.desc())
            )
            users = await session.execute(query)
            return users.scalars().all()

    @classmethod
    async def get_admin(cls, user_id: int):
        async with async_session() as session:
            query = select(User).filter_by(id=user_id, role_id=2, is_active=True)
            result = await session.execute(query)
            admin = result.scalars().all()
            return admin

    @classmethod
    async def get_admin_permissions(cls, user_id: int):
        async with async_session() as session:
            stmt = update(User).values(role_id=2).filter_by(id=user_id)
            await session.execute(stmt)
            await session.commit()
