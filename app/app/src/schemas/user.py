from typing import Optional

from pydantic import BaseModel, EmailStr


# Shared properties
# class UserBase(BaseModel):
#     nick: str
#     email: Optional[EmailStr] = None
#     is_active: Optional[bool] = True
#     is_superuser: bool = False
#     full_name: Optional[str] = None


# Properties to receive via API on creation
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
    #avatar_id: Optional[int]
