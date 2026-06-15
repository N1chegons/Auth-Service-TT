import datetime

from fastapi import HTTPException
from sqlalchemy import insert, select, delete, update
from sqlalchemy.orm import selectinload
from starlette import status

from src.auth.models import Role, User
from src.database import async_session
from src.task.models import Task

class TaskRepository:
    @classmethod
    async def get_task(cls, task_id: int):
        async with async_session() as session:
            query = select(Task).options(selectinload(Task.view_role)).filter_by(id=task_id)
            result = await session.execute(query)
            tasks = result.first()
            return tasks

    @classmethod
    async def get_tasks(cls, user: User):
        async with async_session() as session:
            query = (
                select(
                    Task.id,
                    Task.title,
                    Task.description,
                    Role.title.label("view_role"),
                    Task.created_at,
                    Task.updated_at,
                )
                .join(Role, Role.id == Task.role_id)
                .order_by(Task.created_at.desc())
            )

            if user.role.title != "admin":
                query = query.where(Task.role_id == user.role_id)

            result = await session.execute(query)
            return result.mappings().all()

    @classmethod
    async def create_task(cls, values: dict, user_id: int,  role_id: int):
        async with async_session() as session:
            stmt = insert(Task).values(**values, created_by=user_id, role_id=role_id)
            await session.execute(stmt)
            await session.commit()

    @classmethod
    async def update_task(cls, task_id: int, role_id: int, values: dict):
        async with async_session() as session:
            exists_task = await cls.get_task(task_id)
            if not exists_task:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Задача с id {task_id} не найдена")

            # noinspection PyUnresolvedReferences
            schema = values.model_dump(exclude_unset=True, exclude={"view_role"})
            data = {k: v for k, v in schema.items() if v is not None}

            data["role_id"] = role_id

            # noinspection PyDeprecation
            date_now = datetime.datetime.utcnow()

            if not data:
                return False

            stmt = (
                update(Task)
                .where(Task.id == task_id)
                .values(**data, updated_at=date_now)
            )
            await session.execute(stmt)
            await session.commit()
            return True

    @classmethod
    async def delete_task(cls, task_id: int):
        async with async_session() as session:
            exists_task = await cls.get_task(task_id)
            if not exists_task:
                return False

            stmt = delete(Task).filter_by(id=task_id)
            await session.execute(stmt)
            await session.commit()
            return True