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
    
    # Gemini AI
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    DEFAULT_GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-flash-lite-latest")
    FALLBACK_GEMINI_MODEL: str = "gemini-3.5-flash-lite"
    
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
