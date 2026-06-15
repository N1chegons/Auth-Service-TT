from fastapi import APIRouter, Depends, HTTPException
from starlette import status

from src.auth.models import User
from src.auth.utils import AuthSettings
from src.task.repository import TaskRepository
from src.task.schemas import TaskRead

router = APIRouter(
    prefix="/task",
    tags=["task"],
)

@router.get("/get_tasks", summary="Получение всех задач", response_model=list[TaskRead])
async def get_tasks(user: User = Depends(AuthSettings.current_user)):
    try:
        tasks = await TaskRepository.get_tasks(user)
        if not tasks:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Нету активных задач")

        return tasks

    except HTTPException as http_ex:
        raise http_ex

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Неизвестная ошибка {str(e)}")

