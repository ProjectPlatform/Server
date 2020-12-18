import logging
import os
from datetime import datetime, timedelta
from typing import Optional

from fastapi import HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer, SecurityScopes
from jose import jwt, JWTError
from passlib.context import CryptContext

from dotenv import load_dotenv
from starlette import status

from app.app.backend import get_user_info, ObjectNotFound
from app.app.inital_data import config

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

log.info(config.sections())
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
ALGORITHM = config['security']['ALGORITHM']
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login",
                                     scopes={"user": "Ordinary user", "developer": "Application developer"})
SECRET_KEY = config['security']['SECRET_KEY']
ACCESS_TOKEN_EXPIRE_MINUTES = 3000


# def get_password_hash(password):
#     return pwd_context.hash(password)


#async def decode_token(security_scopes: SecurityScopes, token: str = Depends(oauth2_scheme)):
async def decode_token(token: str = Depends(oauth2_scheme)):
    # if security_scopes.scopes
    log.info(token)
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = int(payload.get("sub"))
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    try:
        user = await get_user_info(current_user=user_id, user_id=user_id)
    except ObjectNotFound:
        raise credentials_exception
    if user is None:
        raise credentials_exception
    return user


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=3000)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt
