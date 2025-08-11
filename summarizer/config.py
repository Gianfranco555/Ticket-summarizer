"""Application configuration for the ticket summarizer.

This module defines the :class:`Settings` object used throughout the
application for environment-based configuration.
"""

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Central configuration managed via environment variables."""

    model_config = SettingsConfigDict(env_prefix="SUMM_")

    openai_api_key: str | None = None
    model: str = "gpt-5"
    model_context_window: int = 128_000
    chunk_max_tokens: int = 15000
    model_max_response_tokens: int = 512
    model_response_token_ratio: int = 8
    chunk_overlap: int = 50
    rate_limit_per_minute: int = 60
    csv_delimiter: str = ","

    @field_validator("csv_delimiter")
    @classmethod
    def delimiter_must_be_a_single_character(cls, v: str) -> str:
        if len(v) != 1:
            raise ValueError("CSV delimiter must be a single character.")
        return v



settings = Settings()
