"""
Configuration settings for the Judge system.
Loads from .env
"""

from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


class JudgeSettings(BaseSettings):
    
    model_config = SettingsConfigDict(
        env_file=Path(__file__).parent / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )
    
    ollama_model: str = "gemma3:12b"
    ollama_base_url: str = "http://localhost:11434"
    ollama_temperature: float = 0.3
    ollama_num_ctx: int = 8192
    
    # Output Configuration
    default_output_format: str = "csv"
    default_output_path: str = "./judge_results"


settings = JudgeSettings()
