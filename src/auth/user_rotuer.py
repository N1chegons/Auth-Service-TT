from fastapi import APIRouter
from fastapi import Depends, HTTPException, status
from starlette.responses import JSONResponse

from src.admin.repository import AdminRepository
from src.auth.models import User
from src.auth.repository import UserRepository
from src.auth.schemas import UserRead, UserUpdate
from src.auth.utils import AuthSettings

router = APIRouter(
    prefix="/user",
    tags=["user"],
)

@router.get("/profile", response_model=UserRead, summary="Просмотр профиля пользовтеля")
async def get_current_user(user: User = Depends(AuthSettings.current_user)):

    try:
        user = await UserRepository.get_user_by_id(int(user.id))
        return user

    except HTTPException as http_ex:
        raise http_ex

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Неизвестная ошибка {str(e)}")

@router.patch("/update_info", summary="Обновленние данных пользователя")
async def update_info(update_schema: UserUpdate = Depends(), user: User = Depends(AuthSettings.current_user)):
    try:
        updated_user = await UserRepository.update_user(user.id, update_schema)
        if not updated_user:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Поля не заполнены, нету данных для обновления")

        return {"status": 200, "detail": "Данные успешно обновлены"}

    except HTTPException as http_ex:
        raise http_ex

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Неизвестная ошибка: {str(e)}")

@router.put("/admin_permissions", summary="Получение прав администратора")
async def admin_permissions(user: User = Depends(AuthSettings.current_user)):
    try:
        if user.role_id == 2:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Вы уже являетесь администратором")

        await AdminRepository.get_admin_permissions(user.id)
        return {"detail": "Права администратора успешно получены."}

    except HTTPException as http_ex:
        raise http_ex

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Неизвестная ошибка {str(e)}")

@router.delete("/dlete_account", summary="Удаление аккаунта")
async def delete_user_imitation(user: User = Depends(AuthSettings.current_user)):
    await UserRepository.delete_user_imitation(user.id)

    response = JSONResponse({"detail": f"Вы удалили аккаунт"})
    response.delete_cookie("access_token")

    return response
