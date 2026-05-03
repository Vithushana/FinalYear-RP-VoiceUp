from pydantic_settings import BaseSettings, SettingsConfigDict

# Configuration settings for the Sarma backend application
class Settings(BaseSettings):
    app_name: str = "VoiceUp Decision Support API"
    database_url: str = "sqlite:///./voiceup.sqlite3"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
