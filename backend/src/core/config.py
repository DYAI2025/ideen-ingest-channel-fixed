"""
Configuration Settings for Ideen Ingest Channel
"""

from pydantic_settings import BaseSettings
from pathlib import Path
from typing import Optional, List
import os


class Settings(BaseSettings):
    """Application settings"""

    # API Settings
    app_name: str = "Ideen Ingest Channel"
    app_version: str = "0.1.0"
    debug: bool = True

    # Server Settings
    host: str = "0.0.0.0"
    port: int = 9999

    # File Upload Settings
    upload_dir: Path = Path.home() / "ideen-growth-system" / "seeds"
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    allowed_extensions: str = ".md,.txt,.json,.yaml,.yml"

    # GBrain Settings
    gbrain_source: str = "ideas"
    gbrain_path: Path = Path.home() / ".gbrain"
    gbrain_command: str = "gbrain"

    # SSH Settings
    ssh_enabled: bool = True
    ssh_port: int = 2222
    ssh_host: str = "localhost"

    # Graph Settings
    graph_cache_ttl: int = 300  # 5 minutes
    max_nodes: int = 100
    max_depth: int = 3

    # Slack Settings
    slack_signing_secret: Optional[str] = None
    slack_bot_token: Optional[str] = None
    slack_app_level_token: Optional[str] = None

    # Database Settings
    db_host: str = "localhost"
    db_port: int = 5432
    db_name: str = "slack_integration"
    db_user: str = "postgres"
    db_password: str = "postgres"

    @property
    def database_url(self) -> str:
        """Construct PostgreSQL database URL"""
        return f"postgresql://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "allow"  # Allow extra fields


settings = Settings()
