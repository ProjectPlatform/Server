from typing import Optional

from app.app.backend import ObjectNotFound
from app.app.backend.user import get_user_info as get_info
from fastapi import APIRouter, HTTPException, Depends
from app.app.src.schemas import user
from app.app.src.security import decode_token

router = APIRouter()


# Add methods for interacting with desktop


@router.get("/get_user_info", response_model=user.UserOut)
async def get_user_info(user_id: int, token: str = Depends(decode_token)):
    try:
        current_user_id = token["id"]
        user_info = await get_info(current_user=current_user_id, user_id=user_id)
        return user_info
    except ObjectNotFound:
        raise HTTPException(status_code=404, detail="Sorry, page not found")
