from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import desc
from uuid import UUID

from backend.database import get_db
from backend.models import Submission, Student
from backend.schemas import RankingResponse

router = APIRouter(prefix="/api/rankings", tags=["rankings"])

@router.get("/{exam_id}", response_model=list[RankingResponse])
async def get_exam_rankings(exam_id: UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Submission, Student)
        .join(Student, Submission.student_id == Student.id)
        .where(Submission.exam_id == exam_id)
        .where(Submission.processing_status == "COMPLETED")
        .order_by(desc(Submission.total_score))
    )
    
    rankings = []
    for sub, student in result.all():
        rankings.append(
            RankingResponse(
                id=sub.id, # Using submission id as ranking id for the response model
                exam_id=sub.exam_id,
                student_id=sub.student_id,
                submission_id=sub.id,
                total_score=sub.total_score or 0.0,
                rank=sub.rank or 0,
                status=sub.time_status
            )
        )
    return rankings
