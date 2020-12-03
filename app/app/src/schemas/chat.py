from pydantic import BaseModel, validator
from typing import List, Optional
from enum import Enum


class ChatMinimalInfo(BaseModel):
    current_user: int
    chat_id: int


class ChatCreate(BaseModel):
    name: str
    avatar: Optional[str] = None
    color_rgba: Optional[int] = 0
    encoded: Optional[bool] = False
   # properties_list: List[str]

    @validator('color_rgba')
    def val_color_rgba(cls, var):
        if var < 0 or var >= 4294967297:
            raise ValueError('Parameter \'color_rgba\' must be greater than or equal to zero and less then 4294967297')


class ChatOut(BaseModel):
    name: str
    avatar_id: str
    colour: str
    is_encrypted: bool = False
    is_personal: bool = False
    is_user_expandable: bool = False
    is_user_expandable_modified_by: bool = False
    is_non_admin: bool = False
    is_non_admin_modified_by: str
    non_removable_messages: bool = False
    non_removable_messages_modified_by: str
    non_modifiable_messages: bool = False
    non_modifiable_messages_modified_by: str
    auto_remove_messages: bool = False
    auto_remove_messages_modified_by: str
    auto_remove_period: int = None
    digest_messages: bool = False
    digest_messages_modified_by: str
    admins: List[str]
    users: List[str]
    tags: List[str]
    attachments: List[bytes]
    last_message_id: str


class Properties(Enum):
    UserExpandable: Optional[bool] = False
    NonAdmin: Optional[bool] = False
    NonRemovableMessages: Optional[bool] = False
    NonModifiableMessages: Optional[bool] = False
    AutoRemoveMessages: Optional[bool] = False
    AutoLoggingMessages: Optional[bool] = False
    PersonalChat: Optional[bool] = False


#
# class Chat(BaseModel):
#     ID: int
#     name: str
#     sent_time: int
#     avatar: Optional[bytes] = None
#     colour: Optional[bytes] = None
#     encoded: bool = False
#     admin_list: List[int]
#     user_list: List[int]
#     tag_list: List[int]
#     properties: List[Properties]
#     attached_files_list: List[str]
#     last_message_ID: List[int] = 0


class Message(BaseModel):
    author: int
    chat_ID: int
    message_id: int
    sent_time: int
    tag_list: List[str]
    body: str
    connected_images: Optional[bytes] = None
    connected_documents: Optional[bytes] = None
