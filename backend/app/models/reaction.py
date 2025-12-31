from sqlalchemy import Column, Integer, String, ForeignKey, UniqueConstraint
from app.database import Base

class Reaction(Base):
    __tablename__ = "reactions"

    id = Column(Integer, primary_key=True)
    type = Column(String, nullable=False)  # "like" or "dislike"

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    report_id = Column(Integer, ForeignKey("reports.id"), nullable=False)

    __table_args__ = (
        UniqueConstraint("user_id", "report_id", name="unique_user_report"),
    )
