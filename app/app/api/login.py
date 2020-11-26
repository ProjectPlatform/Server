from datetime import timedelta
from http.client import HTTPException
from typing import Any

from fastapi import Depends, HTTPException, status
from fastapi import APIRouter
from fastapi.security import OAuth2PasswordRequestForm

from app.app.backend.exceptions import NotInitialised
from app.app.src import schemas
from app.app.backend import user, NickTaken, EmailTaken, AuthenticationError
from app.app.src.schemas.user import UserAuth
from app.app.src.security import create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES

router = APIRouter()


@router.post("/login", response_model=schemas.Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    **Authenticate a user**

    Return the **id** of the authenticated account

    **Exceptions**
    * Status code **400**
    * Status code **401**
    * Status code **501**
    """
    try:
        user_id = await user.authenticate(nick=form_data.username, password=form_data.password)
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": str(user_id)}, expires_delta=access_token_expires
        )
        return {"access_token": access_token, "token_type": "bearer"}
    except NotInitialised:
        HTTPException(status_code=501, detail="Sorry, database was not initialized")
    except AuthenticationError:
        raise HTTPException(status_code=401, detail="Invalid username or password")


@router.post("/registration")
async def create_user(
        user_in: schemas.UserCreate,
) -> Any:
    """
    **Create a user account.**

    Returns JSON string ```{'result': true}```

    **Exceptions:**
    * Status code **422**
    * Status code **501**
    """
    try:
        await user.register(nick=user_in.nick, password=user_in.password, email=user_in.email, name=user_in.name)
        # Add email send
        return {"status": "ok"}
    except NotInitialised:
        HTTPException(status_code=501, detail="Sorry, database was not initialized")
    except NickTaken:
        raise HTTPException(status_code=422, detail="Nick is taken")
    except EmailTaken:
        raise HTTPException(status_code=422, detail="Email is taken")


@router.get("/echo")
async def read_root(echo: str):
    return {"echo": echo}
