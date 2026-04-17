"""
System Configuration — Environment Hardening
============================================
Centralised configuration management using Pydantic BaseSettings.
Loads environment variables with sensible defaults for Cloud Run staging.
"""

import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List


class Settings(BaseSettings):
    """
    Project settings and environment-based configurations.
    """
    # API Metadata
    APP_TITLE: str = "Smart Stadium OS"
    APP_VERSION: str = "2.2.0"
    DEBUG: bool = False

    # Security
    ALLOWED_ORIGINS: str = "http://localhost:3000,http://localhost:5173"  # Comma-separated list for CORS
    RATE_LIMIT_MAX_REQUESTS: int = 30
    RATE_LIMIT_WINDOW: int = 60

    # Firebase
    FIREBASE_DB_URL: str = os.getenv("FIREBASE_DB_URL", "https://smartstadiumos-default-rtdb.firebaseio.com")
    FIREBASE_PROJECT_ID: str = os.getenv("FIREBASE_PROJECT_ID", "smartstadiumos")
    SYNC_TO_FIREBASE: bool = True

    # Cloud Operations
    GCP_PROJECT_ID: str = os.getenv("GOOGLE_CLOUD_PROJECT", "smart-stadium-system")
    LOG_LEVEL: str = "INFO"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    @property
    def cors_origins(self) -> List[str]:
        """Parsed list of allowed CORS origins."""
        if self.ALLOWED_ORIGINS == "*":
            return ["*"]
        return [o.strip() for o in self.ALLOWED_ORIGINS.split(",")]

    def load_elite_secrets(self):
        """
        Dynamically fetches production secrets from GCP Secret Manager.
        Overrides environment defaults for Firebase and JWT configuration.
        """
        try:
            from services.secret_service import secret_service
            
            fb_url = secret_service.get_secret("FIREBASE_DB_URL")
            if fb_url:
                self.FIREBASE_DB_URL = fb_url
                
            gcp_id = secret_service.get_secret("GCP_PROJECT_ID")
            if gcp_id:
                self.GCP_PROJECT_ID = gcp_id
                
        except Exception:
            # Fallback to defaults defined in BaseSettings
            pass

# Singleton instance
settings = Settings()
settings.load_elite_secrets()
