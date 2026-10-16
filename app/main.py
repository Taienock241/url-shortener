"""FastAPI application entry point."""
import os
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app.database import Base, engine
from app import models  # noqa: F401 - registers ORM models with Base
from app.routes import router

app = FastAPI(
    title="URL Shortener API",
    description="Create short URLs, inspect them, and redirect to original destinations.",
    version="1.0.0",
)

FRONTEND_DIR = Path(__file__).resolve().parent.parent / "frontend"
app.mount("/assets", StaticFiles(directory=FRONTEND_DIR), name="frontend")

@app.get("/", include_in_schema=False)
def dashboard() -> FileResponse:
    return FileResponse(FRONTEND_DIR / "index.html")


@app.get("/health", tags=["health"])
def health_check() -> dict[str, str]:
    return {"message": "URL Shortener API is running."}


@app.get("/health/database", tags=["health"])
def database_health() -> JSONResponse:
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        return JSONResponse(status_code=200, content={"database": "ok"})
    except SQLAlchemyError:
        return JSONResponse(
            status_code=503,
            content={"database": "unavailable"},
        )


@app.on_event("startup")
def create_tables_for_local_development() -> None:
    """Create tables automatically for this course MVP.

    Tests set TESTING=1 and use their own isolated database. For production,
    use Alembic migrations instead of create_all().
    """
    if os.getenv("TESTING") == "1":
        return
    Base.metadata.create_all(bind=engine)


app.include_router(router)
