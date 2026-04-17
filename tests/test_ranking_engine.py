"""
Tests for RankingEngine.
"""
from datetime import datetime, timedelta, timezone

import pytest

from app.models.submission import AnswerType, MarkBreakdown, MarkingResult
from app.services.ranking_engine import RankingEngine

UTC = timezone.utc
BASE_TIME = datetime(2024, 6, 1, 10, 0, 0, tzinfo=UTC)


def _make_result(
    student_id: str,
    total_marks: float,
    minutes_offset: int = 0,
    max_marks: float = 100.0,
    passing_marks: float = 40.0,
    exam_id: str = "exam1",
) -> MarkingResult:
    """Helper to create a MarkingResult for testing."""
    submitted_at = BASE_TIME + timedelta(minutes=minutes_offset)
    percentage = round(total_marks / max_marks * 100, 2)
    return MarkingResult(
        student_id=student_id,
        question_id="q1",
        exam_id=exam_id,
        answer_type=AnswerType.TEXT,
        marks_breakdown=MarkBreakdown(
            content_marks=total_marks,
            presentation_marks=0.0,
            time_adjustment=0.0,
            total_marks=total_marks,
            max_marks=max_marks,
            percentage=percentage,
        ),
        feedback="Good answer.",
        strengths=[],
        improvements=[],
        submitted_at=submitted_at,
        is_passing=total_marks >= passing_marks,
    )


@pytest.fixture()
def engine() -> RankingEngine:
    return RankingEngine()


class TestRankingEngine:
    def test_empty_results(self, engine):
        ranking = engine.build_ranking("exam1", [])
        assert ranking.total_students == 0
        assert ranking.rankings == []

    def test_single_student(self, engine):
        results = [_make_result("s1", 75.0)]
        ranking = engine.build_ranking("exam1", results)
        assert ranking.total_students == 1
        assert ranking.rankings[0].rank == 1
        assert ranking.rankings[0].student_id == "s1"

    def test_ranking_by_marks_descending(self, engine):
        results = [
            _make_result("s1", 60.0, minutes_offset=0),
            _make_result("s2", 80.0, minutes_offset=5),
            _make_result("s3", 70.0, minutes_offset=10),
        ]
        ranking = engine.build_ranking("exam1", results)
        ids = [r.student_id for r in ranking.rankings]
        assert ids == ["s2", "s3", "s1"]
        assert ranking.rankings[0].rank == 1
        assert ranking.rankings[1].rank == 2
        assert ranking.rankings[2].rank == 3

    def test_time_tiebreaker_earlier_wins(self, engine):
        """When marks are equal, earlier submitter should be ranked higher."""
        results = [
            _make_result("s1", 75.0, minutes_offset=20),  # submitted later
            _make_result("s2", 75.0, minutes_offset=5),   # submitted earlier
        ]
        ranking = engine.build_ranking("exam1", results)
        assert ranking.rankings[0].student_id == "s2"
        assert ranking.rankings[1].student_id == "s1"

    def test_passing_students_count(self, engine):
        results = [
            _make_result("s1", 80.0),  # passing
            _make_result("s2", 35.0),  # failing
            _make_result("s3", 50.0),  # passing
        ]
        ranking = engine.build_ranking("exam1", results)
        assert ranking.passing_students == 2
        assert ranking.total_students == 3

    def test_statistics_average_highest_lowest(self, engine):
        results = [
            _make_result("s1", 60.0),
            _make_result("s2", 80.0),
            _make_result("s3", 40.0),
        ]
        ranking = engine.build_ranking("exam1", results)
        assert ranking.highest_marks == 80.0
        assert ranking.lowest_marks == 40.0
        assert ranking.average_marks == pytest.approx(60.0)

    def test_time_rank_reflects_submission_order(self, engine):
        """time_rank should independently reflect submission time ordering."""
        results = [
            _make_result("s1", 90.0, minutes_offset=30),  # best marks, submitted latest
            _make_result("s2", 70.0, minutes_offset=10),
            _make_result("s3", 50.0, minutes_offset=0),   # worst marks, submitted first
        ]
        ranking = engine.build_ranking("exam1", results)
        by_student = {r.student_id: r for r in ranking.rankings}
        assert by_student["s3"].time_rank == 1  # submitted first
        assert by_student["s2"].time_rank == 2
        assert by_student["s1"].time_rank == 3  # submitted last

    def test_time_rank_does_not_affect_score_rank(self, engine):
        """Score rank should be based on marks, not submission time."""
        results = [
            _make_result("s1", 90.0, minutes_offset=60),  # submitted last, highest marks
            _make_result("s2", 50.0, minutes_offset=0),   # submitted first, lower marks
        ]
        ranking = engine.build_ranking("exam1", results)
        assert ranking.rankings[0].student_id == "s1"  # still ranked 1st by marks
        assert ranking.rankings[0].time_rank == 2       # but 2nd in time
