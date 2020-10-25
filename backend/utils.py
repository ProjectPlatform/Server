from backend.config import db
from backend.exceptions import NotInitialised
from functools import update_wrapper


def db_required(func):
    def wrapper(*args, **kwargs):
        if not db:
            raise NotInitialised
        return func(*args, **kwargs)

    update_wrapper(wrapper, func)
    return wrapper
