from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey
from app.database_sarma import Base

class AnalysisResult(Base):
    __tablename__ = "analysis_results"

    id = Column(Integer, primary_key=True)
    complaint_id = Column(Integer, ForeignKey("complaints.id"))

    # priority will be added Day 3
    priority_level = Column(Integer, nullable=True)
    priority_score = Column(Float, nullable=True)
    track = Column(String, nullable=True)

    # GIS context
    near_road = Column(Boolean, default=False)
    near_public_place = Column(Boolean, default=False)
    is_remote_area = Column(Boolean, default=False)
    gis_summary = Column(String)

    # recurring
    recurring_count = Column(Integer, default=0)
    is_recurring = Column(Boolean, default=False)

    explanation = Column(String)
