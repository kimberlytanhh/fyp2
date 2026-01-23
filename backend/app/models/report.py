from sqlalchemy import Column, Integer, String, Text, ForeignKey, Float, DateTime, Boolean
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import datetime

class Report(Base):
    __tablename__ = "reports"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)

    # Standardised lifecycle: pending -> in_progress -> resolved
    status = Column(String, default="pending", nullable=False)

    # AI fields
    predicted_category = Column(String, nullable=True)
    confidence_score = Column(Float, nullable=True)

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    user = relationship("User", backref="reports")
    location = Column(String, nullable=False)
    latitude = Column(Float, nullable=False)
    longitude=Column(Float, nullable=False)
    image_path = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # AI – text
    text_category = Column(String, nullable=True)
    text_confidence = Column(Float, nullable=True)

    # AI – image
    image_category = Column(String, nullable=True)
    image_confidence = Column(Float, nullable=True)

    # Final decision
    final_category = Column(String, nullable=True)
    needs_review = Column(Boolean, default=True)
