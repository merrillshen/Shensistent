"""
Configuration management for Shensistent agent.
"""

import os
from typing import Optional, Dict, Any
from pydantic import BaseSettings, Field
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    """Application settings and configuration."""
    
    # Application
    app_name: str = "Shensistent"
    app_version: str = "0.1.0"
    debug: bool = Field(default=False, env="DEBUG")
    
    # OpenAI Configuration
    openai_api_key: str = Field(..., env="OPENAI_API_KEY")
    openai_model: str = Field(default="gpt-4", env="OPENAI_MODEL")
    openai_temperature: float = Field(default=0.7, env="OPENAI_TEMPERATURE")
    
    # Database Configuration
    database_url: str = Field(default="sqlite:///./shensistent.db", env="DATABASE_URL")
    redis_url: str = Field(default="redis://localhost:6379", env="REDIS_URL")
    
    # API Keys for Data Collection
    github_token: Optional[str] = Field(default=None, env="GITHUB_TOKEN")
    twitter_bearer_token: Optional[str] = Field(default=None, env="TWITTER_BEARER_TOKEN")
    linkedin_username: Optional[str] = Field(default=None, env="LINKEDIN_USERNAME")
    linkedin_password: Optional[str] = Field(default=None, env="LINKEDIN_PASSWORD")
    
    # News API
    news_api_key: Optional[str] = Field(default=None, env="NEWS_API_KEY")
    
    # Scheduling
    update_frequency_hours: int = Field(default=24, env="UPDATE_FREQUENCY_HOURS")
    
    # Security
    secret_key: str = Field(..., env="SECRET_KEY")
    algorithm: str = Field(default="HS256", env="ALGORITHM")
    access_token_expire_minutes: int = Field(default=30, env="ACCESS_TOKEN_EXPIRE_MINUTES")
    
    # Data Collection Settings
    max_repositories: int = Field(default=100, env="MAX_REPOSITORIES")
    max_articles: int = Field(default=50, env="MAX_ARTICLES")
    max_social_posts: int = Field(default=200, env="MAX_SOCIAL_POSTS")
    
    class Config:
        env_file = ".env"
        case_sensitive = False

# Global settings instance
settings = Settings()

def get_settings() -> Settings:
    """Get application settings."""
    return settings
