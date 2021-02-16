import logging
from typing import Optional, Dict, Any

from asyncpg.exceptions import UniqueViolationError
from passlib.hash import pbkdf2_sha256
from pydantic import EmailStr

from app.app.backend import config
from app.app.backend.exceptions import NickTaken, EmailTaken, AuthenticationError, ObjectNotFound
from app.app.backend.utils import db_required, insert_with_unique_id

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)


@db_required
async def register(nick: str, password: str, email: EmailStr, name: str):
    password_hash = pbkdf2_sha256.hash(password)
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
    ):
        if pbkdf2_sha256.verify(password, user["passwd_hash"]):
            return user["id"]
    raise AuthenticationError()


@db_required
async def get_user_info(current_user: Optional[int] = None, user_id: Optional[int] = None,
                        user_nick: Optional[str] = None,
                        user_email: Optional[EmailStr] = None) -> Dict[str, Any]:
    if user_id is not None:
        if u := await config.db.fetchrow("SELECT * FROM users_authentication WHERE id=$1", user_id):
            return {"id": u["id"], "nick": u["nick"], "name": u["name"], "email": u["email"]}
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
async def temporary_registration(user_id: int, verification_code: int):
    await config.db.execute(f'insert into registration_verification_codes(id, mailCode) values ($1, $2);',
                            user_id,
                            verification_code)


@db_required
async def verification_attempt(user_id: int, verification_code: int):
    result = await config.db.fetchrow(
        f'select attemptsMade, (mailCode = $2)::bool from registration_verification_codes '
        f'where id = $1 and validTime > current_timestamp limit 1;',
        user_id,
        verification_code)
    if result:
        await config.db.execute(f'delete from registration_verification_codes where id = $1;',
                                user_id)
        await config.db.execute(f'update users_authentication set was_confirmed = true where id = $1;',
                                user_id)
    else:
        await config.db.execute(
            f'update registration_verification_codes set attemptsMade = attemptsMade + 1 where id = $1;',
            user_id)
    return result


@db_required
async def delete_user_system(current_user: int):
    if result := await config.db.execute(f'DELETE FROM users_authentication WHERE id = $1;', current_user):
        return result
    raise ObjectNotFound()


@db_required
async def change_pass(current_user: int, password: str):
    password_hash = pbkdf2_sha256.hash(password)
    if result := await config.db.execute(f'UPDATE users_authentication SET passwd_hash = $1 WHERE id = $2;',
                                         password_hash,
                                         current_user):
        return result
    raise ObjectNotFound()


@db_required
async def change_email(current_user: int, email: EmailStr):
    if result := await config.db.execute(f'UPDATE users_authentication SET email = $1 WHERE id = $2;', email,
                                         current_user):
        return result
    raise ObjectNotFound()


@db_required
async def insert_fcm_token(current_user: int, fcm_token: str):
    await config.db.execute("UPDATE users_authentication SET devices_token_list ="
                            " array_append(users_authentication.devices_token_list, $2::varchar) "
                            "WHERE ID = $1 AND NOT ($2= ANY(users_authentication.devices_token_list));",
                            current_user,
                            fcm_token,
                            )


@db_required
async def delete_fcm_token(current_user: int, fcm_token: str):
    if result := await config.db.execute(
            "update users_authentication set devices_token_list = array_remove(devices_token_list, $2::varchar)"
            " where id = $1 and $2 = any(devices_token_list);",
            current_user,
            fcm_token,
    ):
        return result
    raise ObjectNotFound()


@db_required
async def check_duplicate_fcm_token(fcm_token: str):
    await config.db.execute(
        "update users_authentication set devices_token_list = array_remove(devices_token_list, $1::varchar);",
        fcm_token,
    )
