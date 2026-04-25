from pydantic import BaseModel, ConfigDict
from typing import List, Optional, Dict, Any
from datetime import datetime
from uuid import UUID

class ExamBase(BaseModel):
    title: str
    subject: str
    max_questions: int = 10
    deadline_time: datetime
    late_deadline: datetime

class ExamCreate(ExamBase):
    pass

class ExamResponse(ExamBase):
    id: UUID
    marking_scheme_file_path: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class SubmissionBase(BaseModel):
    exam_id: UUID
    student_id: UUID

class SubmissionCreate(SubmissionBase):
    pass

class SubmissionResponse(SubmissionBase):
    id: UUID
    file_path: str
    file_type: str
    submitted_at: datetime
    time_status: str
    processing_status: str
    total_score: Optional[float] = None
    rank: Optional[int] = None
    processed_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

class EvaluationResponse(BaseModel):
    id: UUID
    question_number: int
    question_part: Optional[str] = None
    marks_awarded: float
    max_marks: float
    feedback: Optional[str] = None
    correct_answer: Optional[str] = None
    evaluation_type: str
    detailed_reasoning: Optional[Dict[str, Any]] = None

    model_config = ConfigDict(from_attributes=True)

class GeneratedPDFResponse(BaseModel):
    id: UUID
    submission_id: UUID
    pdf_type: str
    file_path: str
    generated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class RankingResponse(BaseModel):
    id: UUID
    exam_id: UUID
    student_id: UUID
    submission_id: UUID
    total_score: float
    rank: int
    status: str

    model_config = ConfigDict(from_attributes=True)

class DashboardStats(BaseModel):
    total_submissions: int
    avg_score: float
    pending_count: int
    completed_count: int
    on_time_count: int
    late_count: int
    rejected_count: int

class StudentBase(BaseModel):
    name: str
    email: str
    student_id: str
    language_preference: str

class StudentCreate(StudentBase):
    pass

class StudentResponse(StudentBase):
    id: UUID
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
