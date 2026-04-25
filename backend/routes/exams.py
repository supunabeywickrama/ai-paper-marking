from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from uuid import UUID
import os

from backend.database import get_db
from backend.models import Exam, Submission
from backend.schemas import ExamResponse, SubmissionResponse
from backend.services.marking_scheme_parser import parse_marking_scheme_pdf
from backend.services.ranking_service import update_rankings_for_exam
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

    upload_dir = os.path.join(settings.upload_dir, "marking_schemes")
    os.makedirs(upload_dir, exist_ok=True)
    file_path = os.path.join(upload_dir, f"{new_exam.id}.pdf")

    with open(file_path, "wb") as buffer:
        content = await file.read()
        buffer.write(content)

    new_exam.marking_scheme_file_path = file_path

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

@router.put("/{exam_id}", response_model=ExamResponse)
async def update_exam(
    exam_id: UUID,
    title: str = Form(None),
    subject: str = Form(None),
    max_questions: int = Form(None),
    deadline_time: str = Form(None),
    late_deadline: str = Form(None),
    db: AsyncSession = Depends(get_db)
):
    from datetime import datetime

    result = await db.execute(select(Exam).where(Exam.id == exam_id))
    exam = result.scalars().first()
    if not exam:
        raise HTTPException(status_code=404, detail="Exam not found")

    if title is not None:
        exam.title = title
    if subject is not None:
        exam.subject = subject
    if max_questions is not None:
        exam.max_questions = max_questions
    if deadline_time is not None:
        exam.deadline_time = datetime.fromisoformat(deadline_time.replace('Z', '+00:00'))
    if late_deadline is not None:
        exam.late_deadline = datetime.fromisoformat(late_deadline.replace('Z', '+00:00'))

    await db.commit()
    await db.refresh(exam)
    return exam

@router.delete("/{exam_id}", status_code=204)
async def delete_exam(exam_id: UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Exam).where(Exam.id == exam_id))
    exam = result.scalars().first()
    if not exam:
        raise HTTPException(status_code=404, detail="Exam not found")
    await db.delete(exam)
    await db.commit()

@router.post("/{exam_id}/generate-rankings")
async def generate_rankings(exam_id: UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Exam).where(Exam.id == exam_id))
    if not result.scalars().first():
        raise HTTPException(status_code=404, detail="Exam not found")
    await update_rankings_for_exam(exam_id, db)
    return {"message": "Rankings generated successfully"}

@router.get("/{exam_id}/submissions", response_model=list[SubmissionResponse])
async def get_exam_submissions(
    exam_id: UUID,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Exam).where(Exam.id == exam_id))
    if not result.scalars().first():
        raise HTTPException(status_code=404, detail="Exam not found")
    subs = await db.execute(
        select(Submission)
        .where(Submission.exam_id == exam_id)
        .offset(skip)
        .limit(limit)
    )
    return subs.scalars().all()
