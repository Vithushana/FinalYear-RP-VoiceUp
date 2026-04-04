import json
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database_sarma import SessionLocal
from app.models_sarma.complaint_sa import Complaint
from app.models_sarma.analysis_result_sa import AnalysisResult

from app.services_sarma.recurring_detection_service_sa import detect_recurring_complaints
from app.services_sarma.officer_output_service_sa import build_officer_output
from app.services_sarma.ml_prediction_service_sa import predict_from_text


router = APIRouter(prefix="/officer", tags=["Officer"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/complaint/{complaint_id}")
def officer_view(complaint_id: int, db: Session = Depends(get_db)):

    complaint = db.query(Complaint).filter(Complaint.id == complaint_id).first()
    if not complaint:
        raise HTTPException(status_code=404, detail="Complaint not found")

    # 1) ML prediction
    ml_result = predict_from_text(complaint.text_expanded)

    # 2) Recurring detection (also acts as complaint density)
    recurring_data = detect_recurring_complaints(
        db,
        complaint.category,
        complaint.latitude,
        complaint.longitude
    )

    # 3) Read cached OSM values from DB (NO LIVE FETCH HERE)
    poi_list = []
    raw_poi = getattr(complaint, "osm_poi_list_json", None)
    if raw_poi:
        try:
            poi_list = json.loads(raw_poi)
            if not isinstance(poi_list, list):
                poi_list = []
        except Exception:
            poi_list = []

    road_class = getattr(complaint, "osm_road_class", None) or "unknown"
    alternate_routes_count = int(getattr(complaint, "osm_alternate_routes_count", 0) or 0)
    nearest_alt_crossing_km = float(getattr(complaint, "osm_nearest_alt_crossing_km", 99.0) or 99.0)
    junction_density = int(getattr(complaint, "osm_junction_density", 0) or 0)

    # 4) Build final officer output (Stable hybrid GIS inputs)
    officer_output = build_officer_output(
        complaint_id=complaint.id,
        category=complaint.category,
        expanded_text=complaint.text_expanded,
        latitude=complaint.latitude,
        longitude=complaint.longitude,
        location_link=getattr(complaint, "location_link", None),

        recurring_count=recurring_data["recurring_count"],
        is_recurring=recurring_data["is_recurring"],

        poi_list=poi_list,
        road_class=road_class,
        alternate_routes_count=alternate_routes_count,
        nearest_alt_crossing_km=nearest_alt_crossing_km,
        junction_density=junction_density,
        nearby_complaint_count=recurring_data["recurring_count"],

        ml_result=ml_result
    )

    # 5) OPTIONAL: Update complaint priority fields ONLY if your model has these columns
    if hasattr(complaint, "priority_level"):
        complaint.priority_level = officer_output["summary"]["priority_level"]
    if hasattr(complaint, "priority_score"):
        complaint.priority_score = float(officer_output["summary"]["priority_score"])

    # 6) Upsert analysis_results (avoid duplicate rows)
    analysis = db.query(AnalysisResult).filter(AnalysisResult.complaint_id == complaint.id).first()

    if analysis is None:
        analysis = AnalysisResult(complaint_id=complaint.id)
        db.add(analysis)

    analysis.priority_level = officer_output["summary"]["priority_level"]
    analysis.priority_score = float(officer_output["summary"]["priority_score"])
    analysis.track = officer_output["track"]["track"]
    analysis.gis_summary = officer_output["gis"]["gis_summary"]
    analysis.recurring_count = recurring_data["recurring_count"]
    analysis.is_recurring = recurring_data["is_recurring"]
    analysis.explanation = str(officer_output["why_this_priority"])

    db.commit()

    return officer_output
