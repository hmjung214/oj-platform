from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime
from datetime import datetime
from app.db.base import Base

class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, index=True)
    board_id = Column(String, ForeignKey("boards.id"))
    course_id = Column(String)
    category = Column(String)
    title = Column(String)
    content = Column(Text)
    user_id = Column(String)
    username = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
