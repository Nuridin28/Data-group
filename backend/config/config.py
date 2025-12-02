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
        
        possible_paths = [
            cls.DATA_FILE,
            os.path.join("backend", cls.DATA_FILE),
            os.path.join(os.path.dirname(os.path.dirname(__file__)), cls.DATA_FILE),
            "data/track_1_digital_economy_kz.csv",
            "backend/data/track_1_digital_economy_kz.csv",
        ]
        
        found_path = None
        for path in possible_paths:
            if os.path.exists(path):
                found_path = path
                cls.DATA_FILE = path
                break
        
        if not found_path:
            error_msg = f"Data file not found. Tried paths: {', '.join(possible_paths)}\n"
            error_msg += f"Current DATA_FILE env var: '{os.getenv('DATA_FILE', 'not set')}'\n"
            error_msg += f"Current working directory: {os.getcwd()}\n"
            error_msg += "Please set DATA_FILE environment variable to the correct path."
            raise FileNotFoundError(error_msg)
    
    @property
    def effective_api_key(self) -> str:
        return self.API_KEY

settings = Settings()

