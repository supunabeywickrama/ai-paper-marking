from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    openai_api_key: str = "your_openai_api_key_here"
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/aipapermarking"
    smtp_server: str = "smtp.gmail.com"
    smtp_port: int = 587
    smtp_username: str = "your_email@gmail.com"
    smtp_password: str = "your_app_password"
    upload_dir: str = "./uploads"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

settings = Settings()
