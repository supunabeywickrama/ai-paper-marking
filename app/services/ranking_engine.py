"""
Ranking Engine — builds an automated ranking from a list of marking results.

Fairness rule: when two students have equal total_marks, the student who
submitted *earlier* is ranked higher (time-based tiebreaker).
"""
from datetime import datetime

from ..models.submission import ExamRanking, MarkingResult, RankingEntry


class RankingEngine:
    """Produces an ordered ranking from a collection of MarkingResult objects."""

    def build_ranking(self, exam_id: str, results: list[MarkingResult]) -> ExamRanking:
        """
        Build an ExamRanking from a list of MarkingResult objects.

        Tie-breaking: students with the same total_marks are ordered by
        submitted_at (ascending — earlier is better).

        Parameters
        ----------
        exam_id:
            Identifier for the exam being ranked.
        results:
            All MarkingResult objects for the exam.
        """
        if not results:
            return ExamRanking(
                exam_id=exam_id,
                total_students=0,
                passing_students=0,
                average_marks=0.0,
                highest_marks=0.0,
                lowest_marks=0.0,
                rankings=[],
            )

        # Sort: primary descending by total_marks, secondary ascending by submitted_at
        sorted_results = sorted(
            results,
            key=lambda r: (-r.marks_breakdown.total_marks, r.submitted_at),
        )

        # Build time-rank lookup (rank purely by submission time, earliest = 1)
        time_sorted = sorted(results, key=lambda r: r.submitted_at)
        time_rank_map: dict[str, int] = {
            r.student_id: idx + 1 for idx, r in enumerate(time_sorted)
        }

        rankings: list[RankingEntry] = []
        rank = 1
        prev_marks: float | None = None
        prev_time: datetime | None = None
        tied_count = 0

        for idx, result in enumerate(sorted_results):
            marks = result.marks_breakdown.total_marks
            sub_time = result.submitted_at

            # Determine if this entry shares the same rank as the previous
            if prev_marks is not None and marks == prev_marks and sub_time == prev_time:
                # Exact tie (same marks AND same submission time — extremely rare)
                tied_count += 1
            else:
                rank = idx + 1
                tied_count = 0

            rankings.append(
                RankingEntry(
                    rank=rank,
                    student_id=result.student_id,
                    exam_id=exam_id,
                    total_marks=marks,
                    percentage=result.marks_breakdown.percentage,
                    submission_time=sub_time,
                    time_rank=time_rank_map.get(result.student_id, idx + 1),
                    is_passing=result.is_passing,
                )
            )
            prev_marks = marks
            prev_time = sub_time

        all_marks = [r.marks_breakdown.total_marks for r in results]
        passing = sum(1 for r in results if r.is_passing)

        return ExamRanking(
            exam_id=exam_id,
            total_students=len(results),
            passing_students=passing,
            average_marks=round(sum(all_marks) / len(all_marks), 2),
            highest_marks=max(all_marks),
            lowest_marks=min(all_marks),
            rankings=rankings,
        )
