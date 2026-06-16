from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from sqlalchemy.orm import joinedload
from typing import Optional

from app.database import get_db
from app.models import SharePost, Like, Specimen
from app.schemas import (
    SharePostCreate, SharePostUpdate, SharePostResponse,
    LikeCreate, PaginatedResponse
)

router = APIRouter(prefix="/api/share-posts", tags=["作品分享与点赞"])


@router.get("", response_model=PaginatedResponse)
async def get_posts(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    is_published: Optional[bool] = None,
    keyword: Optional[str] = None,
    tag: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    stmt = select(SharePost).options(
        joinedload(SharePost.specimen).joinedload(Specimen.drying_process)
    )
    conditions = []
    if is_published is not None:
        conditions.append(SharePost.is_published == is_published)
    if keyword:
        conditions.append(or_(
            SharePost.title.contains(keyword),
            SharePost.content.contains(keyword),
            SharePost.author.contains(keyword)
        ))
    if conditions:
        stmt = stmt.where(and_(*conditions))

    count_stmt = select(func.count()).select_from(stmt.subquery())
    total = await db.scalar(count_stmt)

    stmt = stmt.order_by(SharePost.like_count.desc(), SharePost.published_at.desc()).offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(stmt)
    items = result.scalars().unique().all()
    resp_items = [SharePostResponse.model_validate(it) for it in items]

    return PaginatedResponse(total=total, page=page, page_size=page_size, items=resp_items)


@router.get("/{item_id}", response_model=SharePostResponse)
async def get_post(item_id: int, db: AsyncSession = Depends(get_db)):
    stmt = select(SharePost).options(
        joinedload(SharePost.specimen).joinedload(Specimen.drying_process)
    ).where(SharePost.id == item_id)
    result = await db.execute(stmt)
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="分享帖子不存在")
    item.view_count = (item.view_count or 0) + 1
    await db.commit()
    await db.refresh(item)
    return item


@router.post("", response_model=SharePostResponse)
async def create_post(data: SharePostCreate, db: AsyncSession = Depends(get_db)):
    item = SharePost(**data.model_dump(exclude_none=True))
    db.add(item)
    await db.commit()
    await db.refresh(item)

    if item.specimen_id:
        stmt = select(Specimen).where(Specimen.id == item.specimen_id)
        result = await db.execute(stmt)
        specimen = result.scalar_one_or_none()
        if specimen:
            specimen.is_shared = True
            await db.commit()

    stmt = select(SharePost).options(
        joinedload(SharePost.specimen).joinedload(Specimen.drying_process)
    ).where(SharePost.id == item.id)
    result = await db.execute(stmt)
    return result.scalar_one()


@router.put("/{item_id}", response_model=SharePostResponse)
async def update_post(item_id: int, data: SharePostUpdate, db: AsyncSession = Depends(get_db)):
    stmt = select(SharePost).where(SharePost.id == item_id)
    result = await db.execute(stmt)
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="分享帖子不存在")
    update_data = data.model_dump(exclude_none=True)
    for key, value in update_data.items():
        setattr(item, key, value)
    await db.commit()
    await db.refresh(item)
    stmt = select(SharePost).options(
        joinedload(SharePost.specimen).joinedload(Specimen.drying_process)
    ).where(SharePost.id == item_id)
    result = await db.execute(stmt)
    return result.scalar_one()


@router.delete("/{item_id}")
async def delete_post(item_id: int, db: AsyncSession = Depends(get_db)):
    stmt = select(SharePost).where(SharePost.id == item_id)
    result = await db.execute(stmt)
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="分享帖子不存在")
    await db.delete(item)
    await db.commit()
    return {"message": "删除成功"}


@router.post("/{item_id}/like")
async def like_post(item_id: int, data: LikeCreate, db: AsyncSession = Depends(get_db)):
    stmt = select(SharePost).where(SharePost.id == item_id)
    result = await db.execute(stmt)
    post = result.scalar_one_or_none()
    if not post:
        raise HTTPException(status_code=404, detail="分享帖子不存在")

    check_stmt = select(Like).where(
        and_(Like.post_id == item_id, Like.user_identifier == data.user_identifier)
    )
    check_result = await db.execute(check_stmt)
    existing_like = check_result.scalar_one_or_none()

    if existing_like:
        await db.delete(existing_like)
        post.like_count = max(0, (post.like_count or 0) - 1)
        await db.commit()
        return {"liked": False, "like_count": post.like_count}

    like = Like(post_id=item_id, user_identifier=data.user_identifier)
    db.add(like)
    post.like_count = (post.like_count or 0) + 1
    await db.commit()
    return {"liked": True, "like_count": post.like_count}


@router.post("/{item_id}/share")
async def share_post(item_id: int, db: AsyncSession = Depends(get_db)):
    stmt = select(SharePost).where(SharePost.id == item_id)
    result = await db.execute(stmt)
    post = result.scalar_one_or_none()
    if not post:
        raise HTTPException(status_code=404, detail="分享帖子不存在")
    post.share_count = (post.share_count or 0) + 1
    await db.commit()
    return {"share_count": post.share_count}
