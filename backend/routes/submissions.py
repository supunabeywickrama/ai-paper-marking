from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from uuid import UUID

from backend.database import get_db
from backend.models import Submission, Evaluation, ExtractedContent, GeneratedPDF
from backend.schemas import SubmissionResponse, EvaluationResponse, GeneratedPDFResponse

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

@router.get("/{submission_id}/evaluations", response_model=list[EvaluationResponse])
async def get_submission_evaluations(submission_id: UUID, db: AsyncSession = Depends(get_db)):
    sub_res = await db.execute(select(Submission).where(Submission.id == submission_id))
    if not sub_res.scalars().first():
        raise HTTPException(status_code=404, detail="Submission not found")

    result = await db.execute(
        select(Evaluation, ExtractedContent)
        .join(ExtractedContent, Evaluation.content_id == ExtractedContent.id)
        .where(Evaluation.submission_id == submission_id)
        .order_by(Evaluation.question_number)
    )

    evaluations = []
    for evaluation, content in result.all():
        evaluations.append(EvaluationResponse(
            id=evaluation.id,
            question_number=evaluation.question_number,
            question_part=content.question_part,
            marks_awarded=evaluation.marks_awarded,
            max_marks=evaluation.max_marks,
            feedback=evaluation.feedback,
            correct_answer=evaluation.correct_answer,
            evaluation_type=evaluation.evaluation_type,
            detailed_reasoning=evaluation.detailed_reasoning
        ))
    return evaluations

@router.get("/{submission_id}/pdfs", response_model=list[GeneratedPDFResponse])
async def get_submission_pdfs(submission_id: UUID, db: AsyncSession = Depends(get_db)):
    sub_res = await db.execute(select(Submission).where(Submission.id == submission_id))
    if not sub_res.scalars().first():
        raise HTTPException(status_code=404, detail="Submission not found")

    result = await db.execute(
        select(GeneratedPDF).where(GeneratedPDF.submission_id == submission_id)
    )
    return result.scalars().all()
