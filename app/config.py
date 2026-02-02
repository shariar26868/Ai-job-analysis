import os
from dotenv import load_dotenv
from pydantic_settings import BaseSettings

# Load environment variables from .env file
load_dotenv()

class Settings(BaseSettings):
    """Application settings and configuration"""
    
    # OpenAI Configuration
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    openai_model: str = "gpt-4o-mini"  # Cost-effective model
    
    # Application Configuration
    app_name: str = "WireQuote AI Backend"
    app_version: str = "1.0.0"
    debug: bool = os.getenv("DEBUG", "True").lower() == "true"
    
    # Server Configuration
    host: str = os.getenv("HOST", "0.0.0.0")
    port: int = int(os.getenv("PORT", 8000))
    
    # CORS Configuration
    allowed_origins: str = os.getenv(
        "ALLOWED_ORIGINS", 
        "http://localhost:3000,http://localhost:5173,http://localhost:8080"
    )
    
    @property
    def cors_origins(self) -> list[str]:
        """Parse CORS origins from comma-separated string"""
        return [origin.strip() for origin in self.allowed_origins.split(",")]
    
    # Business Logic Configuration
    base_hourly_rate: float = 100.0  # £100 per hour base rate
    emergency_uplift: float = 0.50  # 50% extra for emergency
    call_out_fee: float = 65.0  # £65 call-out fee
    
    class Config:
        env_file = ".env"
        case_sensitive = False

# Create settings instance
settings = Settings()

# Validate OpenAI API key
if not settings.openai_api_key:
    raise ValueError("OPENAI_API_KEY is not set in environment variables")