from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete

from app.db.session import get_db
from app.models.problem import Problem
from app.schemas.problem import ProblemCreate, ProblemOut
from app.deps.user import get_admin_user

router = APIRouter(prefix="/problem", tags=["problem"])

@router.post("/", response_model=ProblemOut)
async def create_problem(
    problem: ProblemCreate,
    db: AsyncSession = Depends(get_db),
    admin=Depends(get_admin_user)
):
    new_problem = Problem(**problem.dict())
    db.add(new_problem)
    await db.commit()
    await db.refresh(new_problem)
    return new_problem

@router.get("/", response_model=list[ProblemOut])
async def list_problems(db: AsyncSession = Depends(get_db)):
    result = await db.execute(Problem.__table__.select())
    return result.mappings().all()

@router.get("/{problem_id}", response_model=ProblemOut)
async def get_problem(problem_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Problem).where(Problem.id == problem_id))
    problem = result.scalar_one_or_none()
    if not problem:
        raise HTTPException(status_code=404, detail="Problem not found")
    return problem

@router.put("/{problem_id}", response_model=ProblemOut)
async def update_problem(
    problem_id: int,
    updated: ProblemCreate,
    db: AsyncSession = Depends(get_db),
    admin=Depends(get_admin_user)
):
    result = await db.execute(select(Problem).where(Problem.id == problem_id))
    existing = result.scalar_one_or_none()

    if not existing:
        raise HTTPException(status_code=404, detail="Problem not found")

    for key, value in updated.dict().items():
        setattr(existing, key, value)

    await db.commit()
    await db.refresh(existing)
    return existing

@router.delete("/{problem_id}")
async def delete_problem(
    problem_id: int,
    db: AsyncSession = Depends(get_db),
    admin=Depends(get_admin_user)
):
    result = await db.execute(select(Problem).where(Problem.id == problem_id))
    problem = result.scalar_one_or_none()

    if not problem:
        raise HTTPException(status_code=404, detail="Problem not found")

    await db.delete(problem)
    await db.commit()
    return {"message": "Problem deleted"}
