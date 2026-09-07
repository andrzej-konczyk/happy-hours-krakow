from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    SUPABASE_URL: str = ""
    SUPABASE_KEY: str = ""
    ANTHROPIC_API_KEY: str = ""
    ADMIN_TOKEN: str = ""
    ENV: str = "development"

    class Config:
        env_file = ".env"


settings = Settings()