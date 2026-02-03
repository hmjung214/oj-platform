from sqlalchemy import Column, Integer, Text, ForeignKey, String, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime

from app.models.base import Base

class Submission(Base):
    __tablename__ = "submissions"

    id = Column(Integer, primary_key=True, index=True)
    problem_id = Column(Integer, ForeignKey("problems.id", ondelete="CASCADE"), nullable=False)
    code = Column(Text, nullable=False)
    language = Column(String(20), default="python")
    result = Column(String(20), default="Pending")
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    stdout = Column(Text)
    stderr = Column(Text)

    created_at = Column(DateTime, default=datetime.utcnow)

    problem = relationship("Problem", back_populates="submissions")
