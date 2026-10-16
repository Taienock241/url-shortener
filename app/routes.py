"""HTTP endpoints for creating, retrieving, and redirecting URLs."""
from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from fastapi.responses import RedirectResponse
from sqlalchemy import desc, update
from sqlalchemy.orm import Session

from app.config import BASE_URL
from app.database import get_db
from app.models import URLRecord
from app.schemas import URLCreate, URLCreated, URLInfo, URLListItem
from app.services import ShortCodeGenerationError, create_url_record

router = APIRouter()


@router.post("/api/urls", response_model=URLCreated, status_code=status.HTTP_201_CREATED)
def create_short_url(payload: URLCreate, db: Session = Depends(get_db)) -> URLCreated:
    try:
        record = create_url_record(db, payload.url)
    except ShortCodeGenerationError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc

    return URLCreated(
        original_url=record.original_url,
        short_code=record.short_code,
        short_url=f"{BASE_URL}/{record.short_code}",
        created_at=record.created_at,
    )


@router.get("/api/urls", response_model=list[URLListItem])
def list_urls(
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
) -> list[URLListItem]:
    """Return recent links for the dashboard, newest first."""
    records = (
        db.query(URLRecord)
        .order_by(desc(URLRecord.created_at), desc(URLRecord.id))
        .offset(offset)
        .limit(limit)
        .all()
    )
    return [
        URLListItem(
            original_url=record.original_url,
            short_code=record.short_code,
            short_url=f"{BASE_URL}/{record.short_code}",
            created_at=record.created_at,
            click_count=record.click_count,
        )
        for record in records
    ]


@router.get("/api/urls/{short_code}", response_model=URLInfo)
def get_url_info(short_code: str, db: Session = Depends(get_db)) -> URLInfo:
    record = db.query(URLRecord).filter(URLRecord.short_code == short_code).first()
    if record is None:
        raise HTTPException(status_code=404, detail="Short URL not found.")
    return URLInfo.model_validate(record)


@router.get("/{short_code}", include_in_schema=False)
def redirect_short_url(short_code: str, db: Session = Depends(get_db)) -> Response:
    record = db.query(URLRecord).filter(URLRecord.short_code == short_code).first()
    if record is None:
        raise HTTPException(status_code=404, detail="Short URL not found.")

    # Atomic increment avoids a read-modify-write race between concurrent clicks.
    db.execute(
        update(URLRecord)
        .where(URLRecord.id == record.id)
        .values(click_count=URLRecord.click_count + 1)
    )
    db.commit()
    return RedirectResponse(url=record.original_url, status_code=status.HTTP_302_FOUND)
