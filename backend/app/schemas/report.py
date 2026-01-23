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
    text_category: str | None
    text_confidence: float | None
    final_category: str | None
    needs_review: bool

class AdminCategoryUpdate(BaseModel):
        final_category: str

model_config = {"from_attributes": True}