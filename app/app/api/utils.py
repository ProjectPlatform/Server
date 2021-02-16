import os
from typing import List, Optional

from fastapi import APIRouter, UploadFile, Depends, File, HTTPException
from starlette.responses import FileResponse

from app.app.backend.chat import create_upload_file, get_attachment
from app.app.backend.utils import get_attachment
from app.app.backend.exceptions import PermissionDenied, ObjectNotFound
from app.app.src.security import decode_token

router = APIRouter()


@router.post("/upload_attachments")
async def upload_attachments(is_showable: bool = True, description: Optional[str] = None,
                             files: List[UploadFile] = File(...), token: str = Depends(decode_token)):
    """
    Upload files to the app's servers

    Return JSON string `{'result': ids}`, where **ids** is a list containing file ids

    **Exceptions:**
    * Status code **403**
    """
    try:
        user_id = token["id"]
        attachment_ids = await create_upload_file(uploaded_files=files, current_user=user_id, description=description,
                                                  is_showable=is_showable)
        return {'uris': attachment_ids}
    except PermissionDenied:
        raise HTTPException(status_code=403, detail="Permission denied")


@router.get("/download_attachments/{file_uri}")
async def get_attachments(file_uri: str, token: str = Depends(decode_token)):
    try:
        user_id = token["id"]
        path = await get_attachment(file_uri=file_uri)
        return FileResponse(path=path, media_type='application/octet-stream', filename=os.path.basename(path))
    except ObjectNotFound:
        raise HTTPException(status_code=404, detail="Resource wasn't found")

