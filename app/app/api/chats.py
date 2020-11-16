from typing import Dict, Any, Optional, List, Tuple

from fastapi import APIRouter, HTTPException, Query, Body
from fastapi.encoders import jsonable_encoder

from app.app.backend import ObjectNotFound
from app.app.backend.exceptions import PermissionDenied
from app.app.src.schemas.chat import ChatMinimalInfo, ChatOut, ChatCreate
from app.app.backend.chat import get_info, add_user, remove_user, make_user_admin, create, create_personal, \
    set_non_admin, set_user_expandable, set_non_removable_messages, set_non_modifiable_messages, \
    set_auto_remove_messages, set_digest_messages, get_message, get_message_range, send_message, edit_message, \
    delete_message, get_chats_for_user, get_messages_with_tag

router = APIRouter()


@router.post("/get_info", response_model=ChatOut)
async def req_get_info(*, info: ChatMinimalInfo = Body(...)) -> Dict[str, Any]:
    try:
        received_info = await get_info(**info.dict())
        return received_info
    except ObjectNotFound:
        raise HTTPException(status_code=404, detail="Page not found")
    except PermissionDenied:
        raise HTTPException(status_code=401, detail="Permission denied")


@router.post("/add_user")
async def req_add_user(info: ChatMinimalInfo, user_to_add: str) -> Any:
    try:
        result = await add_user(**info.dict(), user_to_add=user_to_add)
        return {'result': result}
    except PermissionDenied:
        raise HTTPException(status_code=401, detail="Permission denied")


@router.delete("/remove_user")
async def req_remove_user(*, info: ChatMinimalInfo, user_to_remove: str = Body(...)) -> Any:
    try:
        result = await remove_user(**info.dict(), user_to_remove=user_to_remove)
        return {'result': result}
    except PermissionDenied:
        raise HTTPException(status_code=401, detail="Permission denied")


@router.post('/make_user_admin')
async def req_make_user_admin(info: ChatMinimalInfo, target_user: str) -> Any:
    try:
        result = await make_user_admin(**info.dict(), target_user=target_user)
        return {'result': result}
    except PermissionDenied:
        raise HTTPException(status_code=401, detail="Permission denied")


@router.post('/create')
async def req_create_chat(info: ChatCreate) -> Any:
    try:
        #chat = await create("str","str",0,False,False,False, False, False,False, False,0,False)
        chat = await create(**info.dict())
        return chat
    except PermissionDenied:
        raise HTTPException(status_code=401, detail="Permission denied")


@router.post('/create_personal')
async def req_create_personal(current_user: str, user2: str) -> Dict[str, Any]:
    try:
        chat = await create_personal(current_user=current_user, user2=user2)
        return chat
    except PermissionDenied:
        raise HTTPException(status_code=401, detail="Permission denied")


@router.post('/set_non_admin')
async def req_set_non_admin(current_user: str, chat_id: str, value: bool) -> Any:
    try:
        result = await set_non_admin(current_user=current_user, chat_id=chat_id, value=value)
        return {'result': result}
    except PermissionDenied:
        raise HTTPException(status_code=401, detail="Permission denied")


@router.post('/set_user_expandable')
async def req_set_user_expandable(current_user: str, chat_id: str, value: bool) -> Any:
    try:
        result = await set_user_expandable(current_user=current_user, chat_id=chat_id, value=value)
        return {'result': result}
    except PermissionDenied:
        raise HTTPException(status_code=401, detail="Permission denied")


@router.post('/set_non_removable_messages')
async def req_set_non_removable_messages(current_user: str, chat_id: str, value: bool) -> Any:
    try:
        result = await set_non_removable_messages(current_user=current_user, chat_id=chat_id, value=value)
        return {'result': result}
    except PermissionDenied:
        raise HTTPException(status_code=401, detail="Permission denied")


@router.post('/set_non_modifiable_messages')
async def req_set_non_modifiable_messages(current_user: str, chat_id: str, value: bool) -> Any:
    try:
        result = await set_non_modifiable_messages(current_user=current_user, chat_id=chat_id, value=value)
        return {'result': result}
    except PermissionDenied:
        raise HTTPException(status_code=401, detail="Permission denied")


@router.post('/set_auto_remove_messages')
async def req_set_auto_remove_messages(current_user: str, chat_id: str, value: bool) -> Any:
    try:
        result = await set_auto_remove_messages(current_user=current_user, chat_id=chat_id, value=value)
        return {'result': result}
    except PermissionDenied:
        raise HTTPException(status_code=401, detail="Permission denied")


@router.post('/set_digest_messages')
async def req_set_digest_messages(current_user: str, chat_id: str, value: bool) -> Any:
    try:
        result = await set_digest_messages(current_user=current_user, chat_id=chat_id, value=value)
        return {'result': result}
    except PermissionDenied:
        raise HTTPException(status_code=401, detail="Permission denied")


@router.get('/get_message')
async def req_get_message(current_user: str, message_id: str) -> Any:
    try:
        message = await get_message(current_user=current_user, message_id=message_id)
        return message
    except ObjectNotFound:
        raise HTTPException(status_code=404, detail="Page not found")
    except PermissionDenied:
        raise HTTPException(status_code=401, detail="Permission denied")


@router.get('/get_message_range')
async def req_get_message_range(current_user: str, lower_id: Optional[str], upper_id: Optional[str],
                                limit: int = 50) -> Any:
    try:
        messages = await get_message_range(current_user=current_user, lower_id=lower_id, upper_id=upper_id, limit=limit)
        return messages
    except ObjectNotFound:
        raise HTTPException(status_code=404, detail="Page not found")
    except PermissionDenied:
        raise HTTPException(status_code=401, detail="Permission denied")


@router.post('/send_message')
async def req_send_message(current_user: str, chat_id: str, body: str,
                           attachments: Optional[List[Tuple[int, str]]] = None
                           , tags: Optional[List[str]] = None, ) -> Any:
    try:
        message = await send_message(current_user=current_user, chat_id=chat_id, body=body, attachments=attachments,
                                     tags=tags)
        return message
    except PermissionDenied:
        raise HTTPException(status_code=401, detail="Permission denied")


@router.post('/edit_message')
async def req_edit_message(current_user: str, chat_id: str, body: str,
                           attachments: Optional[List[Tuple[int, str]]] = None
                           , tags: Optional[List[str]] = None, ) -> Any:
    try:
        message = await edit_message(current_user=current_user, chat_id=chat_id, body=body, attachments=attachments,
                                     tags=tags, )
        return message
    except PermissionDenied:
        raise HTTPException(status_code=401, detail="Permission denied")


@router.delete('/delete_message')
async def req_delete_message(current_user: str, message_id: str) -> Any:
    try:
        result = await delete_message(current_user=current_user, message_id=message_id)
        return {'result': result}
    except PermissionDenied:
        raise HTTPException(status_code=401, detail="Permission denied")


@router.get('/get_chats_for_user')
async def req_get_chats_for_user(user_id: str) -> Any:
    try:
        ids = await get_chats_for_user(user_id=user_id)
        return ids
    except PermissionDenied:
        raise HTTPException(status_code=401, detail="Permission denied")
    except Exception as e:
        raise HTTPException(status_code=500, detail="Something went wrong, but we are already working on it :)")


@router.get('/get_messages_with_tag')
async def req_get_messages_with_tag(current_user: str, chat_id: str, tag: str) -> Any:
    try:
        messages = await get_messages_with_tag(current_user=current_user, chat_id=chat_id, tag=tag)
        return messages
    except PermissionDenied:
        raise HTTPException(status_code=401, detail="Permission denied")
