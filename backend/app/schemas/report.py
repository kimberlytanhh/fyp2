from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class ReportCreate(BaseModel):
    title: str
    description: str

class ReportStatusUpdate(BaseModel):
    status: str

class ReportResponse(BaseModel):
    id: int
    title: str
    description: str
    location: str 
    status: str
    predicted_category: str | None
    confidence_score: float | None
    image_path: Optional[str]
    created_at: datetime

    model_config = {"from_attributes": True}