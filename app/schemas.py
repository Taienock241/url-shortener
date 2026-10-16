"""Pydantic request and response schemas."""
from datetime import datetime
from urllib.parse import urlsplit

from pydantic import BaseModel, ConfigDict, Field, field_validator


class URLCreate(BaseModel):
    url: str = Field(min_length=1, max_length=2048)

    @field_validator("url")
    @classmethod
    def validate_url(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("URL must not be empty.")
        try:
            parsed = urlsplit(value)
            # Accessing .port also detects malformed port values.
            _ = parsed.port
        except ValueError as exc:
            raise ValueError("URL is malformed.") from exc

        if parsed.scheme.lower() not in {"http", "https"}:
            raise ValueError("Only http and https URLs are allowed.")
        if not parsed.hostname:
            raise ValueError("URL must include a hostname.")
        if any(ch.isspace() for ch in value):
            raise ValueError("URL must not contain whitespace.")
        if parsed.username is not None or parsed.password is not None:
            raise ValueError("URLs containing embedded credentials are not allowed.")
        return value


class URLCreated(BaseModel):
    original_url: str
    short_code: str
    short_url: str
    created_at: datetime


class URLInfo(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    original_url: str
    short_code: str
    created_at: datetime
    click_count: int


class URLListItem(URLInfo):
    """URL metadata returned in the dashboard history."""

    short_url: str
