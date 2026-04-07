from geopy.distance import geodesic
from sqlalchemy.orm import Session
from app.models_sarma.complaint_sa import Complaint

DISTANCE_THRESHOLD_METERS = 200
RECURRING_THRESHOLD_COUNT = 3


def detect_recurring_complaints(
    db: Session,
    category: str,
    latitude: float,
    longitude: float
) -> dict:
    """
    Detects recurring complaints for the SAME category within a distance threshold.
    """
    current = (latitude, longitude)

    # Filter by category so road and garbage don't mix
    all_complaints = db.query(Complaint).filter(Complaint.category == category).all()

    count = 0
    for c in all_complaints:
        if c.latitude is None or c.longitude is None:
            continue

        d = geodesic(current, (c.latitude, c.longitude)).meters
        if d <= DISTANCE_THRESHOLD_METERS:
            count += 1

    return {
        "recurring_count": count,
        "is_recurring": count >= RECURRING_THRESHOLD_COUNT
    }
