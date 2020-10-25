from pydantic import BaseModel, validator, Field
from typing import Optional
from enum import Enum
from pathlib import Path
from fastapi import File


class education_level(Enum):
    'enrollee',
    'undergraduate',
    'graduate',
    'postgraduate'


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None


class User(BaseModel):
    id: str
    nick: str
    name: str
    avatar_id: str
    pspicture: bytes
    email: Optional[str] = None
    full_name: Optional[str] = None
    disabled: Optional[bool] = None
    # age: int = Field(..., gt=15, lt=90, description="Age author")

    # @validator('age')
    # def check_age(cls, value):
    #     if value < 15 > 90:
    #         raise ValueError('Error age!')
    #     return


class education_records(BaseModel):
    id: str
    user_id: str
    # level: education_level
    institution: str
    from_year: int
    to_year: int

    @validator('from_year', 'to_year')
    def check_to_year(cls, value):
        if value is None or value > 0:
            return
        raise ValueError('Error to_year, from_year')


class career_records(BaseModel):
    id: str
    user_id: str
    company: str
    position: str
    from_year: int
    to_year: int

    @validator('from_year', 'to_year')
    def check_to_year(cls, value):
        if value is None or value > 0:
            return
        raise ValueError('Error to_year, from_year')


class additional_experience_records(BaseModel):
    id: str
    user_id: str
    description: str


class tags(BaseModel):
    id: str
    name: str
    hierarchy: Path


class user_tags(BaseModel):
    id: str
    user_id: str
    tag_id: str


class connections(BaseModel):
    id: str
    from_user_id: str
    to_user_id: str
    groups: int
