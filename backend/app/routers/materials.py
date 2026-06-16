from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from typing import Optional
from datetime import date

from app.database import get_db
from app.models import FlowerMaterial
from app.schemas import (
    FlowerMaterialCreate, FlowerMaterialUpdate, FlowerMaterialResponse,
    FlowerMaterialFilter, PaginatedResponse
)

router = APIRouter(prefix="/api/materials", tags=["鲜花原料管理"])


@router.get("", response_model=PaginatedResponse)
async def get_materials(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    category: Optional[str] = None,
    color: Optional[str] = None,
    is_available: Optional[bool] = None,
    fresh_level: Optional[str] = None,
    keyword: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    stmt = select(FlowerMaterial)
    conditions = []
    if category:
        conditions.append(FlowerMaterial.category == category)
    if color:
        conditions.append(FlowerMaterial.color == color)
    if is_available is not None:
        conditions.append(FlowerMaterial.is_available == is_available)
    if fresh_level:
        conditions.append(FlowerMaterial.fresh_level == fresh_level)
    if keyword:
        conditions.append(or_(
            FlowerMaterial.name.contains(keyword),
            FlowerMaterial.scientific_name.contains(keyword),
            FlowerMaterial.notes.contains(keyword)
        ))
    if conditions:
        stmt = stmt.where(and_(*conditions))

    count_stmt = select(func.count()).select_from(stmt.subquery())
    total = await db.scalar(count_stmt)

    stmt = stmt.order_by(FlowerMaterial.created_at.desc()).offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(stmt)
    items = result.scalars().all()
    resp_items = [FlowerMaterialResponse.model_validate(it) for it in items]

    return PaginatedResponse(total=total, page=page, page_size=page_size, items=resp_items)


@router.get("/options/categories")
async def get_categories(db: AsyncSession = Depends(get_db)):
    stmt = select(FlowerMaterial.category).where(
        FlowerMaterial.category.isnot(None),
        FlowerMaterial.category != ""
    ).distinct()
    result = await db.execute(stmt)
    categories = [r[0] for r in result.all() if r[0] and r[0].strip()]
    defaults = ["玫瑰", "满天星", "尤加利", "绣球", "薰衣草", "向日葵", "小雏菊", "康乃馨", "其他"]
    for c in defaults:
        if c not in categories:
            categories.append(c)
    return {"categories": categories}


@router.get("/options/colors")
async def get_colors(db: AsyncSession = Depends(get_db)):
    stmt = select(FlowerMaterial.color).where(
        FlowerMaterial.color.isnot(None),
        FlowerMaterial.color != ""
    ).distinct()
    result = await db.execute(stmt)
    colors = [r[0] for r in result.all() if r[0] and r[0].strip()]
    defaults = ["粉色", "红色", "白色", "黄色", "紫色", "蓝色", "橙色", "绿色", "香槟色", "混色"]
    for c in defaults:
        if c not in colors:
            colors.append(c)
    return {"colors": colors}


@router.get("/{item_id}", response_model=FlowerMaterialResponse)
async def get_material(item_id: int, db: AsyncSession = Depends(get_db)):
    stmt = select(FlowerMaterial).where(FlowerMaterial.id == item_id)
    result = await db.execute(stmt)
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="原料不存在")
    return item


@router.post("", response_model=FlowerMaterialResponse)
async def create_material(data: FlowerMaterialCreate, db: AsyncSession = Depends(get_db)):
    item = FlowerMaterial(**data.model_dump(exclude_none=True))
    db.add(item)
    await db.commit()
    await db.refresh(item)
    return item


@router.put("/{item_id}", response_model=FlowerMaterialResponse)
async def update_material(item_id: int, data: FlowerMaterialUpdate, db: AsyncSession = Depends(get_db)):
    stmt = select(FlowerMaterial).where(FlowerMaterial.id == item_id)
    result = await db.execute(stmt)
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="原料不存在")
    update_data = data.model_dump(exclude_none=True)
    for key, value in update_data.items():
        setattr(item, key, value)
    await db.commit()
    await db.refresh(item)
    return item


@router.delete("/{item_id}")
async def delete_material(item_id: int, db: AsyncSession = Depends(get_db)):
    stmt = select(FlowerMaterial).where(FlowerMaterial.id == item_id)
    result = await db.execute(stmt)
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="原料不存在")
    await db.delete(item)
    await db.commit()
    return {"message": "删除成功"}
