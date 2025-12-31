from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database import SessionLocal
from app.models.report import Report
from app.core.deps import require_admin

router = APIRouter(prefix="/analytics", tags=["Analytics"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/summary")
def analytics_summary(
    db: Session = Depends(get_db),
    admin = Depends(require_admin),
):
    total_reports = db.query(func.count(Report.id)).scalar()

    status_counts = (
        db.query(Report.status, func.count(Report.id))
        .group_by(Report.status)
        .all()
    )

    return {
        "total_reports": total_reports,
        "reports_by_status": {
            status: count for status, count in status_counts
        },
    }
