from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
import shutil
import os

from app.database import SessionLocal
from app.models.report import Report
from app.models.user import User
from app.ai.text_classifier import predict_text_category
from app.schemas.report import (
    ReportCreate,
    ReportResponse, AdminCategoryUpdate,
    ReportStatusUpdate,
)
from sqlalchemy import func
from app.core.deps import get_current_user, require_admin
from app.ai.text_classifier import predict_text_category

router = APIRouter(prefix="/reports", tags=["Reports"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Create report (uses multipart/form-data because of image upload)
@router.post("/", response_model=ReportResponse)
def create_report(
    title: str = Form(...),
    description: str = Form(...),
    location: str = Form(...),
    longitude: float = Form(...),
    latitude: float = Form(...),
    image: UploadFile | None = File(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    image_path = None

    # ✅ ONLY save image if it exists
    if image:
        os.makedirs("uploads", exist_ok=True)
        image_path = f"uploads/{image.filename}"

        with open(image_path, "wb") as buffer:
            shutil.copyfileobj(image.file, buffer)

        # --- AI TEXT CATEGORY PREDICTION ---
    combined_text = f"{title} {description}".strip()

    text_pred = predict_text_category(combined_text)

    # Text-only = suggestion only (no auto-confirm)
    text_category = text_pred["category"]
    text_confidence = text_pred["confidence"]

    final_category = None
    needs_review = True

    new_report = Report(
        title=title,
        description=description,
        location=location,
        latitude=latitude,
        longitude=longitude,
        image_path=image_path,
        user_id=current_user.id,

        text_category=text_category,
        text_confidence=text_confidence,
        final_category=final_category,
        needs_review=needs_review,
    )

    db.add(new_report)
    db.commit()
    db.refresh(new_report)

    return new_report

@router.get("/public")
def public_reports(
    db: Session = Depends(get_db),
    status: str | None = None,
    sort: str = "newest"
):
    q = db.query(Report).join(User)

    if status:
        q = q.filter(Report.status == status)

    if sort == "oldest":
        q = q.order_by(Report.created_at.asc())
    else:
        q = q.order_by(Report.created_at.desc())

    reports = q.all()   

    return [            
        {
            "id": r.id,
            "title": r.title,
            "description": r.description,
            "location": r.location,
            "status": r.status,
            "created_at": r.created_at,
            "image_path": r.image_path,
            "username": r.user.name,   
        }
        for r in reports
    ]

@router.get("/public/{report_id}")
def public_report_detail(
    report_id: int,
    db: Session = Depends(get_db)
):
    report = (
        db.query(Report)
        .join(User)
        .filter(Report.id == report_id)
        .first()
    )

    if not report:
        raise HTTPException(status_code=404, detail="Report not found")

    return {
        "id": report.id,
        "title": report.title,
        "description": report.description,
        "location": report.location,
        "status": report.status,
        "created_at": report.created_at,
        "image_path": report.image_path,
        "username": report.user.name,  
    }

# View own reports
@router.get("/me", response_model=list[ReportResponse])
def get_my_reports(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return (
        db.query(Report)
        .filter(Report.user_id == current_user.id)
        .all()
    )

@router.get("/map")
def get_reports_for_map(db: Session = Depends(get_db)):
    reports = db.query(Report).all()

    return [
        {
            "id": r.id,
            "title": r.title,
            "status": r.status,
            "category": r.predicted_category,
            "latitude": r.latitude,
            "longitude": r.longitude,
        }
        for r in reports
    ]

@router.get("/{report_id}", response_model=ReportResponse)
def get_report(
    report_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    report = db.query(Report).filter(Report.id == report_id).first()

    if not report:
        raise HTTPException(status_code=404, detail="Report not found")

    if report.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not allowed")

    return report

# Update own report
@router.put("/{report_id}", response_model=ReportResponse)
def update_report(
    report_id: int,
    title: str = Form(...),
    description: str = Form(...),
    location: str = Form(...),
    image: UploadFile | None = File(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    report = db.query(Report).filter(Report.id == report_id).first()

    if not report:
        raise HTTPException(status_code=404, detail="Report not found")

    if report.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")

    report.title = title
    report.description = description
    report.location = location

    if image:
        os.makedirs("uploads", exist_ok=True)
        image_path = f"uploads/{image.filename}"
        with open(image_path, "wb") as buffer:
            shutil.copyfileobj(image.file, buffer)
        report.image_path = image_path

    db.commit()
    db.refresh(report)

    return report


# Delete own report
@router.delete("/{report_id}")
def delete_report(
    report_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    report = db.query(Report).filter(Report.id == report_id).first()

    if not report:
        raise HTTPException(status_code=404, detail="Report not found")

    if report.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not allowed")

    # Optional: delete image file
    if report.image_path and os.path.exists(report.image_path):
        os.remove(report.image_path)

    db.delete(report)
    db.commit()

    return {"detail": "Report deleted"}


# Admin: view all reports
@router.get("/", response_model=list[ReportResponse])
def get_all_reports(
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    return db.query(Report).all()


# Admin: update report status
@router.patch("/{report_id}/status", response_model=ReportResponse)
def update_report_status(
    report_id: int,
    payload: ReportStatusUpdate,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    report = db.query(Report).filter(Report.id == report_id).first()

    if not report:
        raise HTTPException(status_code=404, detail="Report not found")

    report.status = payload.status
    db.commit()
    db.refresh(report)

    return report

# =========================
# Admin Dashboard Summary (NO AUTH FOR NOW)
# =========================
@router.get("/admin/summary")
def admin_dashboard_summary(
    db: Session = Depends(get_db),
):
    total_reports = db.query(Report).count()

    pending_review = (
        db.query(Report)
        .filter(Report.needs_review == True)
        .count()
    )

    status_counts = (
        db.query(Report.status, db.func.count(Report.id))
        .group_by(Report.status)
        .all()
    )

    return {
        "total_reports": total_reports,
        "pending_review": pending_review,
        "status_counts": {
            status: count for status, count in status_counts
        }
    }

# =========================
# Admin: confirm / override category (NO AUTH)
# =========================
@router.patch("/{report_id}/category", response_model=ReportResponse)
def admin_update_category(
    report_id: int,
    payload: AdminCategoryUpdate,
    db: Session = Depends(get_db),
):
    report = db.query(Report).filter(Report.id == report_id).first()

    if not report:
        raise HTTPException(status_code=404, detail="Report not found")

    report.final_category = payload.final_category
    report.needs_review = False

    db.commit()
    db.refresh(report)

    return report

@router.get("/admin/all")
def get_all_reports_for_admin(db: Session = Depends(get_db)):
    return db.query(Report).order_by(Report.created_at.desc()).all()

@router.get("/admin/stats")
def get_admin_dashboard_stats(db: Session = Depends(get_db)):
    total = db.query(Report).count()
    pending = db.query(Report).filter(Report.needs_review == True).count()
    resolved = db.query(Report).filter(Report.status == "resolved").count()

    return {
        "total_reports": total,
        "pending_review": pending,
        "resolved": resolved
    }

@router.get("/admin/analytics/categories")
def analytics_by_category(db: Session = Depends(get_db)):
    results = (
        db.query(Report.final_category, func.count(Report.id))
        .group_by(Report.final_category)
        .all()
    )

    return {
        "labels": [r[0] if r[0] else "Unconfirmed" for r in results],
        "counts": [r[1] for r in results]
    }







