
from fastapi import APIRouter, Depends
from app.core.deps import get_current_user
from app.schemas.user import UserResponse

router = APIRouter(prefix="/users", tags=["Users"])

@router.get("/me", response_model=UserResponse)
def get_my_profile(current_user = Depends(get_current_user)):
    return current_user
