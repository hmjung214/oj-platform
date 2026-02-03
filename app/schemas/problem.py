from pydantic import BaseModel

class ProblemCreate(BaseModel):
    title: str
    description: str
    input_description: str | None = None
    output_description: str | None = None
    input_example: str | None = None
    output_example: str | None = None
    time_limit: int = 1
    memory_limit: int = 128

class ProblemOut(ProblemCreate):
    id: int

    class Config:
        orm_mode = True

