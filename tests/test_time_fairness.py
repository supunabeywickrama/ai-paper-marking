"""
Tests for TimeFairnessService.
"""
from datetime import datetime, timedelta, timezone

import pytest

from app.services.time_fairness import TimeFairnessService


@pytest.fixture()
def service() -> TimeFairnessService:
    return TimeFairnessService(
        early_bonus_minutes=30,
        early_bonus_marks=2.0,
        late_penalty_per_minute=0.5,
        max_late_penalty=20.0,
    )


def _utc(dt: datetime) -> datetime:
    return dt.replace(tzinfo=timezone.utc)


DEADLINE = _utc(datetime(2024, 6, 1, 12, 0, 0))


class TestTimeFairnessAdjustment:
    def test_on_time_no_adjustment(self, service):
        submitted = DEADLINE  # exactly on time
        assert service.calculate_adjustment(submitted, DEADLINE) == 0.0

    def test_slightly_early_no_bonus(self, service):
        # 10 minutes before deadline — within deadline but not in the 30-min bonus window
        submitted = DEADLINE - timedelta(minutes=10)
        assert service.calculate_adjustment(submitted, DEADLINE) == 0.0

    def test_early_enough_for_bonus(self, service):
        # 30 minutes before deadline — exactly at the bonus threshold
        submitted = DEADLINE - timedelta(minutes=30)
        assert service.calculate_adjustment(submitted, DEADLINE) == 2.0

    def test_very_early_still_gets_bonus(self, service):
        # 60 minutes before deadline — well inside the bonus window
        submitted = DEADLINE - timedelta(minutes=60)
        assert service.calculate_adjustment(submitted, DEADLINE) == 2.0

    def test_late_penalty_applied(self, service):
        # 10 minutes late → 10 * 0.5 = 5.0 marks deducted
        submitted = DEADLINE + timedelta(minutes=10)
        assert service.calculate_adjustment(submitted, DEADLINE) == -5.0

    def test_late_penalty_capped_at_max(self, service):
        # 100 minutes late → 100 * 0.5 = 50, but capped at 20
        submitted = DEADLINE + timedelta(minutes=100)
        assert service.calculate_adjustment(submitted, DEADLINE) == -20.0

    def test_partial_minute_late(self, service):
        # 1.5 minutes late → 1.5 * 0.5 = 0.75
        submitted = DEADLINE + timedelta(seconds=90)
        assert service.calculate_adjustment(submitted, DEADLINE) == -0.75

    def test_naive_datetimes_treated_as_utc(self, service):
        naive_deadline = datetime(2024, 6, 1, 12, 0, 0)  # no tzinfo
        naive_submitted = datetime(2024, 6, 1, 11, 0, 0)  # 60 min early
        assert service.calculate_adjustment(naive_submitted, naive_deadline) == 2.0

    def test_aware_and_naive_mixed(self, service):
        aware_deadline = DEADLINE
        naive_submitted = datetime(2024, 6, 1, 12, 30, 0)  # 30 min late, no tzinfo
        assert service.calculate_adjustment(naive_submitted, aware_deadline) == -15.0


class TestSubmissionStatus:
    def test_on_time_status(self, service):
        assert service.submission_status(DEADLINE, DEADLINE) == "On time"

    def test_early_status(self, service):
        submitted = DEADLINE - timedelta(minutes=45)
        assert service.submission_status(submitted, DEADLINE) == "Early (bonus applied)"

    def test_late_status(self, service):
        submitted = DEADLINE + timedelta(minutes=15)
        status = service.submission_status(submitted, DEADLINE)
        assert status.startswith("Late by 15")
