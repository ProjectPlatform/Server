import datetime
import json
import logging
import shutil
import uuid
from typing import Dict, Any, Optional, List, Tuple

from fastapi import APIRouter, HTTPException, Body, Depends, Query, UploadFile, File, WebSocket, status
from fastapi.encoders import jsonable_encoder
from firebase_admin import messaging, auth
import firebase_admin
from pydantic import EmailStr
from starlette.responses import JSONResponse, FileResponse

from app.app.backend.user import get_user_info
from app.app.backend import ObjectNotFound
from app.app.backend.exceptions import PermissionDenied
from app.app.src.schemas.chat import ChatCreate
from app.app.backend.chat import get_info, add_user, remove_user, make_user_admin, create, create_personal, \
    set_non_admin, set_user_expandable, set_non_removable_messages, set_non_modifiable_messages, \
    set_auto_remove_messages, set_digest_messages, get_message, get_message_range, send_message, edit_message, \
    delete_message, get_chats_for_user, get_messages_with_tag, create_upload_file, extract_tokens, \
    update_last_message_id, get_attachment
from app.app.src.security import decode_token, oauth2_scheme
from app.app.src.websockets import connections

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

router = APIRouter()


@router.get("/get_info")
async def req_get_info(chat_id: int, token: str = Depends(decode_token)) -> Dict[str, Any]:
    """
    **Obtain information about a chat.**

    Return a **dict** containing the following keys:

    * **id** - the id of the chat
    * **name** – the name of the chat
    * **creator** - the creator of the chat
    * **avatar** – the id of an image containing the chat's avatar
    * **colour_rgba** – the RGB value of the chat's colour
    * **encoded** – whether the chat is encrypted
    * **tag_list** – a list containing all tags used in this chat
    * **admins** – a list containing the user ids of the chat's admins
    * **users** – a list containing the ids of the chat's participants who are not admins

    **Exceptions:**
    * Status code **403**
    * Status code **404**
    """
    try:
        # log.info(token)
        user_id = token["id"]
        received_info = await get_info(current_user=user_id, chat_id=chat_id)
        logging.info(received_info)
        return received_info
    except ObjectNotFound:
        raise HTTPException(status_code=404, detail="Page not found")
    except PermissionDenied:
        raise HTTPException(status_code=403, detail="Permission denied")


@router.post("/add_user")
async def req_add_user(chat_id: int, user_id: Optional[int] = None, user_nick: Optional[str] = None,
                       user_email: Optional[EmailStr] = None,
                       token: str = Depends(decode_token)) -> Any:
    """
    **Add a user to the chat with the given id.**

    Return JSON string `{'result': true}`.

    **Exceptions:**
    * Status code **403**
    """
    #try:
    cur_user_id = token["id"]
    log.info(cur_user_id)
    user_to_add = await get_user_info(user_id=user_id, user_nick=user_nick, user_email=user_email)

    result = await add_user(current_user=cur_user_id, chat_id=chat_id, user_to_add=user_to_add["id"])
    if not result:
        raise ObjectNotFound()
    # result = await add_user(**info.dict(), user_to_add=user_to_add)
    # return {'result': result}

    message = await send_message(current_user=1, chat_id=chat_id,
                                 body=user_to_add["nick"] + " has joined the chat.", tags=[])
    return message

    # except PermissionDenied:
    #     raise HTTPException(status_code=403, detail="Permission denied")
    # except ObjectNotFound:
    #     raise HTTPException(status_code=404, detail="Page not found")


@router.delete("/remove_user")
async def req_remove_user(chat_id: int, user_id: Optional[int] = None, user_nick: Optional[str] = None,
                          user_email: Optional[EmailStr] = None,
                          token: str = Depends(decode_token)) -> Any:
    """
    **Remove a user from the chat with the given id.**

    Return JSON string `{'result': true}`.

    **Exceptions:**
    * Status code **403**
    * Status code **404**
    """
    try:
        cur_user_id = token["id"]

        user_to_remove = await get_user_info(user_id=user_id, user_nick=user_nick, user_email=user_email)

        result = await remove_user(current_user=cur_user_id, chat_id=chat_id, user_to_remove=user_to_remove["id"])
        if not result:
            raise ObjectNotFound()

        message = await send_message(current_user=1, chat_id=chat_id,
                                     body=user_to_remove["nick"] + " has left the chat.", tags=[])
        return message
    except PermissionDenied:
        raise HTTPException(status_code=403, detail="Permission denied")
    except ObjectNotFound:
        raise HTTPException(status_code=404, detail="Page not found")


@router.post('/make_user_admin')
async def req_make_user_admin(chat_id: int, target_user: int, token: str = Depends(decode_token)) -> Any:
    """
    **Make a user an admin of the given chat.**

    Return JSON string `{'result': true}`.

    **Exceptions:**
    * Status code **403**
    """
    try:
        user_id = token["id"]
        result = await make_user_admin(current_user=user_id, chat_id=chat_id, target_user=target_user)
        return {'result': result}
    except PermissionDenied:
        raise HTTPException(status_code=403, detail="Permission denied")


@router.post('/create')
async def req_create_chat(info: ChatCreate, token: str = Depends(decode_token)) -> Any:
    """
    **Create a new chat.**

    Return a **dict** containing the following keys:

    * **id** - the id of the chat
    * **name** – the name of the chat
    * **creator** - the creator of the chat
    * **avatar** – the id of an image containing the chat's avatar
    * **colour_rgba** – the RGB value of the chat's colour
    * **encoded** – whether the chat is encrypted
    * **tag_list** – a list containing all tags used in this chat
    * **admins** – a list containing the user ids of the chat's admins
    * **users** – a list containing the ids of the chat's participants who are not admins

    **Exceptions:**
    * Status code **403**
    """
    try:
        # chat = await create("str","str",0,False,False,False, False, False,False, False,0,False)
        user_id = token["id"]
        chat = await create(current_user_id=user_id, **info.dict())
        return chat
    except PermissionDenied:
        raise HTTPException(status_code=403, detail="Permission denied")


@router.post('/create_personal', deprecated=True)
async def req_create_personal(current_user: int, user2: int, token: str = Depends(decode_token)) -> Dict[str, Any]:
    try:
        chat = await create_personal(current_user=current_user, user2=user2)
        return chat
    except PermissionDenied:
        raise HTTPException(status_code=403, detail="Permission denied")


@router.post('/set_non_admin')
async def req_set_non_admin(current_user: str, chat_id: str, value: bool, token: str = Depends(decode_token)) -> Any:
    """
    **Set the value of the non_admin property.**

    Return JSON string `{'result': true}`.

    **Exceptions:**
    * Status code **403**
    """
    try:
        result = await set_non_admin(current_user=current_user, chat_id=chat_id, value=value)
        return {'result': result}
    except PermissionDenied:
        raise HTTPException(status_code=403, detail="Permission denied")


@router.post('/set_user_expandable', deprecated=True)
async def req_set_user_expandable(current_user: str, chat_id: str, value: bool,
                                  token: str = Depends(decode_token)) -> Any:
    try:
        result = await set_user_expandable(current_user=current_user, chat_id=chat_id, value=value)
        return {'result': result}
    except PermissionDenied:
        raise HTTPException(status_code=403, detail="Permission denied")


@router.post('/set_non_removable_messages', deprecated=True)
async def req_set_non_removable_messages(current_user: str, chat_id: str, value: bool,
                                         token: str = Depends(decode_token)) -> Any:
    try:
        result = await set_non_removable_messages(current_user=current_user, chat_id=chat_id, value=value)
        return {'result': result}
    except PermissionDenied:
        raise HTTPException(status_code=403, detail="Permission denied")


@router.post('/set_non_modifiable_messages', deprecated=True)
async def req_set_non_modifiable_messages(current_user: str, chat_id: str, value: bool,
                                          token: str = Depends(decode_token)) -> Any:
    try:
        result = await set_non_modifiable_messages(current_user=current_user, chat_id=chat_id, value=value)
        return {'result': result}
    except PermissionDenied:
        raise HTTPException(status_code=403, detail="Permission denied")


@router.post('/set_auto_remove_messages', deprecated=True)
async def req_set_auto_remove_messages(current_user: str, chat_id: str, value: bool,
                                       token: str = Depends(decode_token)) -> Any:
    try:
        result = await set_auto_remove_messages(current_user=current_user, chat_id=chat_id, value=value)
        return {'result': result}
    except PermissionDenied:
        raise HTTPException(status_code=403, detail="Permission denied")


@router.post('/set_digest_messages', deprecated=True)
async def req_set_digest_messages(current_user: str, chat_id: str, value: bool,
                                  token: str = Depends(decode_token)) -> Any:
    try:
        result = await set_digest_messages(current_user=current_user, chat_id=chat_id, value=value)
        return {'result': result}
    except PermissionDenied:
        raise HTTPException(status_code=403, detail="Permission denied")


@router.get('/get_message')
async def req_get_message(message_id: int, token: str = Depends(decode_token)) -> Any:
    """
    **Get the contents of a message.**

    Return a **dict** containing the following keys:

    * **id** – the id of the message
    * **chat_attached_id** – the id of the chat to which this message belongs
    * **author_id** – the id of the user who sent the message
    * **sent_time** – the time when the message was sent. Represented by a datetime object
    * **body** – the body of the message
    * **has_attached_file** - whether the message has attached file
    * **attachments** – a list containing the ids of this message's attachments
    * **tags** – the list of tags of this message

    **Exceptions:**
    * Status code **403**
    * Status code **404**
    """
    try:
        user_id = token["id"]
        message = await get_message(current_user=user_id, message_id=message_id)
        return message
    except PermissionDenied:
        raise HTTPException(status_code=403, detail="Permission denied")
    except ObjectNotFound:
        raise HTTPException(status_code=404, detail="Page not found")


@router.get('/get_message_range')
async def req_get_message_range(chat_id: int, limit: int = 50, token: str = Depends(decode_token)) -> Any:
    """
    **Retrieve messages in the specified time range in a specific chat.**

    Return a **list** containing messages (the same as get_message)

    **Exceptions:**
    * Status code **403**
    * Status code **404**
    """
    try:
        user_id = token["id"]
        messages = await get_message_range(current_user=user_id, chat_id=chat_id, limit=limit)
        #log.info(messages)
        messages = jsonable_encoder(messages)
        return JSONResponse(content=messages)
    except PermissionDenied:
        raise HTTPException(status_code=403, detail="Permission denied")
    except ObjectNotFound:
        raise HTTPException(status_code=404, detail="Page not found")


@router.get("/get_attachments/{file_id}")
async def get_attachments(file_id: int):
    path = await get_attachment(file_id=file_id)
    return FileResponse(path=path, media_type='application/octet-stream', filename=path[12:])


@router.post("/upload_attachments")
async def upload_attachments(is_showable: bool = True, description: Optional[str] = None,
                             files: List[UploadFile] = File(...),
                             token: str = Depends(decode_token)):
    """
    Upload files to the app's servers

    Return JSON string `{'result': ids}`, where **ids** is a list containing file ids

    **Exceptions:**
    * Status code **403**
    """
    try:
        attachments_id = []
        user_id = token["id"]
        for file in files:
            attachment_id = await create_upload_file(uploaded_file=file, current_user=user_id, description=description,
                                                     is_showable=is_showable)
            attachments_id.append(attachment_id)
        return {'ids': attachments_id}
    except PermissionDenied:
        raise HTTPException(status_code=403, detail="Permission denied")


@router.post('/send_message')
async def req_send_message(chat_id: int, body: str = Body(...),
                           attachments: Optional[List[int]] = [],
                           tags: Optional[List[str]] = None, token: str = Depends(decode_token), ) -> Any:
    """
    **Send a message to the specified chat.**

    Return a **dict** containing the following keys:

    * **id** – the id of the message
    * **chat_attached_id** – the id of the chat to which this message belongs
    * **author_id** – the id of the user who sent the message
    * **sent_time** – the time when the message was sent. Represented by a datetime object
    * **tag_list** – the list of tags of this message
    * **body** – the body of the message
    * **has_attached_file** - whether the message has attached file
    * **message_type** - type of message (message or notification or something else)

    **Exceptions**
    * Status code **403**
    """
    try:
        user_id = token["id"]

        log.info("message_test:" + body)
        message = await send_message(current_user=user_id, chat_id=chat_id, body=body, attachments=attachments,
                                     tags=tags)
        # await update_last_message_id(chat_id=chat_id, message_id=message["id"])
        # chat_info = await get_info(current_user=user_id, chat_id=chat_id)
        #
        # token_list = await extract_tokens(current_user=user_id, users=chat_info["users"])
        #
        # message.update({"message_type": "message"})
        # # token_list = token_list["devices_token_list"]
        # log.info(token_list)
        # # logger.info(message["body"])
        #
        # # Send message on android
        # message_firebase = messaging.MulticastMessage(
        #     notification=messaging.Notification(
        #         title=chat_info["name"],
        #         body=user_nick + ": " + message["body"],
        #     ),
        #     data={'data': json.dumps({**message}, indent=4, sort_keys=True, default=str)},
        #     # json.dumps(message,  indent=4, sort_keys=True, default=str),
        #     tokens=token_list
        # )
        # response = messaging.send_multicast(message_firebase)
        # print('Successfully sent message:', response)
        #
        # # Send message to PC client
        # for chat_user in chat_info["users"]:
        #     ws = connections.active_connections.get(chat_user)
        #     log.info(ws)
        #     if ws is not None and ws is not user_id:
        #         log.info("Websocket send message")
        #         await ws.send_bytes(json.dumps({**message}, indent=4, sort_keys=True, default=str))

        return message
    except PermissionDenied:
        raise HTTPException(status_code=403, detail="Permission denied")


@router.post('/edit_message')
async def req_edit_message(message_id: int, body: str, attachments: Optional[List[Tuple[int, str]]] = None
                           , tags: Optional[List[str]] = None, token: str = Depends(decode_token), ) -> Any:
    """
    **Edit a message.**

    Return JSON string `{'result': true}`.

    **Exceptions:**
    * Status code **403**
    """
    try:
        user_id = token["id"]
        message = await edit_message(current_user=user_id, message_id=message_id, body=body, attachments=attachments,
                                     tags=tags, )
        return message
    except PermissionDenied:
        raise HTTPException(status_code=403, detail="Permission denied")


@router.delete('/delete_message')
async def req_delete_message(message_id: int, token: str = Depends(decode_token)) -> Any:
    """
        **Delete a message.**

        Return JSON string `{'result': true}`.

        **Exceptions:**
        * Status code **403**
        """
    try:
        user_id = token["id"]
        result = await delete_message(current_user=user_id, message_id=message_id)
        return {'result': result}
    except PermissionDenied:
        raise HTTPException(status_code=403, detail="Permission denied")


@router.get('/get_chats_for_user')
async def req_get_chats_for_user(token: str = Depends(decode_token)) -> Any:
    # async def req_get_chats_for_user(user_id: str, token: str = Depends(decode_token)) -> Any:
    """
    **Retrieve the list of chats for a user.**

    Return the **list** of chats for a user.

    **Exceptions:**
    * Status code **403**
    """
    try:
        user_id = token["id"]
        ids = await get_chats_for_user(user_id=user_id)
        return {'chats': ids}
    except PermissionDenied:
        raise HTTPException(status_code=403, detail="Permission denied")
    # except Exception as e:
    #     raise HTTPException(status_code=500, detail="Something went wrong, but we are already working on it :)")


@router.get('/get_messages_with_tag')
async def req_get_messages_with_tag(chat_id: int, tag: str,
                                    token: str = Depends(decode_token)) -> Any:
    """
    **Retrieve messages with the specified tag in a specific chat.**

    Return a **list** containing messages (the same as get_message)

    **Exceptions:**
    * Status code **403**
    * Status code **404**
    """
    try:
        user_id = token["id"]
        messages = await get_messages_with_tag(current_user=user_id, chat_id=chat_id, tag=tag)
        return messages
    except PermissionDenied:
        raise HTTPException(status_code=403, detail="Permission denied")
    except ObjectNotFound:
        raise HTTPException(status_code=404, detail="Page not found")
