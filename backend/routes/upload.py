from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from uuid import UUID
import os
from datetime import datetime, timezone

from backend.database import get_db
from backend.models import Submission, Exam, Student
from backend.schemas import SubmissionResponse
from backend.services.time_validator import validate_submission_time
from backend.config import settings

router = APIRouter(prefix="/api/upload", tags=["upload"])

async def mock_background_process(submission_id: UUID):
    # This will be replaced by the actual pipeline in Phase 7
    pass

@router.post("", response_model=SubmissionResponse)
async def upload_paper(
    background_tasks: BackgroundTasks,
    exam_id: UUID = Form(...),
    student_id: UUID = Form(...),
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db)
):
    # Verify exam exists
    exam_result = await db.execute(select(Exam).where(Exam.id == exam_id))
    exam = exam_result.scalars().first()
    if not exam:
        raise HTTPException(status_code=404, detail="Exam not found")
        
    # Verify student exists
    student_result = await db.execute(select(Student).where(Student.id == student_id))
    student = student_result.scalars().first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
        
    # Validate file type
    allowed_types = ["application/pdf", "image/png", "image/jpeg"]
    if file.content_type not in allowed_types:
        raise HTTPException(status_code=400, detail="Invalid file type")

    submitted_at = datetime.now(timezone.utc)
    time_status = validate_submission_time(submitted_at, exam)
    
    if time_status == "REJECTED":
        raise HTTPException(status_code=400, detail="Submission rejected: past the late deadline")

    new_submission = Submission(
        exam_id=exam_id,
        student_id=student_id,
        file_type=file.content_type,
        submitted_at=submitted_at,
        time_status=time_status,
        processing_status="PENDING",
        file_path="" # Temporary
    )
    db.add(new_submission)
    await db.flush()
    
    # Save the file
    upload_dir = os.path.join(settings.upload_dir, str(exam_id), str(new_submission.id))
    os.makedirs(upload_dir, exist_ok=True)
    file_extension = "pdf" if file.content_type == "application/pdf" else file.content_type.split("/")[1]
    file_path = os.path.join(upload_dir, f"original.{file_extension}")
    
    with open(file_path, "wb") as buffer:
        content = await file.read()
        buffer.write(content)
        
    new_submission.file_path = file_path
    await db.commit()
    await db.refresh(new_submission)
    
    # Trigger background pipeline
    background_tasks.add_task(mock_background_process, new_submission.id)
    
    return new_submission
