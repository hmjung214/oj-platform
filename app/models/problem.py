from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.orm import relationship
from app.models.base import Base

class Problem(Base):
    __tablename__ = "problems"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(100), nullable=False)
    description = Column(Text, nullable=False)
    input_description = Column(Text, nullable=True)
    output_description = Column(Text, nullable=True)
    input_example = Column(Text)
    output_example = Column(Text)
    time_limit = Column(Integer, default=1)
    memory_limit = Column(Integer, default=128)

    submissions = relationship(
        "Submission",
        back_populates="problem",
        cascade="all, delete"
    )
