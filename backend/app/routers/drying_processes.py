from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from sqlalchemy.orm import joinedload
from typing import Optional, Dict, Any

from app.database import get_db
from app.models import DryingProcess, FlowerMaterial
from app.schemas import (
    DryingProcessCreate, DryingProcessUpdate, DryingProcessResponse,
    PaginatedResponse
)

router = APIRouter(prefix="/api/drying-processes", tags=["脱水制作记录"])


@router.get("", response_model=PaginatedResponse)
async def get_processes(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    method: Optional[str] = None,
    status: Optional[str] = None,
    material_id: Optional[int] = None,
    color_retention: Optional[str] = None,
    keyword: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    stmt = select(DryingProcess).options(joinedload(DryingProcess.material))
    conditions = []
    if method:
        conditions.append(DryingProcess.method == method)
    if status:
        conditions.append(DryingProcess.status == status)
    if material_id:
        conditions.append(DryingProcess.material_id == material_id)
    if color_retention:
        conditions.append(DryingProcess.color_retention == color_retention)
    if keyword:
        conditions.append(or_(
            DryingProcess.process_name.contains(keyword),
            DryingProcess.pre_treatment.contains(keyword),
            DryingProcess.notes.contains(keyword)
        ))
    if conditions:
        stmt = stmt.where(and_(*conditions))

    count_stmt = select(func.count()).select_from(stmt.subquery())
    total = await db.scalar(count_stmt)

    stmt = stmt.order_by(DryingProcess.created_at.desc()).offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(stmt)
    items = result.scalars().unique().all()
    resp_items = [DryingProcessResponse.model_validate(it) for it in items]

    return PaginatedResponse(total=total, page=page, page_size=page_size, items=resp_items)


@router.get("/options/methods")
async def get_methods():
    return {"methods": ["自然风干", "倒挂", "干燥剂", "微波炉", "压花", "其他"]}


@router.get("/options/statuses")
async def get_statuses():
    return {"statuses": ["进行中", "已完成", "失败"]}


@router.get("/{item_id}", response_model=DryingProcessResponse)
async def get_process(item_id: int, db: AsyncSession = Depends(get_db)):
    stmt = select(DryingProcess).options(joinedload(DryingProcess.material)).where(DryingProcess.id == item_id)
    result = await db.execute(stmt)
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="制作记录不存在")
    return item


@router.post("", response_model=DryingProcessResponse)
async def create_process(data: DryingProcessCreate, db: AsyncSession = Depends(get_db)):
    item = DryingProcess(**data.model_dump(exclude_none=True))
    db.add(item)
    await db.commit()
    await db.refresh(item)
    stmt = select(DryingProcess).options(joinedload(DryingProcess.material)).where(DryingProcess.id == item.id)
    result = await db.execute(stmt)
    return result.scalar_one()


@router.put("/{item_id}", response_model=DryingProcessResponse)
async def update_process(item_id: int, request: Request, db: AsyncSession = Depends(get_db)):
    stmt = select(DryingProcess).where(DryingProcess.id == item_id)
    result = await db.execute(stmt)
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="制作记录不存在")
    
    raw_body: Dict[str, Any] = await request.json()
    validated = DryingProcessUpdate(**raw_body)
    
    def clean_float(v):
        if v is None: return None
        if isinstance(v, str):
            s = v.strip()
            if s == '': return None
            try: return float(s)
            except ValueError: return None
        return v
    
    def clean_int(v):
        if v is None: return None
        if isinstance(v, str):
            s = v.strip()
            if s == '': return None
            try: return int(float(s))
            except ValueError: return None
        return v
    
    def clean_str(v):
        if v is None: return None
        s = str(v).strip()
        return s if s != '' else None
    
    def clean_steps(v):
        if v is None: return None
        if isinstance(v, list):
            cleaned = [str(s).strip() for s in v if s is not None and str(s).strip() != '']
            return cleaned if cleaned else None
        return None
    
    field_cleaners = {
        'material_id': clean_int,
        'process_name': lambda v: str(v).strip() if v else None,
        'method': clean_str,
        'temperature': clean_float,
        'humidity': clean_float,
        'pressure': clean_str,
        'desiccant_weight': clean_float,
        'pre_treatment': clean_str,
        'process_steps': clean_steps,
        'status': clean_str,
        'color_retention': clean_str,
        'shape_retention': clean_str,
        'yield_rate': clean_float,
        'output_quantity': clean_float,
        'notes': clean_str,
    }
    
    for field, raw_value in raw_body.items():
        if field in field_cleaners:
            cleaned = field_cleaners[field](raw_value)
            setattr(item, field, cleaned)
    
    await db.commit()
    await db.refresh(item)
    stmt = select(DryingProcess).options(joinedload(DryingProcess.material)).where(DryingProcess.id == item_id)
    result = await db.execute(stmt)
    return result.scalar_one()


@router.delete("/{item_id}")
async def delete_process(item_id: int, db: AsyncSession = Depends(get_db)):
    stmt = select(DryingProcess).where(DryingProcess.id == item_id)
    result = await db.execute(stmt)
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="制作记录不存在")
    await db.delete(item)
    await db.commit()
    return {"message": "删除成功"}
