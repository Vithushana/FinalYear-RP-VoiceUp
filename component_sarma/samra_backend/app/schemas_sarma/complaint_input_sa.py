from pydantic import BaseModel
from typing import Optional

class ComplaintInput(BaseModel):
    category: str
    text: str
    expand_text: bool = True

    # NEW: link input
    location_link: Optional[str] = None

    # make lat/lon optional (because link can fill it)
    latitude: Optional[float] = None
    longitude: Optional[float] = None
