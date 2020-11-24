import json
from typing import Dict, Any, Optional, List, Tuple

from fastapi import APIRouter, HTTPException, Body, Depends, Query

from app.app.backend import ObjectNotFound
from app.app.backend.exceptions import PermissionDenied
from app.app.src.schemas.chat import ChatMinimalInfo, ChatCreate
from app.app.backend.chat import get_info, add_user, remove_user, make_user_admin, create, create_personal, \
    set_non_admin, set_user_expandable, set_non_removable_messages, set_non_modifiable_messages, \
    set_auto_remove_messages, set_digest_messages, get_message, get_message_range, send_message, edit_message, \
    delete_message, get_chats_for_user, get_messages_with_tag
from app.app.src.security import decode_token

router = APIRouter()


@router.get("/get_info")
async def req_get_info(chat_id: int, token: str = Depends(decode_token)) -> Dict[str, Any]:
    try:
        user_id = token["id"]
        received_info = await get_info(current_user=user_id, chat_id=chat_id)
        return received_info
    except ObjectNotFound:
        raise HTTPException(status_code=404, detail="Page not found")
    except PermissionDenied:
        raise HTTPException(status_code=401, detail="Permission denied")


@router.post("/add_user")
async def req_add_user(chat_id: int, user_to_add: int, token: str = Depends(decode_token)) -> Any:
    try:
        user_id = token["id"]
        result = await add_user(current_user=user_id, chat_id=chat_id, user_to_add=user_to_add)
        # result = await add_user(**info.dict(), user_to_add=user_to_add)
        return {'result': result}
    except PermissionDenied:
        raise HTTPException(status_code=401, detail="Permission denied")


@router.delete("/remove_user")
async def req_remove_user(chat_id: int, user_to_remove: int, token: str = Depends(decode_token)) -> Any:
    try:
        user_id = token["id"]
        result = await remove_user(current_user=user_id, chat_id=chat_id, user_to_remove=user_to_remove)
        return {'result': result}
    except PermissionDenied:
        raise HTTPException(status_code=401, detail="Permission denied")


@router.post('/make_user_admin')
async def req_make_user_admin(chat_id: int, target_user: int, token: str = Depends(decode_token)) -> Any:
    try:
        user_id = token["id"]
        result = await make_user_admin(current_user=user_id, chat_id=chat_id, target_user=target_user)
        return {'result': result}
    except PermissionDenied:
        raise HTTPException(status_code=401, detail="Permission denied")


@router.post('/create')
async def req_create_chat(info: ChatCreate, token: str = Depends(decode_token)) -> Any:
    try:
        # chat = await create("str","str",0,False,False,False, False, False,False, False,0,False)
        user_id = token["id"]
        chat = await create(current_user_id=user_id, **info.dict())
        return chat
    except PermissionDenied:
        raise HTTPException(status_code=401, detail="Permission denied")


@router.post('/create_personal')
async def req_create_personal(current_user: int, user2: int, token: str = Depends(decode_token)) -> Dict[str, Any]:
    try:
        chat = await create_personal(current_user=current_user, user2=user2)
        return chat
    except PermissionDenied:
        raise HTTPException(status_code=401, detail="Permission denied")


@router.post('/set_non_admin')
async def req_set_non_admin(current_user: str, chat_id: str, value: bool, token: str = Depends(decode_token)) -> Any:
    try:
        result = await set_non_admin(current_user=current_user, chat_id=chat_id, value=value)
        return {'result': result}
    except PermissionDenied:
        raise HTTPException(status_code=401, detail="Permission denied")


@router.post('/set_user_expandable')
async def req_set_user_expandable(current_user: str, chat_id: str, value: bool,
                                  token: str = Depends(decode_token)) -> Any:
    try:
        result = await set_user_expandable(current_user=current_user, chat_id=chat_id, value=value)
        return {'result': result}
    except PermissionDenied:
        raise HTTPException(status_code=401, detail="Permission denied")


@router.post('/set_non_removable_messages')
async def req_set_non_removable_messages(current_user: str, chat_id: str, value: bool,
                                         token: str = Depends(decode_token)) -> Any:
    try:
        result = await set_non_removable_messages(current_user=current_user, chat_id=chat_id, value=value)
        return {'result': result}
    except PermissionDenied:
        raise HTTPException(status_code=401, detail="Permission denied")


@router.post('/set_non_modifiable_messages')
async def req_set_non_modifiable_messages(current_user: str, chat_id: str, value: bool,
                                          token: str = Depends(decode_token)) -> Any:
    try:
        result = await set_non_modifiable_messages(current_user=current_user, chat_id=chat_id, value=value)
        return {'result': result}
    except PermissionDenied:
        raise HTTPException(status_code=401, detail="Permission denied")


@router.post('/set_auto_remove_messages')
async def req_set_auto_remove_messages(current_user: str, chat_id: str, value: bool,
                                       token: str = Depends(decode_token)) -> Any:
    try:
        result = await set_auto_remove_messages(current_user=current_user, chat_id=chat_id, value=value)
        return {'result': result}
    except PermissionDenied:
        raise HTTPException(status_code=401, detail="Permission denied")


@router.post('/set_digest_messages')
async def req_set_digest_messages(current_user: str, chat_id: str, value: bool,
                                  token: str = Depends(decode_token)) -> Any:
    try:
        result = await set_digest_messages(current_user=current_user, chat_id=chat_id, value=value)
        return {'result': result}
    except PermissionDenied:
        raise HTTPException(status_code=401, detail="Permission denied")


@router.get('/get_message')
async def req_get_message(message_id: int, token: str = Depends(decode_token)) -> Any:
    try:
        user_id = token["id"]
        message = await get_message(current_user=user_id, message_id=message_id)
        return message
    except ObjectNotFound:
        raise HTTPException(status_code=404, detail="Page not found")
    except PermissionDenied:
        raise HTTPException(status_code=401, detail="Permission denied")


@router.get('/get_message_range')
async def req_get_message_range(lower_id: Optional[int] = None, upper_id: Optional[int] = 100,
                                limit: int = 50, token: str = Depends(decode_token)) -> Any:
    try:
        user_id = token["id"]
        messages = await get_message_range(current_user=user_id, lower_id=lower_id, upper_id=upper_id, limit=limit)
        return messages
    except ObjectNotFound:
        raise HTTPException(status_code=404, detail="Page not found")
    except PermissionDenied:
        raise HTTPException(status_code=401, detail="Permission denied")


@router.post('/send_message')
async def req_send_message(chat_id: int, body: str = Body(...),
                           attachments: Optional[List[Tuple[int, str]]] = (0, 0)
                           , tags: Optional[List[str]] = None, token: str = Depends(decode_token), ) -> Any:
    # TODO fix request in docs
    try:
        user_id = token["id"]
        message = await send_message(current_user=user_id, chat_id=chat_id, body=body, attachments=attachments,
                                     tags=tags)
        return message
    except PermissionDenied:
        raise HTTPException(status_code=401, detail="Permission denied")


@router.post('/edit_message')
async def req_edit_message(message_id: int, body: str, attachments: Optional[List[Tuple[int, str]]] = None
                           , tags: Optional[List[str]] = None, token: str = Depends(decode_token), ) -> Any:
    try:
        user_id = token["id"]
        message = await edit_message(current_user=user_id, message_id=message_id, body=body, attachments=attachments,
                                     tags=tags, )
        return message
    except PermissionDenied:
        raise HTTPException(status_code=401, detail="Permission denied")


@router.delete('/delete_message')
async def req_delete_message(message_id: int, token: str = Depends(decode_token)) -> Any:
    try:
        user_id = token["id"]
        result = await delete_message(current_user=user_id, message_id=message_id)
        return {'result': result}
    except PermissionDenied:
        raise HTTPException(status_code=401, detail="Permission denied")


@router.get('/get_chats_for_user')
async def req_get_chats_for_user(token: str = Depends(decode_token)) -> Any:
    # async def req_get_chats_for_user(user_id: str, token: str = Depends(decode_token)) -> Any:
    try:
        user_id = token["id"]
        ids = await get_chats_for_user(user_id=user_id)
        return {'chats': ids}
    except PermissionDenied:
        raise HTTPException(status_code=401, detail="Permission denied")
    # except Exception as e:
    #     raise HTTPException(status_code=500, detail="Something went wrong, but we are already working on it :)")


@router.get('/get_messages_with_tag')
async def req_get_messages_with_tag(chat_id: int, tag: str,
                                    token: str = Depends(decode_token)) -> Any:
    try:
        user_id = token["id"]
        messages = await get_messages_with_tag(current_user=user_id, chat_id=chat_id, tag=tag)
        return messages
    except PermissionDenied:
        raise HTTPException(status_code=401, detail="Permission denied")
