from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List

from app import models, schemas
from app.db.session import get_db
from app.deps.user import get_current_user, get_admin_user
from app.tasks.judge import judge_submission

router = APIRouter()


@router.post("/submission/", response_model=schemas.SubmissionOut)
async def create_submission(
    submission: schemas.SubmissionCreate,
    db: AsyncSession = Depends(get_db),
    user: models.User = Depends(get_current_user)
):
    db_submission = models.Submission(
        problem_id=submission.problem_id,
        code=submission.code,
        language=submission.language,
        result="Pending",
        user_id=user.id
    )
    db.add(db_submission)
    await db.commit()
    await db.refresh(db_submission)

    judge_submission.delay(db_submission.id)

    return db_submission


@router.get("/submission/mine", response_model=List[schemas.SubmissionOut])
async def get_my_submissions(
    db: AsyncSession = Depends(get_db),
    user: models.User = Depends(get_current_user)
):
    result = await db.execute(
        select(models.Submission).where(models.Submission.user_id == user.id)
    )
    return result.scalars().all()


@router.get("/submissions/all", response_model=List[schemas.SubmissionOut])
async def get_all_submissions(
    db: AsyncSession = Depends(get_db),
    user: models.User = Depends(get_admin_user)
):
    result = await db.execute(select(models.Submission))
    return result.scalars().all()

@router.get("/submission/latest", response_model=schemas.SubmissionOut)
async def get_latest_submission(
    problem_id: int = Query(...),
    db: AsyncSession = Depends(get_db),
    user: models.User = Depends(get_current_user)
):
    result = await db.execute(
        select(models.Submission)
        .where(
            models.Submission.user_id == user.id,
            models.Submission.problem_id == problem_id
        )
        .order_by(models.Submission.created_at.desc())
        .limit(1)
    )
    submission = result.scalars().first()
    if not submission:
        raise HTTPException(status_code=404, detail="최근 제출이 없습니다.")
    return submission


@router.get("/submission/{submission_id}", response_model=schemas.SubmissionOut)
async def get_submission(
    submission_id: int,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(models.Submission).where(models.Submission.id == submission_id)
    )
    submission = result.scalars().first()
    if not submission:
        raise HTTPException(status_code=404, detail="Submission not found")
    return submission
