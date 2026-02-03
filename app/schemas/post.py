from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class PostCreate(BaseModel):
    course_id: str
    category: str
    title: str
    content: str

class PostOut(BaseModel):
    id: int
    board_id: str
    course_id: str
    category: str
    title: str
    content: str
    user_id: str
    username: str
    created_at: datetime

    class Config:
        orm_mode = True
