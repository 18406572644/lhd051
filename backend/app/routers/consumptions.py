from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from typing import Optional

from app.database import get_db
from app.models import MaterialConsumption
from app.schemas import (
    MaterialConsumptionCreate, MaterialConsumptionUpdate, MaterialConsumptionResponse,
    PaginatedResponse
)

router = APIRouter(prefix="/api/consumptions", tags=["耗材统计管理"])


@router.get("", response_model=PaginatedResponse)
async def get_consumptions(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    category: Optional[str] = None,
    material_id: Optional[int] = None,
    drying_process_id: Optional[int] = None,
    keyword: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    stmt = select(MaterialConsumption)
    conditions = []
    if category:
        conditions.append(MaterialConsumption.category == category)
    if material_id:
        conditions.append(MaterialConsumption.material_id == material_id)
    if drying_process_id:
        conditions.append(MaterialConsumption.drying_process_id == drying_process_id)
    if keyword:
        conditions.append(MaterialConsumption.item_name.contains(keyword))
    if conditions:
        stmt = stmt.where(and_(*conditions))

    count_stmt = select(func.count()).select_from(stmt.subquery())
    total = await db.scalar(count_stmt)

    stmt = stmt.order_by(MaterialConsumption.created_at.desc()).offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(stmt)
    items = result.scalars().all()
    resp_items = [MaterialConsumptionResponse.model_validate(it) for it in items]

    return PaginatedResponse(total=total, page=page, page_size=page_size, items=resp_items)


@router.get("/options/categories")
async def get_categories():
    return {"categories": ["花材", "干燥剂", "容器", "工具", "辅料", "其他"]}


@router.get("/summary")
async def get_consumption_summary(db: AsyncSession = Depends(get_db)):
    total_cost_stmt = select(func.sum(MaterialConsumption.total_cost))
    total_cost = await db.scalar(total_cost_stmt) or 0

    by_category_stmt = select(
        MaterialConsumption.category,
        func.sum(MaterialConsumption.total_cost).label("cost")
    ).group_by(MaterialConsumption.category)
    by_category_result = await db.execute(by_category_stmt)
    by_category = [{"category": r[0], "cost": r[1] or 0} for r in by_category_result.all()]

    return {
        "total_cost": total_cost,
        "by_category": by_category
    }


@router.get("/{item_id}", response_model=MaterialConsumptionResponse)
async def get_consumption(item_id: int, db: AsyncSession = Depends(get_db)):
    stmt = select(MaterialConsumption).where(MaterialConsumption.id == item_id)
    result = await db.execute(stmt)
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="耗材记录不存在")
    return item


@router.post("", response_model=MaterialConsumptionResponse)
async def create_consumption(data: MaterialConsumptionCreate, db: AsyncSession = Depends(get_db)):
    item_data = data.model_dump(exclude_none=True)
    if "quantity" in item_data and "unit_price" in item_data:
        item_data["total_cost"] = item_data["quantity"] * item_data["unit_price"]
    item = MaterialConsumption(**item_data)
    db.add(item)
    await db.commit()
    await db.refresh(item)
    return item


@router.put("/{item_id}", response_model=MaterialConsumptionResponse)
async def update_consumption(item_id: int, data: MaterialConsumptionUpdate, db: AsyncSession = Depends(get_db)):
    stmt = select(MaterialConsumption).where(MaterialConsumption.id == item_id)
    result = await db.execute(stmt)
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="耗材记录不存在")
    update_data = data.model_dump(exclude_none=True)
    for key, value in update_data.items():
        setattr(item, key, value)
    if item.quantity and item.unit_price:
        item.total_cost = item.quantity * item.unit_price
    await db.commit()
    await db.refresh(item)
    return item


@router.delete("/{item_id}")
async def delete_consumption(item_id: int, db: AsyncSession = Depends(get_db)):
    stmt = select(MaterialConsumption).where(MaterialConsumption.id == item_id)
    result = await db.execute(stmt)
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="耗材记录不存在")
    await db.delete(item)
    await db.commit()
    return {"message": "删除成功"}
