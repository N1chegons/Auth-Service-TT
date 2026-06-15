from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from starlette import status

from src.admin.repository import AdminRepository
from src.auth.models import User
from src.auth.repository import RoleRepository, UserRepository
from src.auth.schemas import UserReadForAdmin
from src.auth.utils import AuthSettings
from src.task.repository import TaskRepository
from src.task.schemas import TaskCreate, TaskUpdate

router = APIRouter(
    prefix="/admin",
    tags=["admin"],
)


@router.get("/get_users/{active}", summary="Получение списка активных/неактивных пользователей", response_model=list[UserReadForAdmin])
async def get_users(active: bool, admin: User = Depends(AuthSettings.admin_user)):
    """
    True - активные\n
    False - неактивные
    """
    try:
        users = await AdminRepository.get_users(active)
        if not users:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Список пользователей пуст")

        return users

    except HTTPException as http_ex:
        raise http_ex

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Неизвестная ошибка {str(e)}")

@router.get("/get_users_by_role/{role_title}", summary="Получение списка пользователей по роли", response_model=list[UserReadForAdmin])
async def get_users_by_title(role_title: str, admin: User = Depends(AuthSettings.admin_user)):
    try:
        role = await RoleRepository.get_role_by_title(role_title)
        if not role:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Роль <{role_title}> не найдена")

        users = await UserRepository.get_user_by_role_id(role.id)
        if not users:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Список пользователей с ролью <{role_title}> пуст")

        return users

    except HTTPException as http_ex:
        raise http_ex

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Неизвестная ошибка {str(e)}")

@router.get("/get_roles", summary="Получение всех доступных ролей")
async def get_roles(admin: User = Depends(AuthSettings.admin_user)):
    try:
        roles_list = await RoleRepository.get_roles()
        if not roles_list:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Доступных ролей не найдено")

        return roles_list

    except HTTPException as http_ex:
        raise http_ex

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Неизвестная ошибка {str(e)}")

@router.post("/create_role", summary="Создание роли")
async def create_role(role_title: str, admin: User = Depends(AuthSettings.admin_user)):
    try:

        await RoleRepository.create_role(role_title)
        return {"detail": f"Новая роль <{role_title}> создана"}

    except IntegrityError:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Такая роль уже существует")

    except HTTPException as http_ex:
        raise http_ex

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Неизвестная ошибка {str(e)}")

@router.post("/create_task", summary="Создание задачи")
async def create_task(task_schema: TaskCreate = Depends(), admin: User = Depends(AuthSettings.admin_user)):
    try:
        exists_role = await RoleRepository.get_role_by_title(task_schema.view_role)
        if not exists_role:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Роль <{task_schema.view_role} не найдена")

        schema = task_schema.model_dump(exclude={"view_role"})
        await TaskRepository.create_task(schema, admin.id, exists_role.id)
        return {"detail": "Задача успешно создана"}

    except IntegrityError:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Такая роль уже существует")

    except HTTPException as http_ex:
        raise http_ex

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Неизвестная ошибка {str(e)}")

@router.put("/update_user_role/{user_id}", summary="Изменение роли пользователя")
async def update_user_role(user_id: int, role_title: str, user: User = Depends(AuthSettings.admin_user)):
    try:
        if user_id == user.id:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Вы не можете изменить роль сами себе")

        role = await RoleRepository.get_role_by_title(role_title)
        if not role:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Роль <{role_title}> не найдена")

        await UserRepository.update_user_role(user_id, role.id)
        return {"details": f"Вы успешно сменили роль пользователю {user_id} на {role_title}"}

    except HTTPException as http_ex:
        raise http_ex

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Неизвестная ошибка {str(e)}")

@router.put("/update_role/{role_id}", summary="Обновление существующей роли")
async def update_role(role_id: int, new_title: str, user: User = Depends(AuthSettings.admin_user)):
    try:

        updated_role = await RoleRepository.update_role(role_id, new_title)
        if not updated_role:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Роль с id {role_id} не найдена")

        return {"detail": f"Роль с id {role_id} успешно изменена на {new_title}"}

    except HTTPException as http_ex:
        raise http_ex

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Неизвестная ошибка {str(e)}")

@router.patch("/update_task/{task_id}", summary="Обновление задачи")
async def update_task(task_id: int, task_update_schema: TaskUpdate = Depends(), user: User = Depends(AuthSettings.admin_user)):
    try:
        exists_role = await RoleRepository.get_role_by_title(task_update_schema.view_role)
        if not exists_role:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Роль <{task_update_schema.view_role}> не найдена")

        updated_role = await TaskRepository.update_task(task_id, exists_role.id, task_update_schema)
        if not updated_role:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Все поля пустые, нету данных для обновления")

        return {"detail": f"Задача с id {task_id} успешно изменена"}

    except HTTPException as http_ex:
        raise http_ex

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Неизвестная ошибка {str(e)}")


@router.delete("/delete_user/{user_id}", summary="Полное удаления пользователя")
async def delete_user(user_id: int, admin: User = Depends(AuthSettings.admin_user)):
    try:
        exists_admin = await AdminRepository.get_admin(user_id)
        if exists_admin:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Вы не можете удалить другого администратора")

        if user_id == admin.id:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Вы не можете удалить сами себя")

        deleted_user = await UserRepository.delete_user(user_id)
        if not deleted_user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Пользователя с id {user_id} не найден")

        return {"detail": f"Вы успешно удалили пользователя с id {user_id}"}

    except HTTPException as http_ex:
        raise http_ex

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Неизвестная ошибка {str(e)}")

@router.delete("/delete_role/{role_id}", summary="Удаление незанятой роли")
async def delete_role(role_id: int, admin: User = Depends(AuthSettings.admin_user)):
    try:
        deleted_role = await RoleRepository.delete_role(role_id)
        if not deleted_role:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Вы не можете удалить роль так как она уже кому-то принадлежит")

        return {"detail": f"Вы успешно удалили роль с id {role_id}"}

    except HTTPException as http_ex:
        raise http_ex

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Неизвестная ошибка {str(e)}")

@router.delete("/delete_task/{task_id}", summary="Удаление задачи")
async def delete_task(task_id: int, admin: User = Depends(AuthSettings.admin_user)):
    try:
        deleted_task = await TaskRepository.delete_task(task_id)
        if not deleted_task:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail=f"Задача с id {task_id} не найдена")

        return {"detail": f"Вы успешно удалили задачу с id {task_id}"}

    except HTTPException as http_ex:
        raise http_ex

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Неизвестная ошибка {str(e)}")



