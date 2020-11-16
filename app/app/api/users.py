from typing import Optional

from app.app.backend import ObjectNotFound
from app.app.backend.user import get_user_info as get_info
from fastapi import APIRouter, HTTPException
from app.app.src.schemas import user

router = APIRouter()


# Add methods for interacting with desktop


@router.get("/get_user_info", response_model=user.UserOut)
async def get_user_info(current_user: Optional[str], user_id: str):
    try:
        user_info = await get_info(current_user=current_user, user_id=user_id)
        return user_info
    except ObjectNotFound:
        raise HTTPException(status_code=404, detail="Sorry, page not found")
