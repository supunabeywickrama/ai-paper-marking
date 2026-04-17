from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from uuid import UUID

from backend.database import get_db
from backend.models import Submission
from backend.schemas import SubmissionResponse

router = APIRouter(prefix="/api/submissions", tags=["submissions"])

@router.get("", response_model=list[SubmissionResponse])
async def get_all_submissions(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Submission).offset(skip).limit(limit))
    return result.scalars().all()

@router.get("/{submission_id}", response_model=SubmissionResponse)
async def get_submission(submission_id: UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Submission).where(Submission.id == submission_id))
    submission = result.scalars().first()
    if not submission:
        raise HTTPException(status_code=404, detail="Submission not found")
    return submission
