"""Business logic for short-code generation and persistence."""
import secrets
import string

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.config import MAX_COLLISION_RETRIES, SHORT_CODE_LENGTH
from app.models import URLRecord

ALPHABET = string.ascii_letters + string.digits  # 62 possible characters


class ShortCodeGenerationError(Exception):
    """Raised when repeated generated codes collide with existing records."""


def generate_short_code(length: int = SHORT_CODE_LENGTH) -> str:
    """Generate a cryptographically strong random Base62-like code."""
    if length < 1:
        raise ValueError("Short-code length must be positive.")
    return "".join(secrets.choice(ALPHABET) for _ in range(length))


def create_url_record(db: Session, original_url: str) -> URLRecord:
    """Save a URL, retrying if a generated code collides with a unique code."""
    for _ in range(MAX_COLLISION_RETRIES):
        record = URLRecord(
            original_url=original_url,
            short_code=generate_short_code(),
        )
        db.add(record)
        try:
            db.commit()
            db.refresh(record)
            return record
        except IntegrityError:
            db.rollback()
            # The unique short_code constraint is the final authority for
            # uniqueness. Retrying handles the extremely unlikely collision.
    raise ShortCodeGenerationError(
        "Could not generate a unique short code. Please try again."
    )
