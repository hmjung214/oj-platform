from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class SubmissionCreate(BaseModel):
    problem_id: int
    code: str
    language: str

class SubmissionOut(BaseModel):
    id: int
    problem_id: int
    code: str
    language: str
    result: str
    user_id: int
    stdout: Optional[str] = None
    stderr: Optional[str] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True
