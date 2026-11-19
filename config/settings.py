import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv

# Base paths
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
EXPORTS_DIR = BASE_DIR / "exports"
SAMPLE_DIR = BASE_DIR / "sample_data"

# Create directories if they do not exist
DATA_DIR.mkdir(parents=True, exist_ok=True)
EXPORTS_DIR.mkdir(parents=True, exist_ok=True)
SAMPLE_DIR.mkdir(parents=True, exist_ok=True)

# Load .env file
load_dotenv(BASE_DIR / ".env")

class Settings(BaseSettings):
    APP_NAME: str = "PlotHole OS"
    APP_VERSION: str = "1.0.0"
    TAGLINE: str = "Every Story Has a Logic. We Find Where It Breaks."
    
    # Environment & Debug
    APP_ENV: str = os.getenv("APP_ENV", "development")
    DEBUG: bool = os.getenv("DEBUG", "true").lower() in ("true", "1", "t")
    
    # AI Provider Configuration (NVIDIA NIM)
    NVIDIA_API_KEY: str = os.getenv("NVIDIA_API_KEY", os.getenv("GEMINI_API_KEY", ""))
    NVIDIA_BASE_URL: str = os.getenv("NVIDIA_BASE_URL", "https://integrate.api.nvidia.com/v1")
    DEFAULT_NVIDIA_MODEL: str = os.getenv("NVIDIA_MODEL", "minimaxai/minimax-m3.1-flash")
    FALLBACK_NVIDIA_MODEL: str = "google/gemma-4-31b-it"

    # Backward-compatible aliases
    @property
    def GEMINI_API_KEY(self) -> str:
        return self.NVIDIA_API_KEY

    @property
    def DEFAULT_GEMINI_MODEL(self) -> str:
        return self.DEFAULT_NVIDIA_MODEL

    @property
    def FALLBACK_GEMINI_MODEL(self) -> str:
        return self.FALLBACK_NVIDIA_MODEL
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", f"sqlite:///{BASE_DIR / 'plothole.db'}")
    
    # Upload limits
    MAX_UPLOAD_SIZE_MB: int = 30
    ALLOWED_EXTENSIONS: list[str] = [".pdf", ".txt", ".docx"]
    
    # Long Script Chunking
    CHUNK_SIZE_LINES: int = 250
    CHUNK_OVERLAP_LINES: int = 30
    MAX_SCENES_PER_CHUNK: int = 15
    
    # Detection Thresholds
    MIN_CONFIDENCE_THRESHOLD: float = 0.50
    SEVERITY_LEVELS: list[str] = ["Critical", "High", "Medium", "Low", "Informational"]
    
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
