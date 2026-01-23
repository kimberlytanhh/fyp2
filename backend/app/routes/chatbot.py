from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
import requests
import os

from app.database import get_db
from app.models.report import Report

router = APIRouter(prefix="/chatbot", tags=["Admin Chatbot"])


# -------- Request / Response --------
class ChatRequest(BaseModel):
    question: str


class ChatResponse(BaseModel):
    answer: str


# -------- Ollama Config --------
OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "phi3:mini"


# -------- Helper: build system snapshot --------
def build_system_snapshot(db: Session) -> str:
    total_reports = db.query(Report).count()

    category_stats = (
        db.query(Report.final_category, Report.id)
        .all()
    )

    status_stats = (
        db.query(Report.status, Report.id)
        .all()
    )

    category_count = {}
    for cat, _ in category_stats:
        key = cat or "Uncategorized"
        category_count[key] = category_count.get(key, 0) + 1

    status_count = {}
    for status, _ in status_stats:
        key = status or "Unknown"
        status_count[key] = status_count.get(key, 0) + 1

    category_summary = ", ".join(
        f"{k} ({v})" for k, v in category_count.items()
    ) or "No data available"

    status_summary = ", ".join(
        f"{k} ({v})" for k, v in status_count.items()
    ) or "No data available"

    return f"""
SYSTEM SNAPSHOT:
- Total reports: {total_reports}
- Reports by category: {category_summary}
- Reports by status: {status_summary}
""".strip()


# -------- Admin Chatbot Endpoint --------
@router.post("/admin", response_model=ChatResponse)
def admin_chatbot(
    payload: ChatRequest,
    db: Session = Depends(get_db)
):
    snapshot = build_system_snapshot(db)

    prompt = f"""
You are a professional system analyst assisting city administrators.

Rules:
- Use ONLY the system snapshot.
- Do NOT invent data.
- If the answer is not available, say so clearly.

{snapshot}

ADMIN QUESTION:
{payload.question}

Provide a concise, factual answer in plain English.
""".strip()

    try:
        response = requests.post(
            OLLAMA_URL,
            json={
                "model": OLLAMA_MODEL,
                "prompt": prompt,
                "stream": False
            },
            timeout=60
        )
        response.raise_for_status()

        result = response.json()
        return {"answer": result.get("response", "No response.")}

    except Exception as e:
        return {"answer": f"Error generating response: {str(e)}"}
