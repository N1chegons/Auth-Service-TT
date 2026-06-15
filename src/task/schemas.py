import datetime
from typing import Optional

from pydantic import BaseModel, field_validator

class TaskCreate(BaseModel):
    title: str
    description: str | None = None
    view_role: str = "user"

class TaskUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    view_role: str | None = None

class TaskRead(BaseModel):
    id: int
    title: str
    description: str | None = None
    view_role: str
    created_at: datetime.datetime
    updated_at: Optional[datetime.datetime] = None

    @field_validator('created_at', 'updated_at')
    @classmethod
    def custom(cls, val):
        if val is None:
            return None
        return datetime.datetime.strftime(val, "%m.%d.%Y %H:%M")


