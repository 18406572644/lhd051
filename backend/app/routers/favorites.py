from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from typing import Optional

from app.database import get_db
from app.models import Favorite, Specimen, TechniqueNote, DesignPlan, ProductImage
from app.schemas import FavoriteCreate, FavoriteResponse, PaginatedResponse

router = APIRouter(prefix="/api/favorites", tags=["内容收藏管理"])


@router.get("", response_model=PaginatedResponse)
async def get_favorites(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    favorite_type: Optional[str] = None,
    folder: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    stmt = select(Favorite)
    conditions = []
    if favorite_type:
        conditions.append(Favorite.favorite_type == favorite_type)
    if folder:
        conditions.append(Favorite.folder == folder)
    if conditions:
        stmt = stmt.where(and_(*conditions))

    count_stmt = select(func.count()).select_from(stmt.subquery())
    total = await db.scalar(count_stmt)

    stmt = stmt.order_by(Favorite.created_at.desc()).offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(stmt)
    items = result.scalars().all()
    resp_items = [FavoriteResponse.model_validate(it) for it in items]

    return PaginatedResponse(total=total, page=page, page_size=page_size, items=resp_items)


@router.post("", response_model=FavoriteResponse)
async def create_favorite(data: FavoriteCreate, db: AsyncSession = Depends(get_db)):
    check_conditions = [Favorite.favorite_type == data.favorite_type, Favorite.folder == data.folder]
    if data.favorite_type == "specimen" and data.specimen_id:
        check_conditions.append(Favorite.specimen_id == data.specimen_id)
    elif data.favorite_type == "note" and data.note_id:
        check_conditions.append(Favorite.note_id == data.note_id)
    elif data.favorite_type == "plan" and data.plan_id:
        check_conditions.append(Favorite.plan_id == data.plan_id)
    elif data.favorite_type == "image" and data.image_id:
        check_conditions.append(Favorite.image_id == data.image_id)

    check_stmt = select(Favorite).where(and_(*check_conditions))
    check_result = await db.execute(check_stmt)
    if check_result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="该内容已在此收藏夹中")

    item = Favorite(**data.model_dump(exclude_none=True))
    db.add(item)
    await db.commit()
    await db.refresh(item)
    return item


@router.delete("/{item_id}")
async def delete_favorite(item_id: int, db: AsyncSession = Depends(get_db)):
    stmt = select(Favorite).where(Favorite.id == item_id)
    result = await db.execute(stmt)
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="收藏不存在")
    await db.delete(item)
    await db.commit()
    return {"message": "取消收藏成功"}


@router.get("/folders")
async def get_folders(db: AsyncSession = Depends(get_db)):
    stmt = select(Favorite.folder).where(Favorite.folder.isnot(None)).distinct()
    result = await db.execute(stmt)
    folders = [r[0] for r in result.all()]
    return {"folders": folders}
