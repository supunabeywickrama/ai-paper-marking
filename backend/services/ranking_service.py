from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import desc
from uuid import UUID

from backend.models import Submission

async def update_rankings_for_exam(exam_id: UUID, db: AsyncSession):
    """
    Recalculates the rankings for an exam.
    Assigns the rank property for each submission based on total_score.
    """
    result = await db.execute(
        select(Submission)
        .where(Submission.exam_id == exam_id)
        .where(Submission.processing_status == "COMPLETED")
        .order_by(desc(Submission.total_score))
    )
    submissions = result.scalars().all()
    
    current_rank = 1
    for index, sub in enumerate(submissions):
        if index > 0 and sub.total_score == submissions[index-1].total_score:
            sub.rank = submissions[index-1].rank
        else:
            sub.rank = current_rank
            
        current_rank += 1
        
    await db.commit()
