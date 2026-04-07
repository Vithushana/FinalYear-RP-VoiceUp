from sqlalchemy import Column, Integer, String, Float, DateTime, Text
from app.database_sarma import Base
from datetime import datetime

class Complaint(Base):
    __tablename__ = "complaints"

    id = Column(Integer, primary_key=True)
    category = Column(String)
    text_original = Column(Text)
    text_expanded = Column(Text)

    latitude = Column(Float)
    longitude = Column(Float)
    location_link = Column(String, nullable=True)

    # store OSM snapshot (cached)
    osm_poi_list_json = Column(Text, nullable=True)
    osm_road_class = Column(String, nullable=True)
    osm_alternate_routes_count = Column(Integer, nullable=True)
    osm_nearest_alt_crossing_km = Column(Float, nullable=True)
    osm_junction_density = Column(Integer, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Priority assessment fields
    priority_level = Column(Integer, nullable=True)
    priority_score = Column(Float, nullable=True)
