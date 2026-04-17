from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from uuid import UUID
import os

from backend.database import get_db
from backend.models import Exam
from backend.schemas import ExamResponse
from backend.services.marking_scheme_parser import parse_marking_scheme_pdf
from backend.config import settings

router = APIRouter(prefix="/api/exams", tags=["exams"])

@router.post("", response_model=ExamResponse)
async def create_exam(
    title: str = Form(...),
    subject: str = Form(...),
    max_questions: int = Form(10),
    deadline_time: str = Form(...),
    late_deadline: str = Form(...),
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db)
):
    from datetime import datetime
    
    dt_deadline = datetime.fromisoformat(deadline_time.replace('Z', '+00:00'))
    dt_late = datetime.fromisoformat(late_deadline.replace('Z', '+00:00'))
    
    new_exam = Exam(
        title=title,
        subject=subject,
        max_questions=max_questions,
        deadline_time=dt_deadline,
        late_deadline=dt_late
    )
    db.add(new_exam)
    await db.flush()
    
    # Save the file
    upload_dir = os.path.join(settings.upload_dir, "marking_schemes")
    os.makedirs(upload_dir, exist_ok=True)
    file_path = os.path.join(upload_dir, f"{new_exam.id}.pdf")
    
    with open(file_path, "wb") as buffer:
        content = await file.read()
        buffer.write(content)
        
    new_exam.marking_scheme_file_path = file_path
    
    # Parse marking scheme
    try:
        parsed_data = await parse_marking_scheme_pdf(file_path)
        new_exam.marking_scheme_parsed = parsed_data
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Error parsing marking scheme: {str(e)}")
        
    await db.commit()
    await db.refresh(new_exam)
    return new_exam

@router.get("", response_model=list[ExamResponse])
async def get_exams(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Exam).offset(skip).limit(limit))
    return result.scalars().all()

@router.get("/{exam_id}", response_model=ExamResponse)
async def get_exam(exam_id: UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Exam).where(Exam.id == exam_id))
    exam = result.scalars().first()
    if not exam:
        raise HTTPException(status_code=404, detail="Exam not found")
    return exam
