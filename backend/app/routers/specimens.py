from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from sqlalchemy.orm import joinedload
from typing import Optional
from datetime import date

from app.database import get_db
from app.models import Specimen, SharePost, Favorite, DryingProcess, FlowerMaterial
from app.schemas import (
    SpecimenCreate, SpecimenUpdate, SpecimenResponse,
    PaginatedResponse
)

router = APIRouter(prefix="/api/specimens", tags=["成品标本管理"])


@router.get("", response_model=PaginatedResponse)
async def get_specimens(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    category: Optional[str] = None,
    status: Optional[str] = None,
    is_featured: Optional[bool] = None,
    is_shared: Optional[bool] = None,
    frame_style: Optional[str] = None,
    keyword: Optional[str] = None,
    tag: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    stmt = select(Specimen).options(
        joinedload(Specimen.drying_process).joinedload(DryingProcess.material)
    )
    conditions = []
    if category:
        conditions.append(Specimen.category == category)
    if status:
        conditions.append(Specimen.status == status)
    if is_featured is not None:
        conditions.append(Specimen.is_featured == is_featured)
    if is_shared is not None:
        conditions.append(Specimen.is_shared == is_shared)
    if frame_style:
        conditions.append(Specimen.frame_style == frame_style)
    if keyword:
        conditions.append(or_(
            Specimen.name.contains(keyword),
            Specimen.display_code.contains(keyword),
            Specimen.description.contains(keyword)
        ))
    if tag:
        conditions.append(Specimen.tags.contains(tag))
    if conditions:
        stmt = stmt.where(and_(*conditions))

    count_stmt = select(func.count()).select_from(stmt.subquery())
    total = await db.scalar(count_stmt)

    stmt = stmt.order_by(Specimen.is_featured.desc(), Specimen.created_at.desc()).offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(stmt)
    items = result.scalars().unique().all()
    resp_items = [SpecimenResponse.model_validate(it) for it in items]

    return PaginatedResponse(total=total, page=page, page_size=page_size, items=resp_items)


@router.get("/options/categories")
async def get_categories():
    return {"categories": ["单枝", "花束", "压花", "香薰", "摆件", "礼盒", "其他"]}


@router.get("/options/statuses")
async def get_statuses():
    return {"statuses": ["完好", "微损", "已赠出", "售出"]}


@router.get("/options/frame-styles")
async def get_frame_styles():
    return {"frame_styles": ["原木", "复古金", "极简白", "黑色", "透明亚克力", "其他"]}


@router.get("/{item_id}", response_model=SpecimenResponse)
async def get_specimen(item_id: int, db: AsyncSession = Depends(get_db)):
    stmt = select(Specimen).options(joinedload(Specimen.drying_process)).where(Specimen.id == item_id)
    result = await db.execute(stmt)
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="标本不存在")
    item.view_count = (item.view_count or 0) + 1
    await db.commit()
    await db.refresh(item)
    return item


@router.post("", response_model=SpecimenResponse)
async def create_specimen(data: SpecimenCreate, db: AsyncSession = Depends(get_db)):
    item = Specimen(**data.model_dump(exclude_none=True))
    if not item.display_code:
        count_stmt = select(func.count(Specimen.id))
        count = await db.scalar(count_stmt)
        item.display_code = f"SP{date.today().strftime('%Y%m%d')}{count + 1:04d}"
    db.add(item)
    await db.commit()
    await db.refresh(item)
    stmt = select(Specimen).options(joinedload(Specimen.drying_process)).where(Specimen.id == item.id)
    result = await db.execute(stmt)
    return result.scalar_one()


@router.put("/{item_id}", response_model=SpecimenResponse)
async def update_specimen(item_id: int, data: SpecimenUpdate, db: AsyncSession = Depends(get_db)):
    stmt = select(Specimen).where(Specimen.id == item_id)
    result = await db.execute(stmt)
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="标本不存在")
    update_data = data.model_dump(exclude_none=True)
    for key, value in update_data.items():
        setattr(item, key, value)
    await db.commit()
    await db.refresh(item)
    stmt = select(Specimen).options(joinedload(Specimen.drying_process)).where(Specimen.id == item_id)
    result = await db.execute(stmt)
    return result.scalar_one()


@router.delete("/{item_id}")
async def delete_specimen(item_id: int, db: AsyncSession = Depends(get_db)):
    stmt = select(Specimen).where(Specimen.id == item_id)
    result = await db.execute(stmt)
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="标本不存在")
    await db.delete(item)
    await db.commit()
    return {"message": "删除成功"}


@router.post("/{item_id}/like")
async def like_specimen(item_id: int, db: AsyncSession = Depends(get_db)):
    stmt = select(Specimen).where(Specimen.id == item_id)
    result = await db.execute(stmt)
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="标本不存在")
    item.like_count = (item.like_count or 0) + 1
    await db.commit()
    return {"like_count": item.like_count}
