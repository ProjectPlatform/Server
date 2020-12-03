from typing import Optional, Dict, Any

from asyncpg.exceptions import UniqueViolationError
from passlib.hash import pbkdf2_sha256
from pydantic import EmailStr

from app.app.backend import config
from app.app.backend.exceptions import NickTaken, EmailTaken, AuthenticationError, ObjectNotFound
from app.app.backend.utils import db_required, insert_with_unique_id


@db_required
async def register(nick: str, password: str, email: EmailStr, name: str):
    password_hash = pbkdf2_sha256.hash(password)
    print(password_hash)
    try:
        return await insert_with_unique_id(
            "users_authentication",
            ("nick", "name", "passwd_hash", "email"),
            (nick, name, password_hash, email),
        )
    except UniqueViolationError as e:
        if e.constraint_name == "nick_uniq":
            raise NickTaken()
        elif e.constraint_name == "email_uniq":
            raise EmailTaken()


@db_required
async def authenticate(nick: str, password: str) -> str:
    if user := await config.db.fetchrow(
            "SELECT id, passwd_hash FROM users_authentication WHERE nick = $1;", nick
            # "SELECT id, password FROM users WHERE nick = $1", nick
    ):
        if pbkdf2_sha256.verify(password, user["passwd_hash"]):
            return user["id"]
    raise AuthenticationError()


@db_required
async def get_user_info(current_user: Optional[int] = None, user_id: Optional[int] = None, user_nick: Optional[int] = None,
                        user_email: Optional[EmailStr] = None) -> Dict[str, Any]:
    if user_id is not None:
        if u := await config.db.fetchrow("SELECT * FROM users_authentication WHERE id=$1", user_id):
            return {"id": u["id"], "nick": u["nick"], "name": u["name"]}
            # TODO Ilya will add new table user info which will be contain column avatar_id
            # return {"nick": u["nick"], "name": u["name"], "avatar_id": u["avatar_id"]}
        else:
            raise ObjectNotFound()
    elif user_nick is not None:
        if u := await config.db.fetchrow("SELECT * FROM users_authentication WHERE nick=$1", user_nick):
            return {"id": u["id"], "nick": u["nick"], "name": u["name"]}
        else:
            raise ObjectNotFound()
    elif user_email is not None:
        if u := await config.db.fetchrow("SELECT * FROM users_authentication WHERE email=$1", user_email):
            return {"id": u["id"], "nick": u["nick"], "name": u["name"]}
        else:
            raise ObjectNotFound()


@db_required
async def delete_user_system(current_user: int):
    try:
        await config.db.execute(f'DELETE FROM users_authentication WHERE id = $1;', current_user)
        return True
    except Exception as e:
        raise ObjectNotFound()


@db_required
async def change_pass(current_user: int, password: str):
    try:
        password_hash = pbkdf2_sha256.hash(password)
        await config.db.execute(f'UPDATE users_authentication SET passwd_hash = $1 WHERE id = $2;', password_hash,
                                current_user)
        return True
    except Exception as e:
        raise ObjectNotFound()


@db_required
async def change_email(current_user: int, email: EmailStr):
    try:
        await config.db.execute(f'UPDATE users_authentication SET email = $1 WHERE id = $2;', email,
                                current_user)
        return True
    except Exception as e:
        raise ObjectNotFound()


@db_required
async def insert_fcm_token(current_user: int, fcm_token: str):
    # try:
    await config.db.execute("UPDATE users_authentication SET devices_token_list ="
                            " array_append(users_authentication.devices_token_list, $2::varchar) "
                            "WHERE ID = $1 AND NOT ($2= ANY(users_authentication.devices_token_list));",
                            current_user,
                            fcm_token,
                            )
    return {'result': True}
# except Exception as e:
#     raise ObjectNotFound()
