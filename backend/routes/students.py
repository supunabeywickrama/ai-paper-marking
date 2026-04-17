from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from uuid import UUID

from backend.database import get_db
from backend.models import Student
from backend.schemas import StudentCreate, StudentResponse

router = APIRouter(prefix="/api/students", tags=["students"])

@router.post("", response_model=StudentResponse)
async def create_student(student: StudentCreate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Student).where(Student.email == student.email))
    db_student = result.scalars().first()
    if db_student:
        raise HTTPException(status_code=400, detail="Email already registered")
        
    result = await db.execute(select(Student).where(Student.student_id == student.student_id))
    db_student = result.scalars().first()
    if db_student:
        raise HTTPException(status_code=400, detail="Student ID already registered")

    new_student = Student(**student.model_dump())
    db.add(new_student)
    await db.commit()
    await db.refresh(new_student)
    return new_student

@router.get("", response_model=list[StudentResponse])
async def get_students(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Student).offset(skip).limit(limit))
    return result.scalars().all()

@router.get("/{student_id}", response_model=StudentResponse)
async def get_student(student_id: UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Student).where(Student.id == student_id))
    student = result.scalars().first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    return student
