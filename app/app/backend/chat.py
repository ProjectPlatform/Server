import json
import os
from datetime import datetime
import logging
import shutil
import uuid
from typing import Optional, Any, Dict, List, Tuple

from fastapi import UploadFile
from firebase_admin import messaging

from app.app.backend import config
from app.app.backend.utils import db_required, insert_with_unique_id, insert_without_unique_id
from app.app.backend.exceptions import PermissionDenied, ObjectNotFound, InvalidRange
from app.app.backend.user import get_user_info
from app.app.src.websockets import connections

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)


@db_required
async def has_user(user_id: int, chat_id: int):
    return bool(
        await config.db.fetchrow(
            "SELECT * FROM chat_participants WHERE participant_id = $1 AND chat_id = $2;",
            user_id,
            chat_id,
        )
    )


async def is_user_admin(user_id: int, chat_id: int):
    return bool(
        await config.db.fetchrow(
            "SELECT * FROM chat_participants WHERE participant_id = $1 AND chat_id = $2 AND is_admin;",
            user_id,
            chat_id,
        )
    )


@db_required
async def __get_info__(chat_id: int) -> Dict[str, Any]:
    if res := await config.db.fetchrow("SELECT * FROM chats WHERE id = $1", chat_id):
        return dict(res)
    raise ObjectNotFound()


@db_required
async def get_info(current_user: int, chat_id: int) -> Dict[str, Any]:
    if not await has_user(current_user, chat_id) and current_user != 1:
        raise PermissionDenied()
    res = await __get_info__(chat_id)
    res["admins"] = []
    res["users"] = []
    for record in await config.db.fetch(
            "SELECT participant_id, is_admin FROM chat_participants WHERE chat_id = $1", chat_id
    ):
        if record["is_admin"]:
            res["admins"].append(record["participant_id"])
        res["users"].append(record["participant_id"])
    return res


@db_required
async def __is_chat_non_admin__(chat_id: int) -> bool:
    return (await __get_info__(chat_id))["is_non_admin"]


@db_required
async def __add_user__(chat_id: int, user_to_add: int, is_admin: bool = False) -> bool:
    # TODO add except on "chat_participants_participant_id_fkey"
    await insert_without_unique_id("CHAT_PARTICIPANTS",
                                   ("participant_id", "chat_id", "is_admin"),
                                   (user_to_add, chat_id, is_admin),
                                   )
    return True


@db_required
async def add_user(current_user: int, chat_id: int, user_to_add: int) -> bool:
    if await has_user(current_user, chat_id):
        # c = await __get_info__(chat_id)
        # if "is_personal" not in c["properties_list"] and (
        #         "is_user_expandable" in c["properties_list"] or await is_user_admin(current_user, chat_id)
        # ):
        if not await has_user(user_to_add, chat_id):
            return await __add_user__(chat_id, user_to_add)
        else:
            return False
    raise PermissionDenied()


@db_required
async def __remove_user__(chat_id: int, user_to_remove: int) -> bool:
    await config.db.execute(
        "delete from chat_participants Where chat_id = $1 and participant_id = $2;",
        chat_id,
        user_to_remove,
    )
    participants = dict(
        await config.db.fetchrow("Select exists(select '*' from chat_participants Where chat_id = $1);",
                                 chat_id))
    logging.info(participants)
    if not participants["exists"]:
        await config.db.execute(
            "DELETE FROM chats WHERE id = $1;",
            chat_id,
        )
    return True


@db_required
async def remove_user(current_user: int, chat_id: int, user_to_remove: int) -> bool:
    if await has_user(current_user, chat_id):
        if current_user == user_to_remove or await is_user_admin(current_user, chat_id):
            if await has_user(user_to_remove, chat_id):
                return await __remove_user__(chat_id, user_to_remove)
            else:
                return False
    raise PermissionDenied()


@db_required
async def make_user_admin(current_user: str, chat_id: int, target_user: int) -> bool:
    if await is_user_admin(current_user, chat_id):
        if await has_user(target_user, chat_id):
            await config.db.execute(
                "UPDATE chat_participants SET is_admin=true WHERE chat_id=$1 AND participant_id=$2",
                chat_id,
                target_user,
            )
            return True
        else:
            return False
    raise PermissionDenied()


@db_required
async def create(
        current_user_id: int,
        name: str,
        avatar: Optional[str],
        color_rgba: int,
        encoded: bool,
        #  properties_list: List[str],
) -> Dict[str, Any]:
    async with config.db.acquire() as con:
        async with con.transaction():
            res_id = await insert_with_unique_id(
                "chats",
                (
                    "name",
                    "creator",
                    "avatar",
                    "COLOR_RGBA",
                    "ENCODED",
                    # "PROPERTIES_LIST",
                ),
                (
                    name,
                    current_user_id,
                    avatar,
                    color_rgba,
                    encoded,
                    #     properties_list,
                ),
            )
            await __add_user__(res_id, current_user_id, True)
    return await get_info(current_user_id, res_id)


@db_required
async def create_personal(current_user: int, user2: int) -> Dict[str, Any]:
    if await get_personal_chat(current_user, user2):
        raise PermissionDenied()
    u1 = await get_user_info(current_user, current_user)
    u2 = await get_user_info(current_user, user2)
    async with config.db.acquire() as con:
        async with con.transaction():
            res = await create(
                current_user,
                name=f'{u1["nick"]} и {u2["nick"]}',
                is_personal=True,
                is_user_expandable=False,
                is_non_admin=True,
            )
            await __add_user__(res["id"], user2)
    return await get_info(current_user, res["id"])


@db_required
async def set_non_admin(current_user: str, chat_id: str, value: bool) -> bool:
    if await is_user_admin(current_user, chat_id):
        await config.db.execute(
            "UPDATE chats SET is_non_admin=$1, is_non_admin_modified_by=$2 WHERE id=$3",
            value,
            current_user,
            chat_id,
        )
        return True
    raise PermissionDenied()


@db_required
async def __set_property__(
        current_user: str, chat_id: str, propperty: str, value: bool
) -> bool:
    if await is_user_admin(current_user, chat_id) or (
            value and await __is_chat_non_admin__(chat_id)
    ):
        await config.db.execute(
            f"UPDATE chats SET {propperty}=$1, {propperty}_modified_by=$2 WHERE id=$3",
            value,
            current_user,
            chat_id,
        )
        return True
    raise PermissionDenied


@db_required
async def set_user_expandable(current_user: str, chat_id: str, value: bool) -> bool:
    if (await __get_info__(chat_id))["is_personal"]:
        raise PermissionDenied()
    return await __set_property__(current_user, chat_id, "is_user_expandable", value)


@db_required
async def set_non_removable_messages(
        current_user: str, chat_id: str, value: bool
) -> bool:
    return await __set_property__(
        current_user, chat_id, "non_removable_messages", value
    )


@db_required
async def set_non_modifiable_messages(
        current_user: str, chat_id: str, value: bool
) -> bool:
    return await __set_property__(
        current_user, chat_id, "non_modifiable_messages", value
    )


@db_required
async def set_auto_remove_messages(
        current_user: str, chat_id: str, value: bool, period: Optional[int] = None
) -> bool:
    async with config.db.acquire() as con:
        async with con.transaction():
            await __set_property__(
                current_user, chat_id, "non_removable_messages", value
            )
            await config.db.execute(
                "UPDATE chats SET auto_remove_period=$1 WHERE id=$2", period, chat_id
            )
    return True


@db_required
async def set_digest_messages(current_user: str, chat_id: str, value: bool) -> bool:
    return await __set_property__(current_user, chat_id, "digest_messages", value)


@db_required
async def __message_add_extra_fields__(m: Dict[str, Any]) -> None:
    m["attachments"] = []
    for record in await config.db.fetch(
            "SELECT id FROM message_attachments WHERE message_attached_id=$1", m["id"]
    ):
        m["attachments"].append(record["id"])
    m["tags"] = []
    for record in await config.db.fetch(
            "SELECT tag_list FROM messages WHERE id=$1", m["id"]
    ):
        m["tags"].append(record["tag_list"])


@db_required
async def __get_message__(
        message_id: int, include_extra_fields: bool = False
) -> Dict[str, Any]:
    if res := await config.db.fetchrow(
            "SELECT * FROM messages WHERE id=$1", message_id
    ):
        res = dict(res)
        # if include_extra_fields:
        #     await __message_add_extra_fields__(res)
        return res
    raise ObjectNotFound()


@db_required
async def get_message(current_user: int, message_id: int):
    m = await __get_message__(message_id, True)
    if await has_user(current_user, m["chat_attached_id"]):
        return m
    raise PermissionDenied()


@db_required
async def get_message_range(
        current_user: int, chat_id: int, limit: int = 50
) -> List[Dict[str, Any]]:
    if await has_user(current_user, chat_id):
        # if not lower_id and not upper_id:
        #     raise InvalidRange()
        # lower_message = await __get_message__(lower_id) if lower_id else None
        # upper_message = await __get_message__(upper_id) if upper_id else None
        # if (lower_message and upper_message) and (
        #         lower_message["chat_attached_id"] != upper_message["chat_attached_id"]
        # ):
        #     raise InvalidRange()
        # chat_id = lower_message["chat_attached_id"] if lower_message else upper_message["chat_attached_id"]
        # if not await has_user(current_user, chat_id):
        #     raise PermissionDenied()
        # if lower_message and upper_message:
        # lower_message = datetime.date(lower_id)
        # upper_message = datetime.date(upper_id)

        # lower_message = datetime.strptime(lower_date, "%Y-%m-%d %H:%M:%S.%f %z")
        # upper_message = datetime.strptime(upper_date, "%Y-%m-%d %H:%M:%S.%f %z")

        message_list = await config.db.fetch(
            "select * from messages where chat_attached_id = $1 and sent_time > ('2010-9-29 23:24:51.154352+03')::timestamptz Order by sent_time desc LIMIT $2;",
            # "select * from messages where chat_attached_id = $1 and sent_time between $2 and $3 LIMIT $4;",
            chat_id,
            limit,
        )
        # message_list["sent_time"] = datetime.strftime("%Y-%m-%d %H:%M:%S.%f %z")
        # elif not lower_message:
        #     message_list = await config.db.fetch(
        #         "SELECT * FROM messages WHERE chat_attached_id=$1 AND sent_time <= $2 ORDER BY sent_time DESC LIMIT $3",
        #         chat_id,
        #         upper_message["sent_time"],
        #         limit,
        #     )
        # elif not upper_message:
        #     message_list = await config.db.fetch(
        #         "SELECT * FROM messages WHERE chat_attached_id=$1 AND sent_time >= $2 ORDER BY sent_time DESC LIMIT $3",
        #         chat_id,
        #         lower_message["sent_time"],
        #         limit,
        #     )
        # for idx, item in enumerate(message_list):
        #     message_list[idx] = dict(item)
        #     await __message_add_extra_fields__(message_list[idx])
        return message_list
    raise PermissionDenied()


@db_required
async def __send_message__(
        current_user: int,
        chat_id: int,
        body: str,
        attachments: Optional[List[int]] = None,
        tags: Optional[List[str]] = None,
):
    if attachments:
        has_attached_file = True
    else:
        has_attached_file = False
    if not await has_user(current_user, chat_id) and current_user != 1:
        raise PermissionDenied()
    async with config.db.acquire() as con:
        async with con.transaction():
            res = await insert_with_unique_id(
                "messages",
                ("chat_attached_id", "author_id", "tag_list", "body", "has_attached_file"),
                (chat_id, current_user, tags, body, has_attached_file),
            )
            if attachments:
                for a in attachments:
                    await insert_without_unique_id(
                        "message_attachments", ("chat_attached_id", "message_attached_id", "uri"), (chat_id, res, a)
                    )
    return await __get_message__(res, True)


@db_required
async def __send_message_desktop__(
        current_user: int,
        chat_info: Dict[str, Any],
        message: Dict[str, Any],
):
    for chat_user in chat_info["users"]:
        # for i in range(1, 100):
        ws = connections.active_connections.get(chat_user)
        # ws = connections.active_connections.get(i)
        if ws is not None and ws is not current_user:
            log.info(f'Websocket send message to {ws}')
            log.info("  body: " + message["body"])
            await ws.send_bytes(json.dumps({**message}, indent=4, sort_keys=True, default=str))


@db_required
async def __send_message_firebase__(
        current_user: int,
        chat_info: Dict[str, Any],
        message: Dict[str, Any],
        user_nick: str,
):
    token_list = await extract_tokens(current_user=current_user, users=chat_info["users"])
    # log.info(token_list)
    message_firebase = messaging.MulticastMessage(
        notification=messaging.Notification(
            title=chat_info["name"],
            body=user_nick + ": " + message["body"],
        ),
        data={'data': json.dumps({**message}, indent=4, sort_keys=True, default=str)},
        tokens=token_list
    )
    response = messaging.send_multicast(message_firebase)
    # print('Successfully sent message:', response)


@db_required
async def send_system_message(
        chat_id: int,
        body: str,
) -> Dict[str, Any]:
    message = await send_message(current_user=1, chat_id=chat_id, body=body, attachments=[], tags=[])
    return message


@db_required
async def send_message(
        current_user: int,
        chat_id: int,
        body: str,
        attachments: Optional[List[int]] = None,
        tags: Optional[List[str]] = None,
) -> Dict[str, Any]:
    user_info = await get_user_info(user_id=current_user)

    message = await __send_message__(current_user=current_user, chat_id=chat_id, body=body, attachments=attachments,
                                     tags=tags)
    message.update({"message_type": "message"})

    chat_info = await get_info(current_user=current_user, chat_id=chat_id)

    # Send message to desktop client
    await __send_message_desktop__(current_user=current_user, chat_info=chat_info, message=message)

    # Send message to android client
    await __send_message_firebase__(current_user=current_user, chat_info=chat_info, message=message,
                                    user_nick=user_info["nick"])
    return message


@db_required
async def get_attachment(file_id: int):
    file_path = await config.db.fetchrow(f'select path_original from sources where id = $1 limit 1;',
                                         file_id)
    return file_path["path_original"]


@db_required
async def create_upload_file(uploaded_file: UploadFile, current_user: int, description: str, is_showable: bool) -> str:
    filename, file_extension = os.path.splitext(uploaded_file.filename)
    file_id = str(uuid.uuid4()) + file_extension
    file_location = os.path.join(os.path.dirname(__file__), f'attachments/{file_id}')
    with open(file_location, "wb+") as file_object:
        shutil.copyfileobj(uploaded_file.file, file_object)
    await insert_without_unique_id("sources",
                                   ("inner_uri", "is_public", "is_showable", "path_original",
                                    "path_thumbnail", "owner", "description", "meta"),
                                   (file_id, True, is_showable, file_location, file_location,
                                    current_user, description, "meta"))
    return file_id


# ATTACHMENT_IMAGE = 0
# ATTACHMENT_DOCUMENT = 1


@db_required
async def edit_message(
        current_user: int,
        message_id: int,
        body: str,
        attachments: Optional[List[Tuple[int, str]]] = None,
        tags: Optional[List[str]] = None,
) -> bool:
    m = await __get_message__(message_id)
    c = await __get_info__(m["chat_attached_id"])
    # or c["non_modifiable_messages"]
    if m["author_id"] != current_user:
        # or c["non_modifiable_messages"]
        raise PermissionDenied()
    async with config.db.acquire() as con:
        async with con.transaction():
            await config.db.execute(
                "UPDATE messages SET body=$1 WHERE id=$2", body, message_id
            )
            await config.db.execute(
                "DELETE FROM message_attachments WHERE message_attached_id=$1", message_id
            )
            # await config.db.execute(
            #     "DELETE FROM message_tags WHERE message_id=$1", message_id
            # )
            # if attachments:
            #     for a in attachments:
            #         if a[0] == ATTACHMENT_IMAGE:
            #             col = "image_id"
            #         elif a[0] == ATTACHMENT_DOCUMENT:
            #             col = "document_id"
            #         await insert_with_unique_id(
            #             "message_attachments", ("message_attached_id", col), (message_id, a[1])
            #         )
            # if tags:
            #     for t in tags:
            #         await insert_with_unique_id(
            #             "message_tags", ("message_id", "tag"), (message_id, t)
            #         )
    return True


@db_required
async def delete_message(current_user: int, message_id: int) -> bool:
    m = await __get_message__(message_id)
    c = await __get_info__(m["chat_attached_id"])
    if m["author_id"] != current_user:
        # or c["non_removable_messages"]
        raise PermissionDenied()
    await config.db.execute("DELETE FROM messages WHERE id=$1", message_id)
    return True


@db_required
async def get_chats_for_user(user_id: str) -> List[str]:
    chat_list = await config.db.fetch(
        "SELECT chat_id FROM chat_participants WHERE participant_id=$1", user_id
    )
    for idx, item in enumerate(chat_list):
        chat_list[idx] = item["chat_id"]
    return chat_list


@db_required
async def get_personal_chat(user1: int, user2: int) -> Optional[str]:
    chat_list = await get_chats_for_user(user1)
    for chat_id in chat_list:
        chat = await __get_info__(chat_id)
        if chat["is_personal"] and await has_user(user2, chat_id):
            return chat_id
    return None


@db_required
async def get_messages_with_tag(
        current_user: int, chat_id: int, tag: str
) -> List[Dict[str, Any]]:
    if not await has_user(current_user, chat_id):
        raise PermissionDenied()
    if message_list := await config.db.fetch(
            "select * from messages where chat_attached_id = $1 and $2 = any(tag_list) ",
            chat_id,
            tag,
    ):
        logging.info(type(message_list))
        return message_list
    raise ObjectNotFound()


@db_required
async def extract_tokens(current_user: int, users: List[int]):
    token_list = []
    for user in users:
        if user != current_user:
            # log.info(user)
            if token := await config.db.fetchrow(
                    "select devices_token_list as tokens from users_authentication where id = $1 limit 1;",
                    user
            ):
                # logging.info(token)
                # logging.info(token["tokens"])
                token_list.extend(token["tokens"])
    if token_list is not None:
        return token_list
    raise ObjectNotFound()
