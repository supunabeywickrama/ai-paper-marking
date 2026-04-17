from sqlalchemy import String, Integer, Float, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from datetime import datetime
import uuid
from typing import List, Optional, Dict, Any

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"
    
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    email: Mapped[str] = mapped_column(unique=True, index=True)
    password_hash: Mapped[str]
    role: Mapped[str] = mapped_column(default="STUDENT") # ADMIN | STUDENT
    name: Mapped[str]
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    
    submissions: Mapped[List["Submission"]] = relationship(back_populates="user")

class Exam(Base):
    __tablename__ = "exams"
    
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    title: Mapped[str]
    subject: Mapped[str]
    max_questions: Mapped[int] = mapped_column(default=10)
    deadline_time: Mapped[datetime]
    late_deadline: Mapped[datetime]
    marking_scheme_file_path: Mapped[Optional[str]]
    marking_scheme_parsed: Mapped[Optional[Dict[str, Any]]] = mapped_column(type_=JSON)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    
    submissions: Mapped[List["Submission"]] = relationship(back_populates="exam")
    rankings: Mapped[List["Ranking"]] = relationship(back_populates="exam")

class Student(Base):
    __tablename__ = "students"
    
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    name: Mapped[str]
    email: Mapped[str] = mapped_column(unique=True)
    student_id: Mapped[str] = mapped_column(unique=True, index=True)
    language_preference: Mapped[str]
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    
    submissions: Mapped[List["Submission"]] = relationship(back_populates="student")
    rankings: Mapped[List["Ranking"]] = relationship(back_populates="student")

class Submission(Base):
    __tablename__ = "submissions"
    
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    exam_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("exams.id"))
    student_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("students.id"))
    user_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("users.id"))
    file_path: Mapped[str]
    file_type: Mapped[str]
    submitted_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    time_status: Mapped[str] = mapped_column(default="ON_TIME") # ON_TIME | LATE_ACCEPTED | REJECTED
    processing_status: Mapped[str] = mapped_column(default="PENDING") # PENDING | PROCESSING | COMPLETED | FAILED
    total_score: Mapped[Optional[float]]
    text_score: Mapped[Optional[float]]
    visual_score: Mapped[Optional[float]]
    rank: Mapped[Optional[int]]
    processed_at: Mapped[Optional[datetime]]
    
    user: Mapped[Optional["User"]] = relationship(back_populates="submissions")
    exam: Mapped["Exam"] = relationship(back_populates="submissions")
    student: Mapped["Student"] = relationship(back_populates="submissions")
    extracted_contents: Mapped[List["ExtractedContent"]] = relationship(back_populates="submission")
    evaluations: Mapped[List["Evaluation"]] = relationship(back_populates="submission")
    generated_pdfs: Mapped[List["GeneratedPDF"]] = relationship(back_populates="submission")
    email_logs: Mapped[List["EmailLog"]] = relationship(back_populates="submission")
    ranking_record: Mapped[Optional["Ranking"]] = relationship(back_populates="submission")

class ExtractedContent(Base):
    __tablename__ = "extracted_content"
    
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    submission_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("submissions.id"))
    question_number: Mapped[int]
    question_part: Mapped[Optional[str]] # a | b | c | null
    content_type: Mapped[str] # TEXT | DIAGRAM | GRAPH | TABLE
    raw_extracted: Mapped[Optional[str]] = mapped_column(Text)
    reconstructed_text: Mapped[Optional[str]] = mapped_column(Text)
    detected_language: Mapped[Optional[str]] # si | ta | en
    image_path: Mapped[Optional[str]]
    visual_metadata: Mapped[Optional[Dict[str, Any]]] = mapped_column(type_=JSON)
    
    submission: Mapped["Submission"] = relationship(back_populates="extracted_contents")
    evaluation: Mapped[Optional["Evaluation"]] = relationship(back_populates="extracted_content")

class Evaluation(Base):
    __tablename__ = "evaluations"
    
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    content_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("extracted_content.id"))
    submission_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("submissions.id"))
    question_number: Mapped[int]
    marks_awarded: Mapped[float]
    max_marks: Mapped[float]
    feedback: Mapped[Optional[str]] = mapped_column(Text)
    correct_answer: Mapped[Optional[str]] = mapped_column(Text)
    evaluation_type: Mapped[str] # TEXT | VISUAL
    detailed_reasoning: Mapped[Optional[Dict[str, Any]]] = mapped_column(type_=JSON)
    
    extracted_content: Mapped["ExtractedContent"] = relationship(back_populates="evaluation")
    submission: Mapped["Submission"] = relationship(back_populates="evaluations")

class GeneratedPDF(Base):
    __tablename__ = "generated_pdfs"
    
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    submission_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("submissions.id"))
    pdf_type: Mapped[str] # ANNOTATED | CLEAN
    file_path: Mapped[str]
    generated_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    
    submission: Mapped["Submission"] = relationship(back_populates="generated_pdfs")

class EmailLog(Base):
    __tablename__ = "email_logs"
    
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    submission_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("submissions.id"))
    recipient_email: Mapped[str]
    status: Mapped[str] # SENT | FAILED
    sent_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    error_message: Mapped[Optional[str]] = mapped_column(Text)
    
    submission: Mapped["Submission"] = relationship(back_populates="email_logs")

class Ranking(Base):
    __tablename__ = "rankings"
    
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    exam_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("exams.id"))
    student_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("students.id"))
    submission_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("submissions.id"))
    total_score: Mapped[float]
    rank: Mapped[int]
    status: Mapped[str] # RANKED | LATE_NOT_RANKED
    
    exam: Mapped["Exam"] = relationship(back_populates="rankings")
    student: Mapped["Student"] = relationship(back_populates="rankings")
    submission: Mapped["Submission"] = relationship(back_populates="ranking_record")
