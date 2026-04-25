import os
from uuid import UUID
from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from backend.database import async_session_maker
from backend.models import Submission, Exam, Student, ExtractedContent, Evaluation, GeneratedPDF
from backend.services.vision_reader import extract_content_from_pages
from backend.services.text_rewriter import reconstruct_handwriting
from backend.services.evaluator import evaluate_text_answer
from backend.services.visual_evaluator import evaluate_visual_answer
from backend.services.annotation import create_annotated_pdf
from backend.services.pdf_generator import create_clean_pdf
from backend.services.email_service import send_results_email
from backend.services.ranking_service import update_rankings_for_exam

async def process_submission(submission_id: UUID):
    """
    Background task to orchestrate the entire marking pipeline.
    """
    async with async_session_maker() as db:
        result = await db.execute(select(Submission).where(Submission.id == submission_id))
        submission = result.scalars().first()
        if not submission:
            return

        try:
            submission.processing_status = "PROCESSING"
            await db.commit()

            exam_res = await db.execute(select(Exam).where(Exam.id == submission.exam_id))
            exam = exam_res.scalars().first()

            student_res = await db.execute(select(Student).where(Student.id == submission.student_id))
            student = student_res.scalars().first()

            # 1. Vision Reader — extract text and visuals from pages
            extracted_contents = await extract_content_from_pages(submission.file_path, exam)

            # Persist ExtractedContent rows so they get IDs before evaluation
            for content in extracted_contents:
                content.submission_id = submission.id
                db.add(content)
            await db.flush()

            # 2. Evaluation
            total_score = 0.0
            eval_dicts = []  # plain dicts passed to the annotation service

            for content in extracted_contents:
                matching_q = None
                for q in (exam.marking_scheme_parsed or {}).get("questions", []):
                    if (q["question_number"] == content.question_number
                            and q.get("question_part") == content.question_part):
                        matching_q = q
                        break

                if not matching_q:
                    continue

                max_marks = matching_q["max_marks"]
                model_answer = matching_q["model_answer"]

                if matching_q.get("answer_type", "TEXT") == "TEXT":
                    clean_text = await reconstruct_handwriting(content)
                    content.reconstructed_text = clean_text
                    eval_res = await evaluate_text_answer(
                        question=f"Q{content.question_number}{content.question_part or ''}",
                        model_answer=model_answer,
                        student_answer=clean_text,
                        max_marks=max_marks,
                        language=content.detected_language or "en"
                    )
                    eval_type = "TEXT"
                else:
                    visual_data = content.visual_metadata or {
                        "description": content.raw_extracted or ""
                    }
                    eval_res = await evaluate_visual_answer(
                        visual_type=content.content_type,
                        visual_data=visual_data,
                        model_answer=model_answer,
                        max_marks=max_marks
                    )
                    eval_type = "VISUAL"

                marks = eval_res.get("marks_awarded", 0)
                total_score += marks

                db.add(Evaluation(
                    content_id=content.id,
                    submission_id=submission.id,
                    question_number=content.question_number,
                    marks_awarded=marks,
                    max_marks=max_marks,
                    feedback=eval_res.get("feedback", ""),
                    correct_answer=eval_res.get("correct_answer"),
                    evaluation_type=eval_type,
                    detailed_reasoning=eval_res.get("detailed_reasoning")
                ))

                eval_dicts.append({
                    "question_number": content.question_number,
                    "question_part": content.question_part,
                    "marks": marks,
                    "feedback": eval_res.get("feedback", ""),
                    "max_marks": max_marks
                })

            submission.total_score = total_score
            submission.processing_status = "COMPLETED"
            submission.processed_at = datetime.now(timezone.utc)

            # 3. Document Generation — paths based on submission UUID avoid collisions
            upload_dir = os.path.dirname(submission.file_path)
            annotated_pdf_path = os.path.join(upload_dir, f"{submission.id}_annotated.pdf")
            clean_pdf_path = os.path.join(upload_dir, f"{submission.id}_clean.pdf")

            await create_annotated_pdf(submission.file_path, annotated_pdf_path, eval_dicts)
            await create_clean_pdf(clean_pdf_path, extracted_contents)

            db.add(GeneratedPDF(
                submission_id=submission.id,
                pdf_type="ANNOTATED",
                file_path=annotated_pdf_path
            ))
            db.add(GeneratedPDF(
                submission_id=submission.id,
                pdf_type="CLEAN",
                file_path=clean_pdf_path
            ))

            # 4. Email
            await send_results_email(
                student.email, student.name, exam.title, total_score, annotated_pdf_path
            )

            # 5. Rankings (ON_TIME only — logic is inside update_rankings_for_exam)
            await update_rankings_for_exam(exam.id, db)

            await db.commit()

        except Exception as e:
            submission.processing_status = "FAILED"
            print(f"Pipeline error for submission {submission_id}: {e}")
            await db.commit()
