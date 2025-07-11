"""Application configuration for the ticket summarizer.

This module defines the :class:`Settings` object used throughout the
application for environment-based configuration.
"""

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Central configuration managed via environment variables."""

    model_config = SettingsConfigDict(env_prefix="SUMM_", frozen=True)

    model: str = "gpt-4o-mini"
    model_context_window: int = 128_000
    model_response_margin: int = 2_000
    chunk_overlap: int = 50
    rate_limit_per_minute: int = 60
    csv_delimiter: str = ","

    @field_validator("csv_delimiter")
    @classmethod
    def delimiter_must_be_a_single_character(cls, v: str) -> str:
        if len(v) != 1:
            raise ValueError("CSV delimiter must be a single character.")
        return v

    @property
    def max_chunk_tokens(self) -> int:
        """Calculates the max tokens available for a chunk of tickets."""
        return self.model_context_window - self.model_response_margin



settings = Settings()
