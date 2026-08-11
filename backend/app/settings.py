"""
Central configuration management for CareerPilot AI.

All environment variables, defaults, and settings are defined here.
This ensures single source of truth and early validation.
"""

import os
from typing import Optional
from dotenv import load_dotenv

# Load .env file
load_dotenv()


class Settings:
    """Application settings loaded from environment variables."""

    # ==================== API Keys ====================
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    ADZUNA_APP_ID: str = os.getenv("ADZUNA_APP_ID", "")
    ADZUNA_APP_KEY: str = os.getenv("ADZUNA_APP_KEY", "")
    RAPIDAPI_KEY: str = os.getenv("RAPIDAPI_KEY", "")

    # ==================== Database ====================
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql://postgres:postgres@localhost:5433/postgres"
    )

    # ==================== LLM Configuration ====================
    # Model names
    GROQ_PLANNER_MODEL: str = os.getenv("GROQ_PLANNER_MODEL", "llama-3.3-70b-versatile")
    GROQ_AGENT_MODEL: str = os.getenv("GROQ_AGENT_MODEL", "llama-3.3-70b-versatile")
    GROQ_REPORT_MODEL: str = os.getenv("GROQ_REPORT_MODEL", "llama-3.3-70b-versatile")

    # LLM Timeouts (seconds)
    LLM_TIMEOUT: int = int(os.getenv("LLM_TIMEOUT", "30"))
    LLM_RETRY_ATTEMPTS: int = int(os.getenv("LLM_RETRY_ATTEMPTS", "3"))
    LLM_RETRY_BACKOFF: float = float(os.getenv("LLM_RETRY_BACKOFF", "1.5"))
    LLM_RETRY_JITTER: float = float(os.getenv("LLM_RETRY_JITTER", "0.1"))

    # Temperature for structured output (lower = more consistent)
    LLM_TEMPERATURE_STRUCTURED: float = float(
        os.getenv("LLM_TEMPERATURE_STRUCTURED", "0.1")
    )
    # Temperature for creative tasks (higher = more diverse)
    LLM_TEMPERATURE_CREATIVE: float = float(
        os.getenv("LLM_TEMPERATURE_CREATIVE", "0.7")
    )

    # ==================== API Configuration ====================
    # Adzuna API limits
    ADZUNA_MAX_RESULTS: int = int(os.getenv("ADZUNA_MAX_RESULTS", "50"))
    ADZUNA_API_TIMEOUT: int = int(os.getenv("ADZUNA_API_TIMEOUT", "15"))

    # Server
    SERVER_HOST: str = os.getenv("SERVER_HOST", "0.0.0.0")
    SERVER_PORT: int = int(os.getenv("SERVER_PORT", "8000"))

    # CORS
    CORS_ORIGINS: list = os.getenv(
        "CORS_ORIGINS",
        "http://localhost:5173,http://localhost:3000"
    ).split(",")

    # ==================== Logging ====================
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FORMAT: str = os.getenv(
        "LOG_FORMAT",
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    # ==================== Application Behavior ====================
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    DEBUG: bool = ENVIRONMENT == "development"

    # Feature flags
    ENABLE_STRUCTURED_OUTPUT_FALLBACK: bool = (
        os.getenv("ENABLE_STRUCTURED_OUTPUT_FALLBACK", "true").lower() == "true"
    )
    ENABLE_RESPONSE_CACHING: bool = (
        os.getenv("ENABLE_RESPONSE_CACHING", "false").lower() == "true"
    )
    ENABLE_LLM: bool = os.getenv("ENABLE_LLM", "false").lower() == "true"

    @classmethod
    def validate(cls) -> list[str]:
        """
        Validate that all required environment variables are set.

        Returns:
            List of missing variables. Empty if all valid.
        """
        missing = []

        if cls.ENABLE_LLM and not cls.GROQ_API_KEY:
            missing.append("GROQ_API_KEY")

        return missing

    @classmethod
    def to_dict(cls) -> dict:
        """Return settings as dictionary (excluding secrets)."""
        return {
            "DATABASE_URL": cls.DATABASE_URL.split("@")[1] if "@" in cls.DATABASE_URL else "***",
            "GROQ_PLANNER_MODEL": cls.GROQ_PLANNER_MODEL,
            "GROQ_AGENT_MODEL": cls.GROQ_AGENT_MODEL,
            "GROQ_REPORT_MODEL": cls.GROQ_REPORT_MODEL,
            "LLM_TIMEOUT": cls.LLM_TIMEOUT,
            "LLM_RETRY_ATTEMPTS": cls.LLM_RETRY_ATTEMPTS,
            "ENVIRONMENT": cls.ENVIRONMENT,
            "LOG_LEVEL": cls.LOG_LEVEL,
            "ENABLE_LLM": cls.ENABLE_LLM,
        }


# Global settings instance
settings = Settings()
