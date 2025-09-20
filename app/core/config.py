from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    ENV: str = "dev"

    STORAGE_BASE_PATH: str = "./storage"
    TEMPLATE_PATH: str = "./templates/proposta_template.docx"

    SP_TO_HOURS: float = 4.0            # 1 Story Point ≈ 4h
    SPRINT_MEDIUM_HOURS: int = 80       # Sprint média ≈ 80h
    SPRINT_SMALL_HOURS: int = 40        # Sprint pequena ≈ 40h
    HOURS_PER_DAY: int = 6              # Capacidade efetiva/dia

    AWS_REGION: str | None = None
    MODEL_ID: str | None = None
    TEMPERATURE: float = 0.3

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

settings = Settings()
