from datetime import datetime, timezone
from backend.models import Exam

def validate_submission_time(submitted_at: datetime, exam: Exam) -> str:
    """
    Returns: ON_TIME | LATE_ACCEPTED | REJECTED
    
    Rules:
    - submitted_at <= exam.deadline_time → ON_TIME
    - exam.deadline_time < submitted_at <= exam.late_deadline → LATE_ACCEPTED  
    - submitted_at > exam.late_deadline → REJECTED
    """
    # Ensure timezone awareness matches for comparison
    if submitted_at.tzinfo is None and exam.deadline_time.tzinfo is not None:
        submitted_at = submitted_at.replace(tzinfo=timezone.utc)
    if submitted_at.tzinfo is not None and exam.deadline_time.tzinfo is None:
        submitted_at = submitted_at.replace(tzinfo=None)
        
    if submitted_at <= exam.deadline_time:
        return "ON_TIME"
    elif submitted_at <= exam.late_deadline:
        return "LATE_ACCEPTED"
    else:
        return "REJECTED"
