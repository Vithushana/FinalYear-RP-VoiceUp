from pydantic import BaseModel

class OfficerView(BaseModel):
    priority_level: int
    risk_category: str
    recommended_action_time: str
    context_summary: str
    explanation: list[str]

    
    # Optional fields for detailed officer view
    gis: Optional[dict[str, Any]] = None
    recurring: Optional[dict[str, Any]] = None
    summary: Optional[dict[str, Any]] = None
    complaint: Optional[dict[str, Any]] = None
    location: Optional[dict[str, Any]] = None
    why_this_priority: Optional[list[str]] = None
    ai_suggestion: Optional[dict[str, Any]] = None
    track: Optional[dict[str, Any]] = None