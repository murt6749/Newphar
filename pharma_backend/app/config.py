from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    openrouter_api_key: str
    site_url: str
    site_name: str
    database_url: str
    secret_key: str
    algorithm: str
    access_token_expire_minutes: int

    class Config:
        env_file = ".env"

settings = Settings()