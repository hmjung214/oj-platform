from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str
    sync_database_url: str
    secret_key: str
    algorithm: str
    internal_key: str
    debug: bool = False

    redis_url: str
    celery_broker_url: str
    celery_result_backend: str

    openai_api_key: str

    class Config:
        env_file = ".env"

settings = Settings()
