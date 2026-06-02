from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Edu Multi-Agent Service"
    DEBUG: bool = True
    
    XIAOMI_API_KEY: str
    XIAOMI_BASE_URL: str
    XIAOMI_MODEL: str
    
    # RAG Config
    RAG_API_BASE_URL: str
    POSTGRES_URL: str
    REDIS_URL: str
    DASHVECTOR_API_KEY: str
    DASHVECTOR_ENDPOINT: str
    EMBEDDING_API_KEY: str
    EMBEDDING_API_URL: str
    


    class Config:
        env_file = ".env"

settings = Settings()
