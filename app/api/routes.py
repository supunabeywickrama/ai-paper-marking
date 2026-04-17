"""
REST API routes for the AI Paper Marking System.
"""
import logging
from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from ..models.submission import (
    AnswerType,
    ExamRanking,
    MarkingCriteria,
    MarkingResult,
    Submission,
)
from ..services.marking_engine import MarkingEngine
from ..services.ranking_engine import RankingEngine

logger = logging.getLogger(__name__)

router = APIRouter()

# In-memory store (replace with a database in production)
_results_store: dict[str, list[MarkingResult]] = {}  # exam_id → results

_marking_engine = MarkingEngine()
_ranking_engine = RankingEngine()


# ------------------------------------------------------------------
# Request / Response schemas
# ------------------------------------------------------------------


class MarkRequest(BaseModel):
    """Request body for marking a submission."""

    submission: Submission
    criteria: MarkingCriteria


class MarkResponse(BaseModel):
    """Response after marking a submission."""

    result: MarkingResult
    time_status: Optional[str] = None


# ------------------------------------------------------------------
# Endpoints
# ------------------------------------------------------------------


@router.post("/mark", response_model=MarkResponse, summary="Mark a student submission")
def mark_submission(request: MarkRequest) -> MarkResponse:
    """
    Accept a student submission and marking criteria, then return
    AI-generated marks and feedback.

    Supports TEXT, IMAGE, and MIXED answer types.
    Time-based fairness is applied automatically when a deadline is specified
    in the marking criteria.
    """
    try:
        result = _marking_engine.mark(request.submission, request.criteria)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except Exception as exc:
        logger.exception("Marking failed for student %s", request.submission.student_id)
        raise HTTPException(status_code=500, detail="Marking service error.") from exc

    # Persist result for ranking
    exam_id = request.submission.exam_id or "default"
    _results_store.setdefault(exam_id, []).append(result)

    # Build time status string if deadline was provided
    time_status: Optional[str] = None
    if request.criteria.deadline is not None:
        from ..services.time_fairness import TimeFairnessService

        svc = TimeFairnessService()
        time_status = svc.submission_status(
            request.submission.submitted_at, request.criteria.deadline
        )

    return MarkResponse(result=result, time_status=time_status)


@router.get(
    "/rankings/{exam_id}",
    response_model=ExamRanking,
    summary="Get rankings for an exam",
)
def get_rankings(exam_id: str) -> ExamRanking:
    """
    Return an automated ranking for all submissions in the specified exam.

    Students are ranked by total marks (descending).  When marks are equal,
    the earlier submitter is ranked higher (time-based fairness tiebreaker).
    """
    results = _results_store.get(exam_id, [])
    return _ranking_engine.build_ranking(exam_id=exam_id, results=results)


@router.get(
    "/results/{exam_id}/{student_id}",
    response_model=list[MarkingResult],
    summary="Get marking results for a student",
)
def get_student_results(exam_id: str, student_id: str) -> list[MarkingResult]:
    """Return all marking results for a specific student in a specific exam."""
    results = _results_store.get(exam_id, [])
    student_results = [r for r in results if r.student_id == student_id]
    if not student_results:
        raise HTTPException(
            status_code=404,
            detail=f"No results found for student '{student_id}' in exam '{exam_id}'.",
        )
    return student_results


@router.delete(
    "/results/{exam_id}",
    summary="Clear all results for an exam (admin)",
)
def clear_exam_results(exam_id: str) -> dict:
    """Remove all stored results for an exam (useful for testing)."""
    _results_store.pop(exam_id, None)
    return {"message": f"Results for exam '{exam_id}' cleared."}
