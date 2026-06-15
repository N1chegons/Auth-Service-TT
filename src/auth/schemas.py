import datetime
from typing import Optional, List

from fastapi import HTTPException
from pydantic import BaseModel, field_validator, EmailStr, Field
from starlette import status

class RoleRead(BaseModel):
    id: int
    title: str

class RoleReadForTask(BaseModel):
    title: str

class UserCreate(BaseModel):
    name: str
    surname: str
    patronymic: Optional[str] = None
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=60)
    password_conf: str = Field(..., min_length=8, max_length=60)

    @field_validator('password_conf')
    @classmethod
    def passwords_match(cls, val, info):
        if 'password' in info.data and val != info.data['password']:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Пароли не совподают")
        return val

    @field_validator('patronymic')
    @classmethod
    def patronymic_new(cls, val):
        if val is None:
            return ""

class UserRead(BaseModel):
    id: int
    name: str
    surname: str
    patronymic: str
    email: EmailStr
    registered_at: datetime.datetime

    @field_validator('registered_at')
    @classmethod
    def custom(cls, val):
        return datetime.datetime.strftime(val, "%m.%d.%Y %H:%M")

class UserReadForAdmin(UserRead):
    role: RoleRead
    is_active: bool

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserUpdate(BaseModel):
    name: str | None = None
    surname: str | None = None
    patronymic: str | None = None
    email: EmailStr | None = None
