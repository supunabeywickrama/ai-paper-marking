from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func

from backend.database import get_db
from backend.models import Submission
from backend.schemas import DashboardStats

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])

@router.get("/stats", response_model=DashboardStats)
async def get_dashboard_stats(db: AsyncSession = Depends(get_db)):
    # Total submissions
    total_res = await db.execute(select(func.count(Submission.id)))
    total_submissions = total_res.scalar() or 0
    
    # Average score
    avg_res = await db.execute(select(func.avg(Submission.total_score)).where(Submission.processing_status == "COMPLETED"))
    avg_score = avg_res.scalar() or 0.0
    
    # Status counts
    pending_res = await db.execute(select(func.count(Submission.id)).where(Submission.processing_status == "PENDING"))
    pending_count = pending_res.scalar() or 0
    
    completed_res = await db.execute(select(func.count(Submission.id)).where(Submission.processing_status == "COMPLETED"))
    completed_count = completed_res.scalar() or 0
    
    # Time status counts
    on_time_res = await db.execute(select(func.count(Submission.id)).where(Submission.time_status == "ON_TIME"))
    on_time_count = on_time_res.scalar() or 0
    
    late_res = await db.execute(select(func.count(Submission.id)).where(Submission.time_status == "LATE_ACCEPTED"))
    late_count = late_res.scalar() or 0
    
    rejected_res = await db.execute(select(func.count(Submission.id)).where(Submission.time_status == "REJECTED"))
    rejected_count = rejected_res.scalar() or 0
    
    return DashboardStats(
        total_submissions=total_submissions,
        avg_score=round(avg_score, 2),
        pending_count=pending_count,
        completed_count=completed_count,
        on_time_count=on_time_count,
        late_count=late_count,
        rejected_count=rejected_count
    )
