import bcrypt
from fastapi import APIRouter, HTTPException, Depends
from starlette import status
from starlette.responses import JSONResponse

from src.auth.models import User
from src.auth.repository import AuthRepository, UserRepository
from src.auth.schemas import UserCreate, UserLogin
from src.auth.utils import AuthSettings

router = APIRouter(
    prefix="/auth",
    tags=["auth"],
)

@router.post("/register", summary="Регистрация")
async def register(register_schema: UserCreate = Depends()):
    try:
        exist_user = await UserRepository.get_user(email=register_schema.email)
        if exist_user:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Вы уже зарегестрированы")

        schema = register_schema.model_dump(exclude={"password_conf", "password"})
        await AuthRepository.register(schema, register_schema.password)
        return {"detail": "Вы успешно зарегестрировались"}

    except HTTPException as http_ex:
        raise http_ex

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Неизвестная ошибка {str(e)}")

@router.post("/login", summary="Вход в аккаунт")
async def login(login_schema: UserLogin = Depends()):
    try:
        exist_user = await UserRepository.get_user(email=login_schema.email)

        if not exist_user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Неверный email или пароль")

        if not bcrypt.checkpw(login_schema.password.encode(), exist_user.password.encode()):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Неверный email или пароль")

        data = {'sub': str(exist_user.id)}
        access_token = AuthSettings.create_access_token(data=data)

        response = AuthSettings.set_cookie(access_token)
        return response

    except HTTPException as http_ex:
        raise http_ex

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Неизвестная ошибка {str(e)}")

@router.post("/logout", summary="Выход из аккаунта")
async def logout(user: User = Depends(AuthSettings.current_user)):
    response = JSONResponse({"detail": f"Вы вышли из аккаунта"})
    response.delete_cookie("access_token")

    return response

