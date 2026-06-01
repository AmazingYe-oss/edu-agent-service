from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # 应用配置
    APP_NAME: str = "Edu Agent Service"
    DEBUG: bool = False
    
    # OpenAI 配置
    OPENAI_API_KEY: str
    OPENAI_MODEL: str = "gpt-4"
    OPENAI_TEMPERATURE: float = 0.7
    
    # RAG API 配置
    RAG_API_BASE_URL: str = "http://localhost:8000"
    RAG_API_KEY: Optional[str] = None
    
    # 数据库配置（可选）
    DATABASE_URL: Optional[str] = None
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()
