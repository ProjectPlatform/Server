from datetime import timedelta
from http.client import HTTPException
from typing import Any

from fastapi import Depends, HTTPException, status
from fastapi import APIRouter
from fastapi.security import OAuth2PasswordRequestForm
from app.app.src import schemas
from app.app.backend import user
from app.app.src.security import create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES

router = APIRouter()


@router.post("/token", response_model=schemas.Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user_auth = user.authenticate(nick=form_data.username, password=form_data.password)
    if not user_auth:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": form_data.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/registration")
async def create_user(
        user_in: schemas.UserCreate,
) -> Any:
    """
        Create new user.
        """
    await user.register(nick=user_in.nick, password=user_in.password, email=user_in.email, name=user_in.name)
    # Add email send
    return {"status": "ok"}
