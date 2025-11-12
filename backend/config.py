"""Configuration management for the application."""
import os
from typing import List
from functools import lru_cache


class Settings:
    """Application settings loaded from environment variables."""
    
    def __init__(self):
        # Database
        self.database_url: str = os.getenv(
            "DATABASE_URL",
            "sqlite:///./moderation.db"
        )
        
        # Application
        self.environment: str = os.getenv("ENVIRONMENT", "development")
        self.log_level: str = os.getenv("LOG_LEVEL", "INFO")
        self.api_key: str = os.getenv("API_KEY", "")
        
        # CORS
        self.cors_origins: str = os.getenv(
            "CORS_ORIGINS",
            "http://localhost:8000,http://127.0.0.1:8000"
        )
        
        # Security
        self.rate_limit_enabled: bool = os.getenv("RATE_LIMIT_ENABLED", "false").lower() == "true"
        self.rate_limit_per_minute: int = int(os.getenv("RATE_LIMIT_PER_MINUTE", "60"))
        
        # AI Service
        self.openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
        self.ai_service_url: str = os.getenv("AI_SERVICE_URL", "")
        
        # Monitoring
        self.sentry_dsn: str = os.getenv("SENTRY_DSN", "")
        self.prometheus_enabled: bool = os.getenv("PROMETHEUS_ENABLED", "true").lower() == "true"
        
        # Clerk Authentication
        self.clerk_secret_key: str = os.getenv("CLERK_SECRET_KEY", "")
        self.clerk_publishable_key: str = os.getenv("CLERK_PUBLISHABLE_KEY", "")
        self.clerk_enabled: bool = os.getenv("CLERK_ENABLED", "false").lower() == "true"
    
    @property
    def cors_origins_list(self) -> List[str]:
        """Parse CORS origins from comma-separated string."""
        return [origin.strip() for origin in self.cors_origins.split(",")]
    
    @property
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.environment.lower() == "production"
    
    @property
    def is_development(self) -> bool:
        """Check if running in development environment."""
        return self.environment.lower() == "development"


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()

