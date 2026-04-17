"""
Integration tests for the FastAPI routes.

The AI marker services are mocked so no OpenAI key is required.
"""
from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.models.submission import AnswerType, MarkBreakdown, MarkingResult

UTC = timezone.utc
NOW = datetime(2024, 6, 1, 12, 0, 0, tzinfo=UTC)

_MOCK_BREAKDOWN = MarkBreakdown(
    content_marks=70.0,
    presentation_marks=10.0,
    time_adjustment=0.0,
    total_marks=80.0,
    max_marks=100.0,
    percentage=80.0,
)
_MOCK_RESULT = MarkingResult(
    student_id="s1",
    question_id="q1",
    exam_id="exam_test",
    answer_type=AnswerType.TEXT,
    marks_breakdown=_MOCK_BREAKDOWN,
    feedback="Well done.",
    strengths=["Clear writing"],
    improvements=["More depth"],
    submitted_at=NOW,
    is_passing=True,
)


@pytest.fixture(autouse=True)
def clear_store():
    """Clear in-memory results store before each test."""
    from app.api import routes

    routes._results_store.clear()
    yield
    routes._results_store.clear()


@pytest.fixture()
def client():
    return TestClient(app)


@pytest.fixture()
def mock_engine():
    with patch("app.api.routes._marking_engine") as mock:
        mock.mark.return_value = _MOCK_RESULT
        yield mock


class TestHealthEndpoint:
    def test_health_check(self, client):
        resp = client.get("/health")
        assert resp.status_code == 200
        assert resp.json()["status"] == "ok"


class TestMarkEndpoint:
    def test_mark_text_submission(self, client, mock_engine):
        payload = {
            "submission": {
                "student_id": "s1",
                "question_id": "q1",
                "exam_id": "exam_test",
                "answer_text": "Photosynthesis is the process...",
                "answer_type": "text",
                "submitted_at": NOW.isoformat(),
            },
            "criteria": {
                "question_id": "q1",
                "question_text": "Explain photosynthesis.",
                "max_marks": 100.0,
            },
        }
        resp = client.post("/api/v1/mark", json=payload)
        assert resp.status_code == 200
        data = resp.json()
        assert data["result"]["student_id"] == "s1"
        assert data["result"]["marks_breakdown"]["total_marks"] == 80.0
        assert data["result"]["is_passing"] is True

    def test_mark_returns_time_status_when_deadline_given(self, client, mock_engine):
        payload = {
            "submission": {
                "student_id": "s1",
                "question_id": "q1",
                "exam_id": "exam_test",
                "answer_text": "Some answer.",
                "answer_type": "text",
                "submitted_at": NOW.isoformat(),
            },
            "criteria": {
                "question_id": "q1",
                "question_text": "A question.",
                "max_marks": 100.0,
                "deadline": NOW.isoformat(),
            },
        }
        resp = client.post("/api/v1/mark", json=payload)
        assert resp.status_code == 200
        data = resp.json()
        assert data["time_status"] is not None

    def test_mark_engine_error_returns_500(self, client):
        with patch("app.api.routes._marking_engine") as mock:
            mock.mark.side_effect = RuntimeError("LLM API failure")
            payload = {
                "submission": {
                    "student_id": "s1",
                    "question_id": "q1",
                    "answer_text": "Answer.",
                    "answer_type": "text",
                    "submitted_at": NOW.isoformat(),
                },
                "criteria": {
                    "question_id": "q1",
                    "question_text": "Question?",
                    "max_marks": 100.0,
                },
            }
            resp = client.post("/api/v1/mark", json=payload)
            assert resp.status_code == 500


class TestRankingsEndpoint:
    def test_empty_exam_rankings(self, client):
        resp = client.get("/api/v1/rankings/no_such_exam")
        assert resp.status_code == 200
        data = resp.json()
        assert data["total_students"] == 0
        assert data["rankings"] == []

    def test_rankings_after_submissions(self, client, mock_engine):
        # Submit two students
        for student_id in ["s1", "s2"]:
            mock_engine.mark.return_value = MarkingResult(
                student_id=student_id,
                question_id="q1",
                exam_id="exam_r",
                answer_type=AnswerType.TEXT,
                marks_breakdown=MarkBreakdown(
                    content_marks=70.0,
                    presentation_marks=10.0,
                    time_adjustment=0.0,
                    total_marks=80.0 if student_id == "s1" else 60.0,
                    max_marks=100.0,
                    percentage=80.0 if student_id == "s1" else 60.0,
                ),
                feedback="OK",
                strengths=[],
                improvements=[],
                submitted_at=NOW,
                is_passing=True,
            )
            client.post(
                "/api/v1/mark",
                json={
                    "submission": {
                        "student_id": student_id,
                        "question_id": "q1",
                        "exam_id": "exam_r",
                        "answer_text": "Answer.",
                        "answer_type": "text",
                        "submitted_at": NOW.isoformat(),
                    },
                    "criteria": {"question_id": "q1", "question_text": "Q?", "max_marks": 100.0},
                },
            )

        resp = client.get("/api/v1/rankings/exam_r")
        assert resp.status_code == 200
        data = resp.json()
        assert data["total_students"] == 2
        # s1 has higher marks → rank 1
        assert data["rankings"][0]["student_id"] == "s1"


class TestStudentResultsEndpoint:
    def test_student_not_found(self, client):
        resp = client.get("/api/v1/results/exam1/unknown_student")
        assert resp.status_code == 404

    def test_student_results_returned(self, client, mock_engine):
        alice_result = MarkingResult(
            student_id="s_alice",
            question_id="q1",
            exam_id="exam_test",
            answer_type=AnswerType.TEXT,
            marks_breakdown=_MOCK_BREAKDOWN,
            feedback="Well done.",
            strengths=[],
            improvements=[],
            submitted_at=NOW,
            is_passing=True,
        )
        mock_engine.mark.return_value = alice_result

        client.post(
            "/api/v1/mark",
            json={
                "submission": {
                    "student_id": "s_alice",
                    "question_id": "q1",
                    "exam_id": "exam_test",
                    "answer_text": "Alice's answer.",
                    "answer_type": "text",
                    "submitted_at": NOW.isoformat(),
                },
                "criteria": {"question_id": "q1", "question_text": "Q?", "max_marks": 100.0},
            },
        )
        resp = client.get("/api/v1/results/exam_test/s_alice")
        assert resp.status_code == 200
        results = resp.json()
        assert len(results) == 1
        assert results[0]["student_id"] == "s_alice"
