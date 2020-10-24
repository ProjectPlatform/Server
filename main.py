from fastapi import FastAPI, Query, Depends, HTTPException, status, Body, Request
from datetime import datetime, timedelta
from src.schemas import *
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from passlib.hash import sha256_crypt


app = FastAPI(root_path="/api/v1")
