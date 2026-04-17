"""
Vision Marker Service — uses a vision-capable LLM to evaluate image-based student answers.
"""
import base64
import json
import logging
from typing import Optional

from openai import OpenAI

from ..config import settings
from ..models.submission import MarkBreakdown, MarkingCriteria

logger = logging.getLogger(__name__)

_SUPPORTED_IMAGE_PREFIXES = ("data:image/", "/9j/", "iVBOR", "R0lGOD", "UklGR", "Qk0")


def _ensure_data_uri(image_b64: str) -> str:
    """Ensure the base64 string is wrapped in a data URI."""
    if image_b64.startswith("data:"):
        return image_b64
    # Detect common image signatures and pick the MIME type
    try:
        decoded_peek = base64.b64decode(image_b64[:16])
    except Exception:
        decoded_peek = b""

    if decoded_peek[:3] == b"\xff\xd8\xff":
        mime = "image/jpeg"
    elif decoded_peek[:8] == b"\x89PNG\r\n\x1a\n":
        mime = "image/png"
    elif decoded_peek[:6] in (b"GIF87a", b"GIF89a"):
        mime = "image/gif"
    elif decoded_peek[:4] == b"RIFF":
        mime = "image/webp"
    else:
        mime = "image/png"  # safe default

    return f"data:{mime};base64,{image_b64}"


class VisionMarker:
    """Evaluates image-based student answers using a vision-capable language model."""

    def __init__(self, client: Optional[OpenAI] = None) -> None:
        self._client = client or OpenAI(api_key=settings.openai_api_key)

    def mark(
        self,
        image_base64: str,
        criteria: MarkingCriteria,
        supporting_text: Optional[str] = None,
        time_adjustment: float = 0.0,
    ) -> tuple[MarkBreakdown, str, list[str], list[str]]:
        """
        Mark a visual answer (provided as a base64-encoded image).

        Parameters
        ----------
        image_base64:
            Base64-encoded image of the student's answer.
        criteria:
            Marking criteria and rubric.
        supporting_text:
            Optional textual annotation or description submitted alongside the image.
        time_adjustment:
            Marks adjustment for early/late submission.

        Returns
        -------
        tuple of (MarkBreakdown, feedback_str, strengths_list, improvements_list)
        """
        data_uri = _ensure_data_uri(image_base64)
        messages = self._build_messages(data_uri, criteria, supporting_text)

        response = self._client.chat.completions.create(
            model=settings.openai_model_vision,
            messages=messages,
            response_format={"type": "json_object"},
            temperature=0.2,
            max_tokens=1024,
        )

        raw = response.choices[0].message.content
        return self._parse_response(raw, criteria, time_adjustment)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _build_messages(
        data_uri: str,
        criteria: MarkingCriteria,
        supporting_text: Optional[str],
    ) -> list[dict]:
        rubric_section = (
            f"\n\nMarking Rubric:\n{criteria.marking_rubric}" if criteria.marking_rubric else ""
        )
        model_answer_section = (
            f"\n\nModel Answer:\n{criteria.model_answer}" if criteria.model_answer else ""
        )
        system_content = (
            "You are an expert academic marker evaluating a student's visual answer (diagram, "
            "sketch, graph, or written image). Analyse the image carefully and return a JSON "
            "object with:\n"
            "  content_marks      (float) — marks for correctness and completeness of visual content\n"
            "  presentation_marks (float) — marks for neatness, labelling, and clarity\n"
            "  feedback           (string) — overall constructive feedback\n"
            "  strengths          (array of strings) — specific things done well\n"
            "  improvements       (array of strings) — specific areas needing improvement\n\n"
            f"Question: {criteria.question_text}\n"
            f"Maximum marks: {criteria.max_marks}"
            f"{model_answer_section}"
            f"{rubric_section}"
        )

        user_content: list[dict] = [
            {"type": "text", "text": f"Please mark this visual answer for: '{criteria.question_text}'"},
            {"type": "image_url", "image_url": {"url": data_uri, "detail": "high"}},
        ]
        if supporting_text:
            user_content.append(
                {"type": "text", "text": f"Student's annotation/notes: {supporting_text}"}
            )
        user_content.append(
            {"type": "text", "text": f"Award marks out of {criteria.max_marks}."}
        )

        return [
            {"role": "system", "content": system_content},
            {"role": "user", "content": user_content},
        ]

    @staticmethod
    def _parse_response(
        raw_json: str,
        criteria: MarkingCriteria,
        time_adjustment: float,
    ) -> tuple[MarkBreakdown, str, list[str], list[str]]:
        try:
            data = json.loads(raw_json)
        except json.JSONDecodeError:
            logger.error("Failed to parse vision LLM response as JSON: %s", raw_json)
            data = {}

        content_marks = min(float(data.get("content_marks", 0)), criteria.max_marks)
        presentation_marks = float(data.get("presentation_marks", 0))

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
