from pydantic import EmailStr
from typing import Optional, Dict, Any
from app.app.backend.utils import db_required, insert_with_unique_id
from app.app.backend import config
from app.app.backend.exceptions import NickTaken, EmailTaken, AuthenticationError
from passlib.hash import pbkdf2_sha256
from asyncpg.exceptions import UniqueViolationError


@db_required
async def register(nick: str, password: str, email: EmailStr, name: str):
    password = pbkdf2_sha256.hash(password)
    try:
        return await insert_with_unique_id(
            "users",
            ("nick", "password", "email", "name"),
            (nick, password, email, name),
        )
    except UniqueViolationError as e:
        if e.constraint_name == "users_nick_key":
            raise NickTaken()
        elif e.constraint_name == "users_email_key":
            raise EmailTaken()


@db_required
async def authenticate(nick: str, password: str) -> str:
    if user := await config.db.fetchrow(
        "SELECT id, password FROM users WHERE nick = $1", nick
    ):
        if pbkdf2_sha256.verify(password, user["password"]):
            return user["id"]
    raise AuthenticationError()


@db_required
async def get_user_info(current_user: Optional[str], user_id: str) -> Dict[str, Any]:
    # TODO: This function will need to be expanded with more info about the user
    if u := await config.db.fetchrow("SELECT * FROM users WHERE id=$1", user_id):
        return {"nick": u["nick"], "name": u["name"], "avatar_id": u["avatar_id"]}
    else:
        raise ObjectNotFound()
