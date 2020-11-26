from typing import Optional

from pydantic import EmailStr

from app.app.backend import ObjectNotFound
from app.app.backend.user import get_user_info as get_info, delete_user_system, change_pass, change_email
from fastapi import APIRouter, HTTPException, Depends
from app.app.src.schemas import user
from app.app.src.security import decode_token

router = APIRouter()


# Add methods for interacting with desktop


@router.get("/get_info", response_model=user.UserOut)
async def get_user_info(user_id: int, token: str = Depends(decode_token)):
    """
    **Obtain information about a user of the platform.**

    Return a **dict** containing the following keys:

    * **id** - the id of the user
    * **nick** – the nick of the user.
    * **name** – the full name of the user.

    **Exceptions:**
    * Status code **404**
    """
    try:
        current_user_id = token["id"]
        user_info = await get_info(current_user=current_user_id, user_id=user_id)
        return user_info
    except ObjectNotFound():
        raise HTTPException(status_code=404, detail="Sorry, page not found")


@router.delete("/delete_from_system")
async def delete_user_from_system(token: str = Depends(decode_token)):
    try:
        current_user = token["id"]
        await delete_user_system(current_user=current_user)
        return {"status": True}
    except ObjectNotFound:
        raise HTTPException(status_code=404, detail="Sorry, page not found")


@router.post("/update_pass")
async def update_pass(passwd: str, token: str = Depends(decode_token)):
    try:
        current_user_id = token["id"]
        await change_pass(current_user=current_user_id, password=passwd)
        return {"status": True}
    except ObjectNotFound:
        raise HTTPException(status_code=404, detail="Sorry, page not found")


@router.post("/update_email")
async def update_email(email: EmailStr, token: str = Depends(decode_token)):
    try:
        current_user_id = token["id"]
        await change_email(current_user=current_user_id, email=email)
        return {"status": True}
    except ObjectNotFound:
        raise HTTPException(status_code=404, detail="Sorry, page not found")
