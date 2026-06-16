from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from typing import Optional

from app.database import get_db
from app.models import TechniqueNote
from app.schemas import (
    TechniqueNoteCreate, TechniqueNoteUpdate, TechniqueNoteResponse,
    PaginatedResponse
)

router = APIRouter(prefix="/api/technique-notes", tags=["制作手法笔记"])


@router.get("", response_model=PaginatedResponse)
async def get_notes(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    category: Optional[str] = None,
    difficulty: Optional[str] = None,
    is_favorite: Optional[bool] = None,
    keyword: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    stmt = select(TechniqueNote)
    conditions = []
    if category:
        conditions.append(TechniqueNote.category == category)
    if difficulty:
        conditions.append(TechniqueNote.difficulty == difficulty)
    if is_favorite is not None:
        conditions.append(TechniqueNote.is_favorite == is_favorite)
    if keyword:
        conditions.append(or_(
            TechniqueNote.title.contains(keyword),
            TechniqueNote.content.contains(keyword)
        ))
    if conditions:
        stmt = stmt.where(and_(*conditions))

    count_stmt = select(func.count()).select_from(stmt.subquery())
    total = await db.scalar(count_stmt)

    stmt = stmt.order_by(TechniqueNote.created_at.desc()).offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(stmt)
    items = result.scalars().all()
    resp_items = [TechniqueNoteResponse.model_validate(it) for it in items]

    return PaginatedResponse(total=total, page=page, page_size=page_size, items=resp_items)


@router.get("/options/categories")
async def get_categories():
    return {"categories": ["采花", "预处理", "风干", "保色", "装裱", "搭配", "其他"]}


@router.get("/options/difficulties")
async def get_difficulties():
    return {"difficulties": ["入门", "进阶", "精通"]}


@router.get("/{item_id}", response_model=TechniqueNoteResponse)
async def get_note(item_id: int, db: AsyncSession = Depends(get_db)):
    stmt = select(TechniqueNote).where(TechniqueNote.id == item_id)
    result = await db.execute(stmt)
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="笔记不存在")
    return item


@router.post("", response_model=TechniqueNoteResponse)
async def create_note(data: TechniqueNoteCreate, db: AsyncSession = Depends(get_db)):
    item = TechniqueNote(**data.model_dump(exclude_none=True))
    db.add(item)
    await db.commit()
    await db.refresh(item)
    return item


@router.put("/{item_id}", response_model=TechniqueNoteResponse)
async def update_note(item_id: int, data: TechniqueNoteUpdate, db: AsyncSession = Depends(get_db)):
    stmt = select(TechniqueNote).where(TechniqueNote.id == item_id)
    result = await db.execute(stmt)
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="笔记不存在")
    update_data = data.model_dump(exclude_none=True)
    for key, value in update_data.items():
        setattr(item, key, value)
    await db.commit()
    await db.refresh(item)
    return item


@router.delete("/{item_id}")
async def delete_note(item_id: int, db: AsyncSession = Depends(get_db)):
    stmt = select(TechniqueNote).where(TechniqueNote.id == item_id)
    result = await db.execute(stmt)
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="笔记不存在")
    await db.delete(item)
    await db.commit()
    return {"message": "删除成功"}
