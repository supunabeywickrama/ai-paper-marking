"""
Configuration settings for the AI Paper Marking System.
"""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    openai_api_key: str = ""
    openai_model_text: str = "gpt-4o"
    openai_model_vision: str = "gpt-4o"

    # Time fairness settings
    early_submission_bonus_minutes: int = 30  # window before deadline for bonus
    early_submission_bonus_marks: float = 2.0  # bonus marks for early submission
    late_submission_penalty_per_minute: float = 0.5  # marks deducted per minute late
    max_late_penalty: float = 20.0  # maximum late penalty in marks

    # Marking settings
    max_marks_per_question: float = 100.0
    passing_marks: float = 40.0


settings = Settings()
