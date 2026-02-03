from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class BoardCreate(BaseModel):
    name: str
    category: Optional[str] = None

    list_level: int
    view_level: int
    write_level: int
    reply_level: int
    comment_level: int
    link_level: int
    upload_level: int
    download_level: int
    html_level: int

    use_secret: str  # "none" | "always"
    use_dhtml: bool = False

    upload_count: int = 2
    upload_size: int = 1048576

class BoardOut(BaseModel):
    id: str
    name: str
    category: Optional[str] = None

    list_level: int
    view_level: int
    write_level: int
    reply_level: int
    comment_level: int
    link_level: int
    upload_level: int
    download_level: int
    html_level: int

    use_secret: str
    use_dhtml: bool
    upload_count: int
    upload_size: int

    created_at: datetime

    class Config:
        orm_mode = True

class BoardUpdate(BaseModel):
    name: Optional[str]
    category: Optional[str]
    list_level: Optional[int]
    view_level: Optional[int]
    write_level: Optional[int]
    reply_level: Optional[int]
    comment_level: Optional[int]
    link_level: Optional[int]
    upload_level: Optional[int]
    download_level: Optional[int]
    html_level: Optional[int]
    use_secret: Optional[str]
    use_dhtml: Optional[bool]
    upload_count: Optional[int]
    upload_size: Optional[int]

    class Config:
        orm_mode = True
