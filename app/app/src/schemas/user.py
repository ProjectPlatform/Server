from typing import Optional

from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    nick: str
    password: str
    email: EmailStr
    name: str
    #
    # class Config:
    #     arbitrary_types_allowed = True


class UserAuth(BaseModel):
    nick: str
    password: str


class UserOut(BaseModel):
    id: int
    nick: str
    name: str
    email: EmailStr
    #avatar_id: Optional[int]
