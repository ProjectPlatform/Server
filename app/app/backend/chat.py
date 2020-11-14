from datetime import datetime
from typing import Optional, Any, Dict, List, Tuple
from app.app.backend import config
from app.app.backend.utils import db_required, insert_with_unique_id
from app.app.backend.exceptions import PermissionDenied, ObjectNotFound, InvalidRange
from app.app.backend.user import get_user_info


@db_required
async def has_user(user_id: str, chat_id: str):
    return bool(
        await config.db.fetchrow(
            "SELECT * FROM chat_memberships WHERE user_id = $1 AND chat_id = $2;",
            user_id,
            chat_id,
        )
    )


async def is_user_admin(user_id: str, chat_id: str):
    return bool(
        await config.db.fetchrow(
            "SELECT * FROM chat_memberships WHERE user_id = $1 AND chat_id = $2 AND is_admin;",
            user_id,
            chat_id,
        )
    )


@db_required
async def __get_info__(chat_id: str) -> Dict[str, Any]:
    if res := await config.db.fetchrow("SELECT * FROM chats WHERE id = $1", chat_id):
        return dict(res)
    raise ObjectNotFound()


@db_required
async def get_info(current_user: str, chat_id: str) -> Dict[str, Any]:
    if not await has_user(current_user, chat_id):
        raise PermissionDenied()
    res = await __get_info__(chat_id)
    res["admins"] = []
    res["users"] = []
    for record in await config.db.fetch(
        "SELECT user_id, is_admin FROM chat_memberships WHERE chat_id = $1", chat_id
    ):
        if record["is_admin"]:
            res["admins"].append(record["user_id"])
        else:
            res["users"].append(record["user_id"])
    res["tags"] = []
    for record in await config.db.fetch(
        "SELECT distinct tag FROM message_tags JOIN messages ON messages.id=message_id WHERE messages.chat_id=$1",
        chat_id,
    ):
        res["tags"].append(record.tag)
    res["attachments"] = []
    for record in await config.db.fetch(
        "SELECT id FROM message_attachments JOIN messages ON messages.id=message_id WHERE messages.chat_id = $1",
        chat_id,
    ):
        res["attachments"].append(record["id"])
    res["last_message_id"] = await config.db.fetchval(
        "SELECT id FROM messages WHERE chat_id=$1 ORDER BY timestamp DESC LIMIT 1",
        chat_id,
    )
    return res


@db_required
async def __is_chat_non_admin__(chat_id: str) -> bool:
    return await __get_info__(chat_id)["is_non_admin"]


@db_required
async def __add_user__(chat_id: str, user_to_add: str, is_admin: bool = False) -> bool:
    await insert_with_unique_id(
        "chat_memberships",
        ("user_id", "chat_id", "is_admin"),
        (current_user, res, is_admin),
    )
    return True


@db_required
async def add_user(current_user: str, chat_id: str, user_to_add: str) -> bool:
    if await has_user(current_user, chat_id):
        c = await __get_info__(chat_id)
        if not c["is_personal"] and (
            c["is_user_expandable"] or await is_chat_admin(current_user, chat_id)
        ):
            if not await has_user(user_to_add, chat_id):
                return await __add_user__(chat_id, user_to_add)
            else:
                return False
    raise PermissionDenied()


@db_required
async def __remove_user__(chat_id: str, user_to_remove: str) -> bool:
    await config.db.execute(
        "DELETE FROM chat_memberships WHERE chat_id=$1 AND user_id=$2",
        chat_id,
        user_to_remove,
    )
    return True


@db_required
async def remove_user(current_user: str, chat_id: str, user_to_remove: str) -> bool:
    if await has_user(current_user, chat_id):
        if current_user == user_to_remove or await is_chat_admin(current_user, chat_id):
            if await has_user(user_to_add, chat_id):
                return await __remove_user__(chat_id, user_to_remove)
            else:
                return False
    raise PermissionDenied()


@db_required
async def make_user_admin(current_user: str, chat_id: str, target_user: str) -> bool:
    if await is_user_admin(current_user, chat_id):
        if await has_user(target_user, chat_id):
            await config.db.execute(
                "UPDATE chat_memberships SET is_admin=true WHERE chat_id=$1 AND user_id=$2",
                chat_id,
                target_user,
            )
            return True
        else:
            return False
    raise PermissionDenied()


@db_required
async def create(
    current_user: str,
    name: str,
    colour: int = 0,
    is_encrypted: bool = False,
    is_personal: bool = False,
    is_user_expandable: bool = False,
    is_non_admin: bool = False,
    non_removable_messages: bool = False,
    non_modifiable_messages: bool = False,
    auto_remove_messages: bool = False,
    auto_remove_period: Optional[int] = None,
    digest_messages: bool = False,
) -> Dict[str, Any]:
    async with config.db.acquire() as con:
        async with con.transaction():
            res = await insert_with_unique_id(
                "chats",
                (
                    "name",
                    "colour",
                    "is_encrypted",
                    "is_personal",
                    "is_user_expandable",
                    "is_non_admin",
                    "non_removable_messages",
                    "non_modifiable_messages",
                    "auto_remove_messages",
                    "auto_remove_period",
                    "digest_messages",
                    "is_user_expandable_modified_by",
                    "is_non_admin_modified_by",
                    "non_removable_messages_modified_by",
                    "non_modifiable_messages_modified_by",
                    "auto_remove_messages_modified_by",
                    "digest_messages_modified_by",
                ),
                (
                    name,
                    colour,
                    is_encrypted,
                    is_personal,
                    is_user_expandable,
                    is_non_admin,
                    non_removable_messages,
                    non_modifiable_messages,
                    auto_remove_messages,
                    auto_remove_period,
                    digest_messages,
                    current_user,
                    current_user,
                    current_user,
                    current_user,
                    current_user,
                    current_user,
                ),
            )
            await __add__user_to_chat__(res, current_user, True)
    return await get_info(current_user, res)


@db_required
async def create_personal(current_user: str, user2: str) -> str:
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
            await __add__user_to_chat__(res["id"], current_user, True)
            await __add__user_to_chat__(res["id"], user2, True)
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
async def __set_propperty__(current_user: str, propperty: str, value: bool) -> bool:
    if await is_user_admin(current_user, chat_id) or (
        value and __is_chat_non_admin__(chat_id)
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
    return await __set_propperty__(current_user, "is_user_expandable", value)


@db_required
async def set_non_removable_messages(
    current_user: str, chat_id: str, value: bool
) -> bool:
    return await __set_propperty__(current_user, "non_removable_messages", value)


@db_required
async def set_non_modifiable_messages(
    current_user: str, chat_id: str, value: bool
) -> bool:
    return await __set_propperty__(current_user, "non_modifiable_messages", value)


@db_required
async def set_auto_remove_messages(
    current_user: str, chat_id: str, value: bool, period: Optional[int]
) -> bool:
    async with config.db.acquire() as con:
        async with con.transaction():
            await __set_propperty__(current_user, "non_removable_messages", value)
            await config.db.execute(
                "UPDATE chats SET auto_remove_period=$1 WHERE id=$2", period, chat_id
            )
    return True


@db_required
async def set_digest_messages(current_user: str, chat_id: str, value: bool) -> bool:
    return await __set_propperty__(current_user, "digest_messages", value)


@db_required
async def __message_add_extra_fields__(m: Dict[str, Any]) -> None:
    m["attachments"] = []
    for record in await config.db.fetch(
        "SELECT id FROM message_attachments WHERE message_id=$1", m["id"]
    ):
        m["attachments"].append(record["id"])
    m["tags"] = []
    for record in await config.db.fetch(
        "SELECT id FROM message_tags WHERE message_id=$1", m["id"]
    ):
        m["tags"].append(record["id"])


@db_required
async def __get_message__(
    message_id: str, include_extra_fields: bool = False
) -> Dict[str, Any]:
    if res := await config.db.fetchrow(
        "SELECT * FROM messages WHERE id=$1", message_id
    ):
        res = dict(res)
        if include_extra_fields:
            await __message_add_extra_fields__(res)
        return res
    raise ObjectNotFound()


@db_required
async def get_message(current_user: str, message_id: str):
    m = await __get_message__(message_id, True)
    if await has_user(current_user, m["chat_id"]):
        return m
    raise PermissionDenied()


@db_required
async def get_message_range(
    current_user: str, lower_id: Optional[str], upper_id: Optional[str], limit: int = 50
) -> List[Dict[str, Any]]:
    if not lower_id and not upper_id:
        raise InvalidRange()
    lower_message = await __get_message__(lower_id) if lower_id else None
    upper_message = await __get_message__(upper_id) if upper_id else None
    if (lower_message and upper_message) and (
        lower_message["chat_id"] != upper_message["chat_id"]
    ):
        raise InvalidRange()
    chat_id = lower_message["chat_id"] if lower_message else upper_message["chat_id"]
    if not await has_user(current_user, chat_id):
        raise PermissionDenied()
    if lower_message and upper_message:
        message_list = await config.db.fetch(
            "SELECT * FROM messages WHERE chat_id=$1 AND time BETWEEN $2 AND $3 ORDER BY time LIMIT $4",
            chat_id,
            lower_message["time"],
            upper_message["time"],
            limit,
        )
    elif not lower_message:
        message_list = await config.db.fetch(
            "SELECT * FROM messages WHERE chat_id=$1 AND time <= $2 ORDER BY time LIMIT $3",
            chat_id,
            upper_message["time"],
            limit,
        )
    elif not upper_message:
        message_list = await config.db.fetch(
            "SELECT * FROM messages WHERE chat_id=$1 AND time >= $2 ORDER BY time LIMIT $3",
            chat_id,
            lower_message["time"],
            limit,
        )
    for idx, item in enumerate(message_list):
        message_list[idx] = dict(item)
        await __message_add_extra_fields__(message_list[idx])
    return message_list


ATTACHMENT_IMAGE = 0
ATTACHMENT_DOCUMENT = 1


@db_required
async def send_message(
    current_user: str,
    chat_id: str,
    body: str,
    attachments: Optional[List[Tuple[int, str]]],
    tags: Optional[List[str]],
) -> Dict[str, Any]:
    if not await has_user(current_user, chat_id):
        raise PermissionDenied()
    async with config.db.acquire() as con:
        async with con.transaction():
            res = await insert_with_unique_id(
                "messages",
                ("chat_id", "author_id", "body", "time"),
                (chat_id, current_user, body, datetime.now()),
            )
            if attachments:
                for a in attachments:
                    if a[0] == ATTACHMENT_IMAGE:
                        col = "image_id"
                    elif a[0] == ATTACHMENT_DOCUMENT:
                        col = "document_id"
                    await insert_with_unique_id(
                        "message_attachments", ("message_id", col), (res, a[1])
                    )
            if tags:
                for t in tags:
                    await insert_with_unique_id(
                        "message_tags", ("message_id", "tag"), (res, t)
                    )
    return await __get_message__(res, True)


@db_required
async def edit_message(
    current_user: str,
    message_id: str,
    body: str,
    attachments: Optional[List[Tuple[int, str]]],
    tags: Optional[List[str]],
) -> bool:
    m = await __get_message__(message_id)
    c = await __get_info__(m["chat_id"])
    if m["author_id"] != current_user or c["non_modifiable_messages"]:
        raise PermissionDenied()
    async with config.db.acquire() as con:
        async with con.transaction():
            await config.db.execute(
                "UPDATE messages SET body=$1 WHERE id=$2", body, message_id
            )
            await config.db.execute(
                "DELETE FROM message_attachments WHERE message_id=$1", message_id
            )
            await config.db.execute(
                "DELETE FROM message_tags WHERE message_id=$1", message_id
            )
            if attachments:
                for a in attachments:
                    if a[0] == ATTACHMENT_IMAGE:
                        col = "image_id"
                    elif a[0] == ATTACHMENT_DOCUMENT:
                        col = "document_id"
                    await insert_with_unique_id(
                        "message_attachments", ("message_id", col), (message_id, a[1])
                    )
            if tags:
                for t in tags:
                    await insert_with_unique_id(
                        "message_tags", ("message_id", "tag"), (message_id, t)
                    )
    return True


@db_required
async def delete_message(current_user: str, message_id: str) -> bool:
    m = await __get_message__(message_id)
    c = await __get_info__(m["chat_id"])
    if m["author_id"] != current_user or c["non_removable_messages"]:
        raise PermissionDenied()
    await config.db.execute("DELETE FROM messages WHERE id=$1", message_id)
    return True


@db_required
async def get_chats_for_user(user_id: str) -> List[str]:
    chat_list = await config.db.fetch(
        "SELECT chat_id FROM chat_memberships WHERE user_id=$1", user_id
    )
    for idx, item in enumerate(chat_list):
        chat_list[idx] = item["chat_id"]
    return chat_list
