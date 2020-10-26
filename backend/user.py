from backend.utils import db_required, insert_with_unique_id
from backend.exceptions import NickTaken, EmailTaken
from passlib.hash import pbkdf2_sha256
from asyncpg.exceptions import UniqueViolationError
import pickle


@db_required
async def register(nick: str, password: str, email: str, name: str):
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
