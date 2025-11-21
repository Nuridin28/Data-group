import os
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

_api_key = os.getenv("API_KEY")

if _api_key:
    os.environ["API_KEY"] = _api_key

class Settings:
    
    API_KEY: str = os.getenv("API_KEY", "")
    API_BASE_URL: str = os.getenv("API_BASE_URL", "")
    LLM_MODEL: str = os.getenv("LLM_MODEL", "deepseek-chat")
    
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")
    
    CHROMA_PERSIST_DIR: str = os.getenv("CHROMA_PERSIST_DIR", "./vectorstore")
    
    DATA_FILE: str = os.getenv("DATA_FILE", "data/track_1_digital_economy_kz.csv")
    
    RAG_TOP_K: int = int(os.getenv("RAG_TOP_K", "5"))
    TEMPERATURE: float = float(os.getenv("TEMPERATURE", "0.0"))
    
    API_TITLE: str = "Financial Analytics & Digital Business AI System"
    API_VERSION: str = "1.0.0"
    API_DESCRIPTION: str = "AI-powered financial analytics system with RAG for Kazakhstan digital economy data"
    
    @classmethod
    def validate(cls) -> None:
        if not cls.API_KEY:
            raise ValueError("API_KEY is required. Please set it in .env file.")
        if not os.path.exists(cls.DATA_FILE):
            raise FileNotFoundError(f"Data file not found: {cls.DATA_FILE}")
    
    @property
    def effective_api_key(self) -> str:
        return self.API_KEY

settings = Settings()

