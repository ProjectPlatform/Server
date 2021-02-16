import logging
import random
from datetime import timedelta
from http.client import HTTPException
from typing import Any, Optional

from fastapi import Depends, HTTPException, status, Body
from fastapi import APIRouter
from fastapi.security import OAuth2PasswordRequestForm
from firebase_admin import auth, messaging
from starlette.responses import JSONResponse

from app.app.backend.exceptions import NotInitialised, AuthenticationError, NickTaken, EmailTaken, ObjectNotFound
from app.app.src import schemas
# from app.app.backend import user, NickTaken, EmailTaken, AuthenticationError, ObjectNotFound, get_user_info
from app.app.backend.user import insert_fcm_token, delete_fcm_token, check_duplicate_fcm_token, temporary_registration, \
    verification_attempt, authenticate, register, get_user_info
from app.app.src.security import create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES, decode_token
from app.app.utils import send_verification_email

router = APIRouter()

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)


@router.post("/login", response_model=schemas.TokenOut)
async def login_for_access_token(fcm_token: Optional[str] = None, form_data: OAuth2PasswordRequestForm = Depends(), ):
    """
    **Authenticate a user**

    Return the **id** of the authenticated account

    **Exceptions**
    * Status code **401**
    """
    try:
        user_id = await authenticate(nick=form_data.username, password=form_data.password)
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

        if fcm_token is not None:
            await check_duplicate_fcm_token(fcm_token=fcm_token)
            await insert_fcm_token(current_user=user_id, fcm_token=fcm_token)

        return {"access_token": access_token, "token_type": "bearer", "id": user_id}
    except AuthenticationError:
        raise HTTPException(status_code=401, detail="Invalid username or password")
    # except NotInitialised:
    #     HTTPException(status_code=501, detail="Sorry, we have some problems on server")


@router.post("/registration")
async def create_user(
        user_in: schemas.UserCreate,
) -> Any:
    """
    **Create a user account.**

    Returns JSON string ```{'result': true}```

    **Exceptions:**
    * Status code **422**
    """
    try:
        await register(nick=user_in.nick, password=user_in.password, email=user_in.email, name=user_in.name)
        user_info = await get_user_info(user_nick=user_in.nick)

        verification_code = random.randint(100000, 999999)
        await send_verification_email(email_to=user_in.email, subject_template="Please verify your email",
                                      html_template="""
                                                <mjml>
                                          <mj-body background-color="#fff">
                                            <mj-section>
                                              <mj-column>
                                                <mj-divider border-color="#555"></mj-divider>
                                                <mj-text font-size="20px" color="#555" font-family="helvetica">Your verification code: {{ code }}</mj-text>
                                                
                                                <mj-divider border-color="#555" border-width="2px" />
                                              </mj-column>
                                            </mj-section>
                                          </mj-body>
                                        </mjml>""",
                                      environment={"code": verification_code})

        await temporary_registration(user_id=user_info["id"], verification_code=verification_code)
        return {"id": user_info["id"]}
    except NickTaken:
        raise HTTPException(status_code=422, detail="Nick is taken")
    except EmailTaken:
        raise HTTPException(status_code=422, detail="Email is taken")
    # except NotInitialised:
    #     HTTPException(status_code=501, detail="Sorry, we have some problems on server")


@router.post("/verification")
async def verification(user_id: int, verification_code: int):
    """
    **Verify a user account.**

    Returns JSON string with the field ```message```
    In case of successful verification status_code = 200 else 422

    """
    result = await verification_attempt(user_id=user_id, verification_code=verification_code)
    if result:
        return HTTPException(status_code=200, detail="You have successfully verified your account")
    else:
        return HTTPException(status_code=422, detail="Wrong verification code. Try again")


@router.post("/logout")
async def logout(fcm_token: str, token: str = Depends(decode_token)):
    """
    **Revokes the user's fcm token.**

    Returns JSON string ```{'result': True}```

    **Exceptions:**
    * Status code **404**
    """
    try:
        user_id = token["id"]
        result = await delete_fcm_token(current_user=user_id, fcm_token=fcm_token)
        return {"result": result}
    except ObjectNotFound:
        raise HTTPException(status_code=404, detail="Resource wasn't found")