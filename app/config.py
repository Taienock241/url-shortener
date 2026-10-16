"""Application configuration loaded from environment variables."""
import os

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg://urlshortener:Ratt2580!!!!@localhost:5432/url_shortener",
)
BASE_URL = os.getenv("BASE_URL", "http://127.0.0.1:8000").rstrip("/")
SHORT_CODE_LENGTH = int(os.getenv("SHORT_CODE_LENGTH", "7"))
MAX_COLLISION_RETRIES = int(os.getenv("MAX_COLLISION_RETRIES", "5"))
