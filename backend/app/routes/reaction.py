from fastapi import APIRouter, Depends, Form, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.reaction import Reaction
from app.models.report import Report
from app.core.deps import get_current_user

router = APIRouter(tags=["Reactions"])


@router.post("/reports/{report_id}/reaction")
def react(
    report_id: int,
    type: str = Form(...),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
):
    if type not in ("like", "dislike"):
        raise HTTPException(status_code=400, detail="Invalid reaction type")

    report = db.query(Report).filter(Report.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")

    existing = db.query(Reaction).filter(
        Reaction.report_id == report_id,
        Reaction.user_id == current_user.id,
    ).first()

    if existing:
        existing.type = type
    else:
        db.add(Reaction(
            report_id=report_id,
            user_id=current_user.id,
            type=type,
        ))

    db.commit()
    return {"detail": "Reaction saved"}

@router.get("/reports/{report_id}/reactions")
def get_reactions(
    report_id: int,
    db: Session = Depends(get_db),
):
    likes = (
        db.query(Reaction)
        .filter(Reaction.report_id == report_id, Reaction.type == "like")
        .count()
    )

    dislikes = (
        db.query(Reaction)
        .filter(Reaction.report_id == report_id, Reaction.type == "dislike")
        .count()
    )

    return {
        "likes": likes,
        "dislikes": dislikes
    }
