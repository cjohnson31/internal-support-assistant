from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    llm_api_key: str = ""
    llm_model: str = "claude-haiku-4-5-20251001"
    embedding_model: str = "all-MiniLM-L6-v2"
    judge_model: str = "claude-haiku-4-5-20251001"

    slack_bot_token: str = ""
    slack_app_token: str = ""

    chroma_persist_dir: str = ".chroma"
    retrieval_top_k: int = 5
    confidence_threshold: float = 0.3


settings = Settings()
