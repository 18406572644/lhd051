from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from typing import Optional

from app.database import get_db
from app.models import ProductImage
from app.schemas import (
    ProductImageCreate, ProductImageUpdate, ProductImageResponse,
    PaginatedResponse
)

router = APIRouter(prefix="/api/product-images", tags=["成品图片管理"])


@router.get("", response_model=PaginatedResponse)
async def get_images(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    specimen_id: Optional[int] = None,
    design_plan_id: Optional[int] = None,
    shot_angle: Optional[str] = None,
    is_cover: Optional[bool] = None,
    keyword: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    stmt = select(ProductImage)
    conditions = []
    if specimen_id:
        conditions.append(ProductImage.specimen_id == specimen_id)
    if design_plan_id:
        conditions.append(ProductImage.design_plan_id == design_plan_id)
    if shot_angle:
        conditions.append(ProductImage.shot_angle == shot_angle)
    if is_cover is not None:
        conditions.append(ProductImage.is_cover == is_cover)
    if keyword:
        conditions.append(or_(
            ProductImage.title.contains(keyword),
            ProductImage.description.contains(keyword)
        ))
    if conditions:
        stmt = stmt.where(and_(*conditions))

    count_stmt = select(func.count()).select_from(stmt.subquery())
    total = await db.scalar(count_stmt)

    stmt = stmt.order_by(ProductImage.sort_order.asc(), ProductImage.created_at.desc()).offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(stmt)
    items = result.scalars().all()
    resp_items = [ProductImageResponse.model_validate(it) for it in items]

    return PaginatedResponse(total=total, page=page, page_size=page_size, items=resp_items)


@router.get("/options/shot-angles")
async def get_shot_angles():
    return {"shot_angles": ["正面", "侧面", "俯视", "特写", "全景", "其他"]}


@router.get("/options/lightings")
async def get_lightings():
    return {"lightings": ["自然光", "暖光", "冷光", "柔光", "其他"]}


@router.get("/options/backgrounds")
async def get_backgrounds():
    return {"backgrounds": ["纯色", "花艺", "木质", "布艺", "大理石", "其他"]}


@router.get("/{item_id}", response_model=ProductImageResponse)
async def get_image(item_id: int, db: AsyncSession = Depends(get_db)):
    stmt = select(ProductImage).where(ProductImage.id == item_id)
    result = await db.execute(stmt)
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="图片不存在")
    return item


@router.post("", response_model=ProductImageResponse)
async def create_image(data: ProductImageCreate, db: AsyncSession = Depends(get_db)):
    item = ProductImage(**data.model_dump(exclude_none=True))
    db.add(item)
    await db.commit()
    await db.refresh(item)
    return item


@router.put("/{item_id}", response_model=ProductImageResponse)
async def update_image(item_id: int, data: ProductImageUpdate, db: AsyncSession = Depends(get_db)):
    stmt = select(ProductImage).where(ProductImage.id == item_id)
    result = await db.execute(stmt)
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="图片不存在")
    update_data = data.model_dump(exclude_none=True)
    for key, value in update_data.items():
        setattr(item, key, value)
    await db.commit()
    await db.refresh(item)
    return item


@router.delete("/{item_id}")
async def delete_image(item_id: int, db: AsyncSession = Depends(get_db)):
    stmt = select(ProductImage).where(ProductImage.id == item_id)
    result = await db.execute(stmt)
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="图片不存在")
    await db.delete(item)
    await db.commit()
    return {"message": "删除成功"}
