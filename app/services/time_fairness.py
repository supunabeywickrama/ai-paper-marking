"""
Time Fairness Service — calculates time-based mark adjustments.

Rules
-----
* Submissions made *before* the deadline and within the early-bonus window earn
  a small bonus (reward for timely preparation).
* Submissions made *after* the deadline incur a per-minute late penalty up to a
  configurable maximum.
* Submissions made exactly on time or outside the bonus window but before the
  deadline receive no adjustment.
* When two students achieve the same total marks the earlier submitter is ranked
  higher — this is enforced by the RankingEngine, not by adjusting marks here.
"""
from datetime import datetime, timezone

from ..config import settings


class TimeFairnessService:
    """Calculates time-based mark adjustments for a submission."""

    def __init__(
        self,
        early_bonus_minutes: int = settings.early_submission_bonus_minutes,
        early_bonus_marks: float = settings.early_submission_bonus_marks,
        late_penalty_per_minute: float = settings.late_submission_penalty_per_minute,
        max_late_penalty: float = settings.max_late_penalty,
    ) -> None:
        self.early_bonus_minutes = early_bonus_minutes
        self.early_bonus_marks = early_bonus_marks
        self.late_penalty_per_minute = late_penalty_per_minute
        self.max_late_penalty = max_late_penalty

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def calculate_adjustment(
        self,
        submitted_at: datetime,
        deadline: datetime,
    ) -> float:
        """
        Return the mark adjustment (positive = bonus, negative = penalty) for
        a submission relative to its deadline.

        Both datetimes should be timezone-aware (UTC).  Naive datetimes are
        treated as UTC.
        """
        submitted_at = self._to_utc(submitted_at)
        deadline = self._to_utc(deadline)

        delta_seconds = (submitted_at - deadline).total_seconds()
        delta_minutes = delta_seconds / 60.0

        if delta_minutes > 0:
            # Late submission — apply penalty
            penalty = min(delta_minutes * self.late_penalty_per_minute, self.max_late_penalty)
            return -round(penalty, 2)

        # On time or early
        early_minutes = -delta_minutes  # positive = how many minutes before deadline
        if early_minutes >= self.early_bonus_minutes:
            return round(self.early_bonus_marks, 2)

        return 0.0

    def submission_status(self, submitted_at: datetime, deadline: datetime) -> str:
        """Return a human-readable status string."""
        submitted_at = self._to_utc(submitted_at)
        deadline = self._to_utc(deadline)
        delta_seconds = (submitted_at - deadline).total_seconds()

        if delta_seconds > 0:
            minutes_late = int(delta_seconds / 60)
            return f"Late by {minutes_late} minute(s)"
        elif -delta_seconds / 60 >= self.early_bonus_minutes:
            return "Early (bonus applied)"
        else:
            return "On time"

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _to_utc(dt: datetime) -> datetime:
        if dt.tzinfo is None:
            return dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(timezone.utc)
