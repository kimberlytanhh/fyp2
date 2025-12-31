from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.notification import Notification
from app.core.deps import get_current_user

router = APIRouter(prefix="/notifications", tags=["Notifications"])

@router.get("/")
def get_notifications(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    notes = (
        db.query(Notification)
        .filter(Notification.user_id == current_user.id)
        .order_by(Notification.created_at.desc())
        .all()
    )

    return [
        {
            "id": n.id,
            "actor": n.actor_name,
            "type": n.type,
            "report_id": n.report_id,
            "is_read": n.is_read,
            "created_at": n.created_at
        }
        for n in notes
    ]

@router.post("/{notification_id}/read")
def mark_as_read(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    n = (
        db.query(Notification)
        .filter(Notification.id == notification_id,
                Notification.user_id == current_user.id)
        .first()
    )

    if n:
        n.is_read = True
        db.commit()

    return {"detail": "ok"}
