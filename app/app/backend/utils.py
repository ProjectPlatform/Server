from app.app.backend import config
from app.app.backend.exceptions import NotInitialised
from asyncpg.exceptions import UniqueViolationError
from functools import update_wrapper
import random
import string
from typing import Tuple, Any


def db_required(func):
    def wrapper(*args, **kwargs):
        if not config.db:
            raise NotInitialised
        return func(*args, **kwargs)

    update_wrapper(wrapper, func)
    return wrapper


def generate_id() -> int:
    return random.randint(1, 999999)


async def insert_with_unique_id(
        table: str, columns: Tuple[str, ...], values: Tuple[Any, ...]
) -> int:
    while 1:
        uid = generate_id()
        try:
            await config.db.execute(
                # TODO replace sql request
                # "INSERT INTO users_authentication (ID, NICK, EMAIL, NAME, PASSWD_HASH, PASSWD_SALT) VALUES (DEFAULT, 'test', 'test@test', 'test', 'test', '_PASSWORD_SALT');"

                f'INSERT INTO {table} (id, {", ".join(columns)}) VALUES ($1, {", ".join([f"${i}" for i in range(2, len(values) + 2)])});',
                uid,
                *values,
            )
            return uid
        except UniqueViolationError as e:
            if e.constraint_name == f"{table}_id_pkey":
                continue
            else:
                # TODO coolision id detected
                raise e
