from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, Form
from fastapi.staticfiles import StaticFiles
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
import os
import uuid
import aiofiles
from datetime import datetime

from app.config import settings
from app.database import get_db

router = APIRouter(prefix="/api/uploads", tags=["图片上传管理"])


def _get_extension(filename: str) -> str:
    return filename.rsplit(".", 1)[1].lower() if "." in filename else ""


def _allowed_file(filename: str) -> bool:
    return _get_extension(filename) in settings.ALLOWED_IMAGE_EXTENSIONS


@router.post("")
async def upload_image(
    file: UploadFile = File(...),
    folder: Optional[str] = Form("general"),
    db: AsyncSession = Depends(get_db)
):
    if not file:
        raise HTTPException(status_code=400, detail="未上传文件，请选择图片后重试")

    if not _allowed_file(file.filename):
        allowed_formats = ", ".join(sorted(settings.ALLOWED_IMAGE_EXTENSIONS)).upper()
        raise HTTPException(
            status_code=400,
            detail=f"不支持的文件格式「{file.filename}」，仅支持 {allowed_formats} 格式"
        )

    file_size = 0
    content = await file.read()
    file_size = len(content)
    if file_size > settings.MAX_UPLOAD_SIZE:
        max_size_mb = settings.MAX_UPLOAD_SIZE // 1024 // 1024
        raise HTTPException(
            status_code=400,
            detail=f"文件过大「{file.filename}」({file_size // 1024}KB)，单张图片最大支持 {max_size_mb}MB"
        )

    ext = _get_extension(file.filename)
    date_folder = datetime.now().strftime("%Y%m%d")
    target_dir = os.path.join(settings.UPLOAD_DIR, folder, date_folder)
    os.makedirs(target_dir, exist_ok=True)

    unique_name = f"{uuid.uuid4().hex}.{ext}"
    file_path = os.path.join(target_dir, unique_name)

    async with aiofiles.open(file_path, "wb") as f:
        await f.write(content)

    relative_path = f"/static/uploads/{folder}/{date_folder}/{unique_name}"
    file_url = relative_path

    return {
        "url": file_url,
        "filename": unique_name,
        "original_name": file.filename,
        "size": file_size,
        "path": file_path
    }


@router.post("/batch")
async def upload_batch_images(
    files: list[UploadFile] = File(...),
    folder: Optional[str] = Form("general"),
    db: AsyncSession = Depends(get_db)
):
    results = []
    for file in files:
        try:
            result = await upload_image(file, folder, db)
            results.append(result)
        except Exception as e:
            results.append({"error": str(e), "filename": file.filename})
    return {"uploaded": len(results), "results": results}


@router.delete("")
async def delete_image(file_path: str, db: AsyncSession = Depends(get_db)):
    if not file_path:
        raise HTTPException(status_code=400, detail="文件路径不能为空")

    abs_path = os.path.join(settings.BASE_DIR, file_path.lstrip("/").replace("static/", ""))
    if os.path.exists(abs_path) and os.path.isfile(abs_path):
        os.remove(abs_path)
        return {"message": "删除成功"}
    raise HTTPException(status_code=404, detail="文件不存在")
