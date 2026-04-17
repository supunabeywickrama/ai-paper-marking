"""
Marking Engine — orchestrates text and/or vision marking for a submission.
"""
import logging
from typing import Optional

from ..config import settings
from ..models.submission import (
    AnswerType,
    MarkingCriteria,
    MarkingResult,
    Submission,
)
from .text_marker import TextMarker
from .time_fairness import TimeFairnessService
from .vision_marker import VisionMarker

logger = logging.getLogger(__name__)


class MarkingEngine:
    """
    Orchestrates the full marking pipeline for a student submission.

    Supports three answer types:
    - TEXT   → evaluated with the language-model marker only
    - IMAGE  → evaluated with the vision-model marker only
    - MIXED  → both markers are run; the higher content score is used together
                with the vision presentation score and a blended average feedback
    """

    def __init__(
        self,
        text_marker: Optional[TextMarker] = None,
        vision_marker: Optional[VisionMarker] = None,
        time_service: Optional[TimeFairnessService] = None,
        passing_marks: float = settings.passing_marks,
    ) -> None:
        self._text_marker = text_marker or TextMarker()
        self._vision_marker = vision_marker or VisionMarker()
        self._time_service = time_service or TimeFairnessService()
        self._passing_marks = passing_marks

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def mark(self, submission: Submission, criteria: MarkingCriteria) -> MarkingResult:
        """
        Mark a submission and return a MarkingResult.

        Parameters
        ----------
        submission:
            The student's answer submission.
        criteria:
            The marking criteria and rubric for this question.
        """
        # Calculate time-based adjustment if a deadline is set
        time_adjustment = 0.0
        if criteria.deadline is not None:
            time_adjustment = self._time_service.calculate_adjustment(
                submitted_at=submission.submitted_at,
                deadline=criteria.deadline,
            )

        answer_type = submission.answer_type

        if answer_type == AnswerType.TEXT:
            breakdown, feedback, strengths, improvements = self._mark_text(
                submission, criteria, time_adjustment
            )
        elif answer_type == AnswerType.IMAGE:
            breakdown, feedback, strengths, improvements = self._mark_image(
                submission, criteria, time_adjustment
            )
        else:  # MIXED
            breakdown, feedback, strengths, improvements = self._mark_mixed(
                submission, criteria, time_adjustment
            )

        is_passing = breakdown.total_marks >= self._passing_marks

        return MarkingResult(
            student_id=submission.student_id,
            question_id=submission.question_id,
            exam_id=submission.exam_id,
            answer_type=answer_type,
            marks_breakdown=breakdown,
            feedback=feedback,
            strengths=strengths,
            improvements=improvements,
            submitted_at=submission.submitted_at,
            is_passing=is_passing,
        )

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _mark_text(self, submission: Submission, criteria: MarkingCriteria, time_adjustment: float):
        if not submission.answer_text:
            raise ValueError("TEXT submission must include answer_text.")
        return self._text_marker.mark(submission.answer_text, criteria, time_adjustment)

    def _mark_image(
        self, submission: Submission, criteria: MarkingCriteria, time_adjustment: float
    ):
        if not submission.answer_image_base64:
            raise ValueError("IMAGE submission must include answer_image_base64.")
        return self._vision_marker.mark(
            submission.answer_image_base64,
            criteria,
            supporting_text=submission.answer_text,
            time_adjustment=time_adjustment,
        )

    def _mark_mixed(
        self, submission: Submission, criteria: MarkingCriteria, time_adjustment: float
    ):
        """
        For mixed submissions, run both markers and combine:
        - Use the higher content_marks from the two markers
        - Combine feedback and strengths/improvements from both
        """
        results = []

        if submission.answer_text:
            results.append(
                self._text_marker.mark(submission.answer_text, criteria, time_adjustment=0.0)
            )

        if submission.answer_image_base64:
            results.append(
                self._vision_marker.mark(
                    submission.answer_image_base64,
                    criteria,
                    supporting_text=submission.answer_text,
                    time_adjustment=0.0,
                )
            )

        if not results:
            raise ValueError("MIXED submission must include at least one of answer_text or answer_image_base64.")

        # Combine: take the best content marks, average presentation marks
        best_content = max(r[0].content_marks for r in results)
        avg_presentation = sum(r[0].presentation_marks for r in results) / len(results)

        raw_total = min(best_content + avg_presentation, criteria.max_marks)
        total_marks = max(0.0, min(raw_total + time_adjustment, criteria.max_marks))
        percentage = round(total_marks / criteria.max_marks * 100, 2) if criteria.max_marks else 0.0

        from ..models.submission import MarkBreakdown

        breakdown = MarkBreakdown(
            content_marks=best_content,
            presentation_marks=avg_presentation,
            time_adjustment=time_adjustment,
            total_marks=total_marks,
            max_marks=criteria.max_marks,
            percentage=percentage,
        )

        # Combine feedback
        feedback_parts = [r[1] for r in results if r[1]]
        feedback = " | ".join(feedback_parts) if len(feedback_parts) > 1 else (feedback_parts[0] if feedback_parts else "")

        # Deduplicated strengths and improvements
        strengths: list[str] = []
        improvements: list[str] = []
        seen_s: set[str] = set()
        seen_i: set[str] = set()
        for _, _, s_list, i_list in results:
            for s in s_list:
                if s not in seen_s:
                    strengths.append(s)
                    seen_s.add(s)
            for i in i_list:
                if i not in seen_i:
                    improvements.append(i)
                    seen_i.add(i)

        return breakdown, feedback, strengths, improvements
