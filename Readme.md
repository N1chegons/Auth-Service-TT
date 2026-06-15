# Test task for 'effective-mobile'

Тестовое задание для 'effective-mobile'. Сервис регисрации и авторизации пользователя без использования стороних библиотек.

## Технологии
![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104-009688?logo=fastapi)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-17-336791?logo=postgresql)
![Docker](https://img.shields.io/badge/Docker-24.0-2496ED?logo=docker)
![Docker Compose](https://img.shields.io/badge/Docker_Compose-2.21-2496ED)

## О сервисе
## О сервисе

### Рабочие аспекты

Сервис реализован на **FastAPI** с использованием **JWT-токенов** и **HttpOnly cookies** для аутентификации. Пароли хэшируются с помощью **bcrypt**. Реализована собственная система аутентификации и авторизации (без FastAPI Users и т.п.). JWT-токен создаётся на основе `user_id`, подписывается секретным ключом и передаётся в `HttpOnly cookie` (защита от XSS). Время жизни токена — 60 минут. При последующих запросах токен извлекается из cookie, расшифровывается, идентифицируется пользователь. Также в проекте уже созданны некторые данные в таблице для минимального примера работы сервиса.  


### Структура управлениями ограничениями доступа
```flowchart TD
    Start[Запрос к API] --> GetCookie{Есть cookie\naccess_token?}
    GetCookie -->|Нет| 401[401 Unauthorized]
    GetCookie -->|Да| Decode[JWT decode + проверка подписи]
    
    Decode --> Valid{Токен валиден?}
    Valid -->|Нет| 401
    Valid -->|Да| GetUser[Запрос user из БД + role]
    
    GetUser --> Active{user.is_active?}
    Active -->|Нет| 403[403 Forbidden\nАккаунт деактивирован]
    Active -->|Да| CheckRole{Проверка прав доступа}
    
    CheckRole -->|admin| Allow[200 OK\nПолный доступ]
    CheckRole -->|manager| ManagerCheck{Ресурс\nдоступен менеджеру?}
    CheckRole -->|user| UserCheck{Ресурс\nдоступен пользователю?}
    
    ManagerCheck -->|Да| Allow
    ManagerCheck -->|Нет| 403
    UserCheck -->|Да| Allow
    UserCheck -->|Нет| 403
   ```


## Быстрый старт
### Установка и запуск

### 1. Клонируйте репозиторий
```bash
git clone https://github.com/N1chegons/Auth-Service-TT.git
cd Auth-Service-TT
```

### 2. Создайте файл окружения
.env (на основе файла .env.example)

<details>
    <summary>Структура .env.example</summary>    

    DB_HOST=db_host
    DB_PORT=5432
    DB_NAME=db_name
    DB_USER=db_user
    DB_PASS=db_pass
    
    JWT_SECRET=your_jwt_secret_key

</details>

### 3. Запустите приложение
```bash
docker-compose up --build
```

### 4. Откройте в браузере
-  Документация: http://localhost:5050/docs
-  ReDoc: http://localhost:5050/redoc

## Реализованные ручки API

### Аутентификация (`/auth`)

| Метод | Эндпоинт | Описание |
|-------|----------|----------|
| POST | `/auth/register` | Регистрация (имя, фамилия, отчество, email, пароль) |
| POST | `/auth/login` | Вход (email, пароль) → установка JWT в cookie |
| POST | `/auth/logout` | Выход (удаление cookie) |

### Пользователь (`/user`)

| Метод | Эндпоинт | Описание | Доступ |
|-------|----------|----------|--------|
| GET | `/user/profile` | Просмотр профиля | авторизованный пользователь |
| PATCH | `/user/update_info` | Обновление данных | авторизованный пользователь |
| PUT | `/user/admin_permissions` | Получение прав администратора | авторизованный пользователь |
| DELETE | `/user/dlete_account` | Мягкое удаление аккаунта | авторизованный пользователь |

### Задачи (`/task`)

| Метод | Эндпоинт | Описание | Доступ |
|-------|----------|----------|--------|
| GET | `/task/get_tasks` | Получение списка задач | авторизованный пользователь |

### Администрирование (`/admin`)

| Метод | Эндпоинт | Описание |
|-------|----------|----------|
| GET | `/admin/get_users/{active}` | Список активных/неактивных пользователей |
| GET | `/admin/get_users_by_role/{role_title}` | Список пользователей по роли |
| GET | `/admin/get_roles` | Список всех ролей |
| POST | `/admin/create_role` | Создание новой роли |
| POST | `/admin/create_task` | Создание задачи |
| PUT | `/admin/update_user_role/{user_id}` | Изменение роли пользователя |
| PUT | `/admin/update_role/{role_id}` | Изменение названия роли |
| PATCH | `/admin/update_task/{task_id}` | Обновление задачи |
| DELETE | `/admin/delete_user/{user_id}` | Полное удаление пользователя |
| DELETE | `/admin/delete_role/{role_id}` | Удаление роли (если не занята) |
| DELETE | `/admin/delete_task/{task_id}` | Удаление задачи |