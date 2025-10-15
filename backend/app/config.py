from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List
from pathlib import Path


class Settings(BaseSettings):
    """Application configuration settings"""
    
    # App Info
    app_name: str = "DoNexus Document AI"
    app_version: str = "1.0.0"
    environment: str = "development"
    
    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = True
    
    # API Keys (Required for AI extraction)
    OPENAI_API_KEY: str = ""
    ANTHROPIC_API_KEY: str = ""
    
    # CORS
    cors_origins: List[str] = ["http://localhost:5173", "http://localhost:3000"]
    
    # File Upload
    max_file_size_mb: int = 10
    upload_dir: Path = Path("./uploads")
    allowed_extensions: List[str] = [".pdf"]
    
    # AI Models
    primary_model: str = "gpt-4-turbo-preview"
    fallback_model: str = "claude-3-sonnet-20240229"
    ai_temperature: float = 0.1
    ai_max_tokens: int = 2000
    
    # Storage
    storage_type: str = "filesystem"
    data_dir: Path = Path("./data")
    
    # Logging
    log_level: str = "INFO"
    log_file: Path = Path("./logs/app.log")
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False
    )
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Create directories if they don't exist
        self.upload_dir.mkdir(parents=True, exist_ok=True)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.log_file.parent.mkdir(parents=True, exist_ok=True)


# Global settings instance
settings = Settings()
