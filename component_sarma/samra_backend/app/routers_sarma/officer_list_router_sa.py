from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import extract

from app.database_sarma import SessionLocal
from app.models_sarma.complaint_sa import Complaint

router = APIRouter(prefix="/officer", tags=["Officer"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/complaints")
def list_complaints(
    db: Session = Depends(get_db),
    year: int | None = None,
    month: int | None = Query(default=None, ge=1, le=12),
    category: str | None = None,
    priority_level: int | None = Query(default=None, ge=1, le=3),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=50),
):
    q = db.query(Complaint)

    if category:
        q = q.filter(Complaint.category == category)

    if priority_level is not None:
        q = q.filter(Complaint.priority_level == priority_level)

    if year is not None:
        q = q.filter(extract("year", Complaint.created_at) == year)

    if month is not None:
        q = q.filter(extract("month", Complaint.created_at) == month)

    total = q.count()

    items = (
        q.order_by(Complaint.created_at.desc())
         .offset((page - 1) * page_size)
         .limit(page_size)
         .all()
    )

    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "items": [
            {
                "id": c.id,
                "category": c.category,
                "text_expanded": c.text_expanded,
                "created_at": c.created_at.isoformat() if c.created_at else None,
                "priority_level": c.priority_level,
                "priority_score": c.priority_score,
                "latitude": c.latitude,
                "longitude": c.longitude,
            }
            for c in items
        ],
    }
