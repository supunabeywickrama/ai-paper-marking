"""
Data models for the AI Paper Marking System.
"""
from datetime import datetime, timezone
from enum import Enum
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class AnswerType(str, Enum):
    """Type of student answer."""

    TEXT = "text"
    IMAGE = "image"
    MIXED = "mixed"  # both text and image


class Submission(BaseModel):
    """A student's answer submission."""

    student_id: str = Field(..., description="Unique identifier for the student")
    question_id: str = Field(..., description="Unique identifier for the question")
    answer_text: Optional[str] = Field(None, description="Textual answer from the student")
    answer_image_base64: Optional[str] = Field(
        None, description="Base64-encoded image of the student's visual answer"
    )
    answer_type: AnswerType = Field(AnswerType.TEXT, description="Type of answer provided")
    submitted_at: datetime = Field(
        default_factory=_utcnow, description="UTC timestamp when the answer was submitted"
    )
    exam_id: Optional[str] = Field(None, description="Exam this submission belongs to")


class MarkingCriteria(BaseModel):
    """Criteria used to mark a question."""

    model_config = ConfigDict(protected_namespaces=())

    question_id: str = Field(..., description="Question identifier")
    question_text: str = Field(..., description="The question text")
    model_answer: Optional[str] = Field(None, description="Model/expected answer for reference")
    max_marks: float = Field(..., description="Maximum marks available for the question")
    marking_rubric: Optional[str] = Field(
        None, description="Detailed rubric describing how marks should be awarded"
    )
    deadline: Optional[datetime] = Field(
        None, description="Submission deadline for time-fairness enforcement"
    )


class MarkBreakdown(BaseModel):
    """Breakdown of marks awarded."""

    content_marks: float = Field(..., description="Marks awarded for answer content")
    presentation_marks: float = Field(0.0, description="Marks for presentation/clarity")
    time_adjustment: float = Field(0.0, description="Adjustment applied for early/late submission")
    total_marks: float = Field(..., description="Total marks after all adjustments")
    max_marks: float = Field(..., description="Maximum achievable marks")
    percentage: float = Field(..., description="Percentage score")


class MarkingResult(BaseModel):
    """The result of marking a student's submission."""

    student_id: str
    question_id: str
    exam_id: Optional[str] = None
    answer_type: AnswerType
    marks_breakdown: MarkBreakdown
    feedback: str = Field(..., description="Detailed AI-generated feedback")
    strengths: list[str] = Field(default_factory=list, description="Identified strengths")
    improvements: list[str] = Field(default_factory=list, description="Areas for improvement")
    marked_at: datetime = Field(default_factory=_utcnow)
    submitted_at: datetime
    is_passing: bool = Field(..., description="Whether the student passed")


class RankingEntry(BaseModel):
    """A single entry in the exam ranking."""

    rank: int = Field(..., description="Student's rank (1 = highest)")
    student_id: str
    exam_id: str
    total_marks: float
    percentage: float
    submission_time: datetime = Field(..., description="When the student submitted")
    time_rank: int = Field(..., description="Rank based purely on submission time")
    is_passing: bool


class ExamRanking(BaseModel):
    """Complete ranking for an exam."""

    exam_id: str
    generated_at: datetime = Field(default_factory=_utcnow)
    total_students: int
    passing_students: int
    average_marks: float
    highest_marks: float
    lowest_marks: float
    rankings: list[RankingEntry]
