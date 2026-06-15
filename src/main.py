from contextlib import asynccontextmanager

from fastapi import FastAPI

from migrations.seed_data import seed
from src.auth.router import router as auth_router
from src.auth.user_rotuer import router as user_router
from src.admin.router import router as admin_router
from src.task.router import router as task_router

# noinspection PyUnusedLocal
@asynccontextmanager
async def lifespan(_app: FastAPI):
    await seed()
    yield

app = FastAPI(
    lifespan=lifespan,
    title="Auth Service",
    summary="Сервис регистрации/авторизации",
)

app.include_router(user_router)
app.include_router(task_router)
app.include_router(admin_router)
app.include_router(auth_router)
