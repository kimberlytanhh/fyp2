from fastapi import FastAPI
from app.database import Base, engine
from fastapi.staticfiles import StaticFiles
from app.models import user, report as report_model
from app.routes import auth, report as report_routes
from app.routes import analytics, user
from fastapi.middleware.cors import CORSMiddleware
from app.routes import comment, reaction, notifications




app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5500",
        "http://localhost:5500",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)

app.include_router(auth.router)
app.include_router(report_routes.router)
app.include_router(analytics.router)
app.include_router(user.router)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")
app.include_router(comment.router)
app.include_router(reaction.router)
app.include_router(notifications.router)


@app.get("/health")
def health():
    return {"status": "Backend is running safely"}
