import logging
from datetime import timedelta
from http.client import HTTPException
from typing import Any

from fastapi import Depends, HTTPException, status, Body
from fastapi import APIRouter
from fastapi.security import OAuth2PasswordRequestForm
from firebase_admin import auth, messaging

from app.app.backend.exceptions import NotInitialised
from app.app.src import schemas
from app.app.backend import user, NickTaken, EmailTaken, AuthenticationError, ObjectNotFound
from app.app.backend.user import insert_fcm_token
from app.app.src.schemas.user import UserAuth
from app.app.src.security import create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES, decode_token
from app.app import inital_data

router = APIRouter()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@router.post("/login", response_model=schemas.TokenOut)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), ):
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
            data={"sub": str(user_id), "scopes": form_data.scopes},
            expires_delta=access_token_expires
        )
        # custom_token = auth.create_custom_token(str(user_id))
        # logging.info(custom_token)
        return {"access_token": access_token, "token_type": "bearer", "id": user_id}
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


# @router.post("/get_fcm_token")
# async def get_fcm_token(token: str= Body()):
#     if

@router.post("/send_fcm_token")
async def send_fcm_token(fcm_token: str, token: str = Depends(decode_token), ):
    try:
        user_id = token["id"]
        await insert_fcm_token(current_user=user_id, fcm_token=fcm_token)
        return {"result": True}
    except ObjectNotFound:
        raise HTTPException(status_code=404, detail="Page not found")


@router.get("/echo")
async def read_root(echo: str):
    logger.info(echo)
    message = messaging.Message(
        notification=messaging.Notification(
            title=echo,
            body=echo,
        ),
        token="fKxkxbWdTTCuwfodx37qZe:APA91bHTbYrcHvvlivB84UAukLKfKquweyXqJzdgW10JHRbgBMcVCr8N_DkebFTE0Y_OXjsMsBT5WFySSO3NLuo0b3EQSzPTN11QXIgnnI-n4T-NgJ2Ckhk-0TeDdSYRT4KIAoDOZjCY"
    )
    response = messaging.send(message)

    print('Successfully sent message:', response)
    return {"echo": echo}
