import json
import logging
import traceback
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

# Database and Model imports
from app.database_sarma import SessionLocal
from app.schemas_sarma.complaint_input_sa import ComplaintInput
from app.models_sarma.complaint_sa import Complaint
from app.models_sarma.analysis_result_sa import AnalysisResult

# Service imports
from app.services_sarma.text_expansion_service_sa import expand_complaint_text
from app.services_sarma.location_link_service_sa import get_lat_lon_from_maps_link
from app.services_sarma.osm_fetch_service_sa import fetch_osm_features
from app.services_sarma.gis_usage_service_sa import calculate_hybrid_gis_score

router = APIRouter(prefix="/complaints", tags=["Complaints"])

logger = logging.getLogger(__name__)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 1. NEW: AI EXPANSION ONLY ROUTE
@router.post("/expand")
async def expand_only(payload: dict):
    """
    Indha route dhaan Flutter-la 'Expand with AI' click panna udane Flask vazhiya call aagum.
    """
    text = payload.get("text", "")
    category = payload.get("category", "road") # Default category
    
    if not text:
        raise HTTPException(status_code=400, detail="Text is required for expansion")

    try:
        # AI generate panna expanded text-ah 'expanded_text' key-la return pannum
        expanded = expand_complaint_text(category, text)
        return {
            "status": "success",
            "expanded_text": expanded 
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 2. UPDATED SUBMIT ROUTE
@router.post("/submit")
def submit_complaint(payload: ComplaintInput, db: Session = Depends(get_db)):
    try:
        # A. Maps link-la irundhu coordinates edukka
        if (payload.latitude is None or payload.longitude is None) and payload.location_link:
            try:
                lat, lon = get_lat_lon_from_maps_link(payload.location_link)
                payload.latitude = lat
                payload.longitude = lon
            except Exception as e:
                raise HTTPException(status_code=400, detail=f"Location link error: {str(e)}")

        if payload.latitude is None or payload.longitude is None:
            raise HTTPException(status_code=422, detail="Latitude/Longitude required")

        lat = float(payload.latitude)
        lon = float(payload.longitude)

        # B. Text Logic: User expand check pannaal AI text use pannum, illai-na raw text
        final_text = (
            expand_complaint_text(payload.category, payload.text)
            if payload.expand_text
            else payload.text
        )

        # C. GIS and OSM Processing with Safety Catch
        # This prevents the 500 Error if the map fetch takes too long.
        try:
            osm = fetch_osm_features(lat, lon)
            gis_results = calculate_hybrid_gis_score(
                latitude=lat,
                longitude=lon,
                poi_list=osm.get("poi_list", []),
                road_class=osm.get("road_class", "unknown"),
                alternate_routes_count=int(osm.get("alternate_routes_count", 0)),
                nearest_alt_crossing_km=float(osm.get("nearest_alt_crossing_km", 99.0)),
                junction_density=int(osm.get("junction_density", 0)),
                nearby_complaint_count=1,
                category=payload.category,
                expanded_text=final_text 
            )
        except Exception as e:
            # If the map server is slow, the system "fails gracefully" instead of crashing
            print(f"GIS Fetch failed or timed out: {e}")
            gis_results = {
                "gis_score": 0,
                "gis_summary": "Live GIS data currently unavailable. Using baseline priority level."
            }
            osm = {"road_class": "unknown"}
        # D. Save Complaint to DB
        complaint = Complaint(
            category=payload.category,
            text_original=payload.text,
            text_expanded=final_text, # AI expansion store aagum
            latitude=lat,
            longitude=lon,
            location_link=payload.location_link,


            osm_road_class=osm.get("road_class", "unknown"),
            osm_poi_list_json=json.dumps(osm.get("poi_list", [])),
            osm_alternate_routes_count=int(osm.get("alternate_routes_count", 0)),
            osm_nearest_alt_crossing_km=float(osm.get("nearest_alt_crossing_km", 99.0)),
            osm_junction_density=int(osm.get("junction_density", 0)),
        )
        db.add(complaint)
        db.commit()
        db.refresh(complaint)

        # E. Save Analysis Results
        analysis = AnalysisResult(
            complaint_id=complaint.id,
            priority_score=gis_results["gis_score"],
            explanation=gis_results["gis_summary"]
        )
        db.add(analysis)
        db.commit()

        return {
            "status": "success",
            "complaint_id": complaint.id,
            "priority_score": gis_results["gis_score"],
            "message": "Complaint processed with GIS Priority"
        }

    except HTTPException:
        # Re-raise deliberate HTTPExceptions so FastAPI handles them as intended
        raise
    except Exception as e:
        # Log full traceback to server logs and return a 500 with error text
        logger.exception("Unhandled error in submit_complaint: %s", str(e))
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

# 3. LIST ALL ROUTE
@router.get("/all")
def list_all(db: Session = Depends(get_db)):
    return db.query(Complaint).order_by(Complaint.created_at.desc()).all()


# Note: lightweight `last_update` endpoint removed. Frontend polling cleaned up.