"""Application configuration for the ticket summarizer.

This module defines the :class:`Settings` object used throughout the
application for environment-based configuration.
"""

from pydantic import BaseSettings


class Settings(BaseSettings):
    """Central configuration managed via environment variables."""

    model: str = "gpt-4o-mini"
    model_context_window: int = 128_000
    model_response_margin: int = 2_000
    chunk_overlap: int = 50
    rate_limit_per_minute: int = 60
    csv_delimiter: str = ","

    @property
    def max_chunk_tokens(self) -> int:
        """Calculates the max tokens available for a chunk of tickets."""
        return self.model_context_window - self.model_response_margin

    class Config:
        env_prefix = "SUMM_"


settings = Settings()
