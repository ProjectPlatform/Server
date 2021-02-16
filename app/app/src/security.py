import logging
from datetime import datetime, timedelta
from typing import Optional

from fastapi import HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer, SecurityScopes
from jose import jwt, JWTError
from passlib.context import CryptContext

from starlette import status
from app.app import inital_data
from app.app.backend.exceptions import ObjectNotFound
from app.app.backend.user import get_user_info

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
ALGORITHM = inital_data.config['security']['ALGORITHM']
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login",
                                     scopes={"user": "Ordinary user", "developer": "Application developer"})
SECRET_KEY = inital_data.config['security']['SECRET_KEY']
ACCESS_TOKEN_EXPIRE_MINUTES = 3000


# async def decode_token(security_scopes: SecurityScopes, token: str = Depends(oauth2_scheme)):
async def decode_token(token: str = Depends(oauth2_scheme)):
    # if security_scopes.scopes
    # log.info(token)
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
