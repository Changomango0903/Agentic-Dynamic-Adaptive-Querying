from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    TAVILY_API_KEY: str | None = None
    NEWSAPI_KEY: str | None = None
    CACHE_TTL_SECS: int = 86400
    TOP_K: int = 8
    STEP_CAP: int = 5
    MARGINAL_COVERAGE_THRESHOLD: float = 0.12

    LLM_PROVIDER: str = "ollama"  # or "ollama"
    OPENAI_API_KEY: str | None = None
    OPENAI_MODEL: str = "gpt-4o-mini"
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "llama3.2"

    SQLITE_PATH: str = "./adaq.db"

    class Config:
        env_file = ".env"

settings = Settings()