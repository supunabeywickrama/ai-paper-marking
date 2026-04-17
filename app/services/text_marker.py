"""
Text Marker Service — uses an LLM to evaluate textual student answers.
"""
import json
import logging
from typing import Optional

from openai import OpenAI

from ..config import settings
from ..models.submission import MarkBreakdown, MarkingCriteria

logger = logging.getLogger(__name__)


class TextMarker:
    """Evaluates textual student answers using a large language model."""

    def __init__(self, client: Optional[OpenAI] = None) -> None:
        self._client = client or OpenAI(api_key=settings.openai_api_key)

    def mark(
        self,
        answer_text: str,
        criteria: MarkingCriteria,
        time_adjustment: float = 0.0,
    ) -> tuple[MarkBreakdown, str, list[str], list[str]]:
        """
        Mark a textual answer against the given criteria.

        Returns
        -------
        tuple of (MarkBreakdown, feedback_str, strengths_list, improvements_list)
        """
        system_prompt = self._build_system_prompt(criteria)
        user_prompt = self._build_user_prompt(answer_text, criteria)

        response = self._client.chat.completions.create(
            model=settings.openai_model_text,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            response_format={"type": "json_object"},
            temperature=0.2,
        )

        raw = response.choices[0].message.content
        return self._parse_response(raw, criteria, time_adjustment)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _build_system_prompt(self, criteria: MarkingCriteria) -> str:
        rubric_section = (
            f"\n\nMarking Rubric:\n{criteria.marking_rubric}" if criteria.marking_rubric else ""
        )
        model_answer_section = (
            f"\n\nModel Answer:\n{criteria.model_answer}" if criteria.model_answer else ""
        )
        return (
            "You are an expert academic marker. Evaluate the student's answer objectively "
            "and return a JSON object with the following keys:\n"
            "  content_marks   (float) — marks for correctness and depth of answer content\n"
            "  presentation_marks (float) — marks for clarity, structure, and communication\n"
            "  feedback        (string) — overall constructive feedback\n"
            "  strengths       (array of strings) — specific things the student did well\n"
            "  improvements    (array of strings) — specific areas needing improvement\n\n"
            f"Question: {criteria.question_text}\n"
            f"Maximum marks: {criteria.max_marks}"
            f"{model_answer_section}"
            f"{rubric_section}"
        )

    @staticmethod
    def _build_user_prompt(answer_text: str, criteria: MarkingCriteria) -> str:
        return (
            f"Please mark the following student answer for the question: "
            f"'{criteria.question_text}'\n\n"
            f"Student Answer:\n{answer_text}\n\n"
            f"Award marks out of {criteria.max_marks}. "
            "Ensure content_marks + presentation_marks does not exceed the maximum."
        )

    @staticmethod
    def _parse_response(
        raw_json: str,
        criteria: MarkingCriteria,
        time_adjustment: float,
    ) -> tuple[MarkBreakdown, str, list[str], list[str]]:
        try:
            data = json.loads(raw_json)
        except json.JSONDecodeError:
            logger.error("Failed to parse LLM response as JSON: %s", raw_json)
            data = {}

        content_marks = min(float(data.get("content_marks", 0)), criteria.max_marks)
        presentation_marks = float(data.get("presentation_marks", 0))

        # Cap total raw marks to max before applying time adjustment
        raw_total = min(content_marks + presentation_marks, criteria.max_marks)
        total_marks = max(0.0, min(raw_total + time_adjustment, criteria.max_marks))
        percentage = round(total_marks / criteria.max_marks * 100, 2) if criteria.max_marks else 0.0

        breakdown = MarkBreakdown(
            content_marks=content_marks,
            presentation_marks=presentation_marks,
            time_adjustment=time_adjustment,
            total_marks=total_marks,
            max_marks=criteria.max_marks,
            percentage=percentage,
        )
        feedback = data.get("feedback", "No feedback provided.")
        strengths = data.get("strengths", [])
        improvements = data.get("improvements", [])
        return breakdown, feedback, strengths, improvements
