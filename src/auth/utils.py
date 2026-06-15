from datetime import timedelta, datetime
from fastapi import Request, HTTPException

import jwt
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer
from starlette import status

from src.auth.repository import UserRepository
from src.config import settings

class AuthSettings:
    SECRET_KEY = settings.JWT_SECRET
    ALGORITHM = "HS256"
    ATEM = 60
    security = HTTPBearer(auto_error=False)

    @classmethod
    def create_access_token(cls, data: dict, expires_delta: timedelta = None):
        to_encode = data.copy()
        # noinspection PyDeprecation
        expire = datetime.utcnow() + (expires_delta or timedelta(minutes=cls.ATEM))
        to_encode.update({"exp": expire})
        return jwt.encode(to_encode, cls.SECRET_KEY, algorithm=cls.ALGORITHM)

    @classmethod
    def set_cookie(cls, access_token):
        response = JSONResponse({"detail": "Вы успешно вошли в аккаунт"})
        response.set_cookie(
            key="access_token",
            value=access_token,
            httponly=True,
            max_age=3600,
            samesite="lax"
        )

        return response

    @classmethod
    async def current_user(cls, request: Request = Request):
        token = request.cookies.get("access_token")

        try:
            if not token:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Вы не авторизованы. Пожалуйста, войдите в систему"
               )

            payload = jwt.decode(token, cls.SECRET_KEY, algorithms=cls.ALGORITHM)
            user_id = payload.get("sub")

            user = await UserRepository.get_user_by_id(int(user_id))

            if not user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Вы не зарегестрированы. Пожалуйста, зарегестрируйтесь"
               )

            if not user.is_active:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Ваш аккаунт удален.")

            return user

        except jwt.InvalidTokenError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Сессия истекла. Войдите заново"
            )

    @classmethod
    async def admin_user(cls, request: Request = Request):
        cur_user = await cls.current_user(request)
        if cur_user.role.title != "admin":
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Доступ ограничен")

        return cur_user