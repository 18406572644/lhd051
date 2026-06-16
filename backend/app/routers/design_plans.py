from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from typing import Optional

from app.database import get_db
from app.models import DesignPlan
from app.schemas import (
    DesignPlanCreate, DesignPlanUpdate, DesignPlanResponse,
    PaginatedResponse
)

router = APIRouter(prefix="/api/design-plans", tags=["设计方案管理"])


@router.get("", response_model=PaginatedResponse)
async def get_plans(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    style: Optional[str] = None,
    scene: Optional[str] = None,
    status: Optional[str] = None,
    keyword: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    stmt = select(DesignPlan)
    conditions = []
    if style:
        conditions.append(DesignPlan.style == style)
    if scene:
        conditions.append(DesignPlan.scene == scene)
    if status:
        conditions.append(DesignPlan.status == status)
    if keyword:
        conditions.append(or_(
            DesignPlan.name.contains(keyword),
            DesignPlan.color_theme.contains(keyword),
            DesignPlan.layout_description.contains(keyword)
        ))
    if conditions:
        stmt = stmt.where(and_(*conditions))

    count_stmt = select(func.count()).select_from(stmt.subquery())
    total = await db.scalar(count_stmt)

    stmt = stmt.order_by(DesignPlan.priority.desc(), DesignPlan.created_at.desc()).offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(stmt)
    items = result.scalars().all()
    resp_items = [DesignPlanResponse.model_validate(it) for it in items]

    return PaginatedResponse(total=total, page=page, page_size=page_size, items=resp_items)


@router.get("/options/styles")
async def get_styles():
    return {"styles": ["复古", "清新", "森系", "极简", "浪漫", "田园", "其他"]}


@router.get("/options/scenes")
async def get_scenes():
    return {"scenes": ["家居", "婚礼", "办公", "礼品", "展览", "其他"]}


@router.get("/options/statuses")
async def get_statuses():
    return {"statuses": ["草稿", "进行中", "已完成"]}


@router.get("/{item_id}", response_model=DesignPlanResponse)
async def get_plan(item_id: int, db: AsyncSession = Depends(get_db)):
    stmt = select(DesignPlan).where(DesignPlan.id == item_id)
    result = await db.execute(stmt)
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="设计方案不存在")
    return item


@router.post("", response_model=DesignPlanResponse)
async def create_plan(data: DesignPlanCreate, db: AsyncSession = Depends(get_db)):
    item = DesignPlan(**data.model_dump(exclude_none=True))
    db.add(item)
    await db.commit()
    await db.refresh(item)
    return item


@router.put("/{item_id}", response_model=DesignPlanResponse)
async def update_plan(item_id: int, data: DesignPlanUpdate, db: AsyncSession = Depends(get_db)):
    stmt = select(DesignPlan).where(DesignPlan.id == item_id)
    result = await db.execute(stmt)
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="设计方案不存在")
    update_data = data.model_dump(exclude_none=True)
    for key, value in update_data.items():
        setattr(item, key, value)
    await db.commit()
    await db.refresh(item)
    return item


@router.delete("/{item_id}")
async def delete_plan(item_id: int, db: AsyncSession = Depends(get_db)):
    stmt = select(DesignPlan).where(DesignPlan.id == item_id)
    result = await db.execute(stmt)
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="设计方案不存在")
    await db.delete(item)
    await db.commit()
    return {"message": "删除成功"}
