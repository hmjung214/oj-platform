from sqlalchemy import Column, String, Integer, Boolean, DateTime, func
from datetime import datetime
import uuid

from app.db.base import Base

class Board(Base):
    __tablename__ = "boards"

    id = Column(String, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    category = Column(String(255), nullable=True)

    list_level = Column(Integer, nullable=False, default=1)
    view_level = Column(Integer, nullable=False, default=1)
    write_level = Column(Integer, nullable=False, default=1)
    reply_level = Column(Integer, nullable=False, default=1)
    comment_level = Column(Integer, nullable=False, default=1)
    link_level = Column(Integer, nullable=False, default=1)
    upload_level = Column(Integer, nullable=False, default=1)
    download_level = Column(Integer, nullable=False, default=1)
    html_level = Column(Integer, nullable=False, default=1)

    use_secret = Column(String(20), nullable=False, default="none")   # ex: "none", "always"
    use_dhtml = Column(Boolean, nullable=False, default=False)

    upload_count = Column(Integer, nullable=False, default=2)
    upload_size = Column(Integer, nullable=False, default=1048576)  # bytes

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
