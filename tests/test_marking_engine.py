"""
Tests for MarkingEngine — mocking out the AI services.
"""
from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock

import pytest

from app.models.submission import (
    AnswerType,
    MarkBreakdown,
    MarkingCriteria,
    Submission,
)
from app.services.marking_engine import MarkingEngine
from app.services.text_marker import TextMarker
from app.services.time_fairness import TimeFairnessService
from app.services.vision_marker import VisionMarker

UTC = timezone.utc
DEADLINE = datetime(2024, 6, 1, 12, 0, 0, tzinfo=UTC)


def _breakdown(
    content: float,
    presentation: float,
    time_adj: float,
    max_marks: float = 100.0,
) -> MarkBreakdown:
    total = max(0.0, min(content + presentation + time_adj, max_marks))
    return MarkBreakdown(
        content_marks=content,
        presentation_marks=presentation,
        time_adjustment=time_adj,
        total_marks=total,
        max_marks=max_marks,
        percentage=round(total / max_marks * 100, 2),
    )


def _mock_text_marker(content=70.0, presentation=10.0, time_adj=0.0) -> TextMarker:
    marker = MagicMock(spec=TextMarker)
    marker.mark.return_value = (
        _breakdown(content, presentation, time_adj),
        "Good text answer.",
        ["Clear explanation"],
        ["More examples needed"],
    )
    return marker


def _mock_vision_marker(content=65.0, presentation=15.0, time_adj=0.0) -> VisionMarker:
    marker = MagicMock(spec=VisionMarker)
    marker.mark.return_value = (
        _breakdown(content, presentation, time_adj),
        "Good diagram.",
        ["Well labelled"],
        ["Add units to axes"],
    )
    return marker


def _criteria(deadline=None) -> MarkingCriteria:
    return MarkingCriteria(
        question_id="q1",
        question_text="Explain photosynthesis.",
        model_answer="Photosynthesis converts light to chemical energy.",
        max_marks=100.0,
        marking_rubric="Award marks for accuracy, depth, and clarity.",
        deadline=deadline,
    )


def _submission(
    answer_type: AnswerType = AnswerType.TEXT,
    submitted_at: datetime | None = None,
) -> Submission:
    return Submission(
        student_id="student_001",
        question_id="q1",
        exam_id="exam1",
        answer_text="Plants use sunlight to make glucose." if answer_type != AnswerType.IMAGE else None,
        answer_image_base64="AAAA" if answer_type in (AnswerType.IMAGE, AnswerType.MIXED) else None,
        answer_type=answer_type,
        submitted_at=submitted_at or DEADLINE,
    )


class TestMarkingEngineText:
    def test_text_submission_marks_and_feedback(self):
        engine = MarkingEngine(
            text_marker=_mock_text_marker(),
            vision_marker=_mock_vision_marker(),
        )
        result = engine.mark(_submission(AnswerType.TEXT), _criteria())
        assert result.marks_breakdown.content_marks == 70.0
        assert result.marks_breakdown.total_marks == 80.0
        assert result.feedback == "Good text answer."
        assert "Clear explanation" in result.strengths
        assert result.is_passing is True

    def test_text_submission_failing(self):
        engine = MarkingEngine(
            text_marker=_mock_text_marker(content=20.0, presentation=5.0),
            vision_marker=_mock_vision_marker(),
            passing_marks=40.0,
        )
        result = engine.mark(_submission(AnswerType.TEXT), _criteria())
        assert result.is_passing is False

    def test_text_no_answer_raises(self):
        engine = MarkingEngine(
            text_marker=_mock_text_marker(),
            vision_marker=_mock_vision_marker(),
        )
        sub = Submission(
            student_id="s1",
            question_id="q1",
            answer_type=AnswerType.TEXT,
            submitted_at=DEADLINE,
        )
        with pytest.raises(ValueError, match="answer_text"):
            engine.mark(sub, _criteria())


class TestMarkingEngineImage:
    def test_image_submission_uses_vision_marker(self):
        vision = _mock_vision_marker(content=65.0, presentation=15.0)
        engine = MarkingEngine(text_marker=_mock_text_marker(), vision_marker=vision)
        result = engine.mark(_submission(AnswerType.IMAGE), _criteria())
        vision.mark.assert_called_once()
        assert result.marks_breakdown.content_marks == 65.0

    def test_image_no_image_raises(self):
        engine = MarkingEngine(
            text_marker=_mock_text_marker(),
            vision_marker=_mock_vision_marker(),
        )
        sub = Submission(
            student_id="s1",
            question_id="q1",
            answer_type=AnswerType.IMAGE,
            submitted_at=DEADLINE,
        )
        with pytest.raises(ValueError, match="answer_image_base64"):
            engine.mark(sub, _criteria())


class TestMarkingEngineMixed:
    def test_mixed_uses_best_content_marks(self):
        # text: 70 content, vision: 65 content → best is 70
        engine = MarkingEngine(
            text_marker=_mock_text_marker(content=70.0, presentation=10.0),
            vision_marker=_mock_vision_marker(content=65.0, presentation=15.0),
        )
        result = engine.mark(_submission(AnswerType.MIXED), _criteria())
        assert result.marks_breakdown.content_marks == 70.0

    def test_mixed_averages_presentation_marks(self):
        # text: 10 presentation, vision: 15 presentation → average 12.5
        engine = MarkingEngine(
            text_marker=_mock_text_marker(content=70.0, presentation=10.0),
            vision_marker=_mock_vision_marker(content=65.0, presentation=15.0),
        )
        result = engine.mark(_submission(AnswerType.MIXED), _criteria())
        assert result.marks_breakdown.presentation_marks == pytest.approx(12.5)

    def test_mixed_combines_feedback(self):
        engine = MarkingEngine(
            text_marker=_mock_text_marker(),
            vision_marker=_mock_vision_marker(),
        )
        result = engine.mark(_submission(AnswerType.MIXED), _criteria())
        assert "Good text answer." in result.feedback
        assert "Good diagram." in result.feedback

    def test_mixed_deduplicates_strengths(self):
        text = _mock_text_marker()
        text.mark.return_value = (
            _breakdown(70, 10, 0),
            "Text feedback.",
            ["Clear explanation", "Shared strength"],
            [],
        )
        vision = _mock_vision_marker()
        vision.mark.return_value = (
            _breakdown(65, 15, 0),
            "Vision feedback.",
            ["Shared strength", "Well labelled"],
            [],
        )
        engine = MarkingEngine(text_marker=text, vision_marker=vision)
        result = engine.mark(_submission(AnswerType.MIXED), _criteria())
        # "Shared strength" should appear only once
        assert result.strengths.count("Shared strength") == 1


class TestTimeFairnessIntegration:
    def test_early_submission_gets_bonus(self):
        early_time = DEADLINE - timedelta(minutes=60)
        sub = _submission(submitted_at=early_time)
        engine = MarkingEngine(
            text_marker=_mock_text_marker(content=70.0, presentation=10.0, time_adj=2.0),
            vision_marker=_mock_vision_marker(),
            time_service=TimeFairnessService(
                early_bonus_minutes=30,
                early_bonus_marks=2.0,
                late_penalty_per_minute=0.5,
                max_late_penalty=20.0,
            ),
        )
        # The mock already returns time_adj=2.0 in its breakdown
        criteria = _criteria(deadline=DEADLINE)
        result = engine.mark(sub, criteria)
        assert result.marks_breakdown.time_adjustment == 2.0

    def test_late_submission_has_negative_adjustment(self):
        late_time = DEADLINE + timedelta(minutes=10)
        sub = _submission(submitted_at=late_time)

        time_service = TimeFairnessService(
            early_bonus_minutes=30,
            early_bonus_marks=2.0,
            late_penalty_per_minute=0.5,
            max_late_penalty=20.0,
        )
        text_marker = MagicMock(spec=TextMarker)

        def capture_and_return(answer_text, criteria, time_adjustment):
            # reflect the actual time_adjustment passed in
            bd = _breakdown(70, 10, time_adjustment)
            return bd, "Feedback.", [], []

        text_marker.mark.side_effect = capture_and_return

        engine = MarkingEngine(
            text_marker=text_marker,
            vision_marker=_mock_vision_marker(),
            time_service=time_service,
        )
        criteria = _criteria(deadline=DEADLINE)
        result = engine.mark(sub, criteria)
        assert result.marks_breakdown.time_adjustment == -5.0
        assert result.marks_breakdown.total_marks == 75.0  # 70+10-5
