from typing import List
from pydantic_settings import BaseSettings
from pydantic import Field
import os

class Settings(BaseSettings):
    app_name: str = "Language Simplification MVP"
    environment: str = "development"
    debug: bool = True
    
    # CORS
    allowed_origins: str = "http://localhost:5173,http://127.0.0.1:5173,http://localhost:3000"
    
    # Database
    _BACKEND_DIR: str = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    _DEFAULT_DB: str = os.path.join(_BACKEND_DIR, "adaptive_learning.db").replace("\\", "/")
    database_url: str = f"sqlite:///{_DEFAULT_DB}"
    
    # LLM Configuration
    llm_provider: str = "google"
    llm_model: str = "gemini-1.5-flash"
    llm_timeout_seconds: int = 15
    llm_temperature: float = 0.2
    llm_max_regenerations: int = 1
    
    # Optional API Keys
    gemini_api_key: str = ""
    openai_api_key: str = ""

    # Stage 12 Integration Modes
    component1_mode: str = "mock"       # mock | api
    component2_mode: str = "mock"       # mock | api
    component4_mode: str = "mock"       # mock | api
    enable_component1_external_import: bool = False
    scoring_version: str = "1.0"
    
    @property
    def cors_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.allowed_origins.split(",") if origin.strip()]

    model_config = {
        "env_file": ".env",
        "extra": "ignore"
    }

settings = Settings()

