from fastapi import APIRouter, Depends, Form, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.comment import Comment
from app.models.report import Report
from app.core.deps import get_current_user
from app.models.user import User

router = APIRouter(tags=["Comments"])


@router.get("/reports/{report_id}/comments")
def get_comments(
    report_id: int,
    db: Session = Depends(get_db)
):
    comments = (
        db.query(Comment)
        .join(User)
        .filter(Comment.report_id == report_id)
        .order_by(Comment.created_at.desc())
        .all()
    )

    return [
        {
            "id": c.id,
            "content": c.content,
            "created_at": c.created_at,
            "username": c.user.name,   # ✅ THIS IS KEY
        }
        for c in comments
    ]


@router.post("/reports/{report_id}/comments")
def add_comment(
    report_id: int,
    content: str = Form(...),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
):
    report = db.query(Report).filter(Report.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")

    comment = Comment(
        content=content,
        user_id=current_user.id,
        report_id=report_id,
    )
    db.add(comment)
    db.commit()
    return {"detail": "Comment added"}

@router.delete("/{comment_id}")
def delete_comment(
    comment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    comment = db.query(Comment).filter(Comment.id == comment_id).first()

    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")

    if comment.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not allowed")

    db.delete(comment)
    db.commit()

    return {"detail": "Comment deleted"}

@router.put("/{comment_id}")
def update_comment(
    comment_id: int,
    content: str = Form(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    comment = db.query(Comment).filter(Comment.id == comment_id).first()

    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")

    if comment.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not allowed")

    comment.content = content
    db.commit()
    db.refresh(comment)

    return comment


