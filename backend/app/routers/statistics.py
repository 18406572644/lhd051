from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, cast, String, and_
from datetime import datetime, timedelta

from app.database import get_db
from app.models import (
    FlowerMaterial, DryingProcess, Specimen, TechniqueNote,
    DesignPlan, ProductImage, SharePost, Like, MaterialConsumption, Favorite
)
from app.schemas import StatisticsResponse

router = APIRouter(prefix="/api/statistics", tags=["数据统计分析"])


@router.get("", response_model=StatisticsResponse)
async def get_statistics(db: AsyncSession = Depends(get_db)):
    total_materials = await db.scalar(select(func.count(FlowerMaterial.id))) or 0
    total_processes = await db.scalar(select(func.count(DryingProcess.id))) or 0
    total_specimens = await db.scalar(select(func.count(Specimen.id))) or 0
    total_notes = await db.scalar(select(func.count(TechniqueNote.id))) or 0
    total_plans = await db.scalar(select(func.count(DesignPlan.id))) or 0
    total_images = await db.scalar(select(func.count(ProductImage.id))) or 0
    total_posts = await db.scalar(select(func.count(SharePost.id))) or 0
    total_likes = (await db.scalar(select(func.sum(SharePost.like_count))) or 0) + \
                  (await db.scalar(select(func.sum(Specimen.like_count))) or 0)

    total_duration_stmt = select(func.sum(DryingProcess.duration_hours))
    total_duration_hours = await db.scalar(total_duration_stmt) or 0

    total_cost_stmt = select(func.sum(MaterialConsumption.total_cost))
    total_cost = await db.scalar(total_cost_stmt) or 0

    materials_by_category_stmt = select(
        FlowerMaterial.category,
        func.count(FlowerMaterial.id).label("count")
    ).where(FlowerMaterial.category.isnot(None)).group_by(FlowerMaterial.category)
    materials_by_category_result = await db.execute(materials_by_category_stmt)
    materials_by_category = [{"name": r[0], "value": r[1]} for r in materials_by_category_result.all()]

    specimens_by_category_stmt = select(
        Specimen.category,
        func.count(Specimen.id).label("count")
    ).where(Specimen.category.isnot(None)).group_by(Specimen.category)
    specimens_by_category_result = await db.execute(specimens_by_category_stmt)
    specimens_by_category = [{"name": r[0], "value": r[1]} for r in specimens_by_category_result.all()]

    methods_usage_stmt = select(
        DryingProcess.method,
        func.count(DryingProcess.id).label("count")
    ).where(DryingProcess.method.isnot(None)).group_by(DryingProcess.method)
    methods_usage_result = await db.execute(methods_usage_stmt)
    methods_usage = [{"name": r[0], "value": r[1]} for r in methods_usage_result.all()]

    now = datetime.now()
    monthly_processes = []
    for i in range(6):
        month_start = (now.replace(day=1) - timedelta(days=i*30)).replace(day=1)
        if month_start.month == 12:
            next_month = month_start.replace(year=month_start.year + 1, month=1)
        else:
            next_month = month_start.replace(month=month_start.month + 1)
        month_count_stmt = select(func.count(DryingProcess.id)).where(
            and_(
                cast(DryingProcess.created_at, String).like(f"{month_start.strftime('%Y-%m')}%")
            )
        )
        count = await db.scalar(month_count_stmt) or 0
        monthly_processes.append({
            "month": month_start.strftime("%Y-%m"),
            "count": count
        })
    monthly_processes.reverse()

    top_favorites_stmt = select(
        Favorite.favorite_type,
        func.count(Favorite.id).label("count")
    ).group_by(Favorite.favorite_type)
    top_favorites_result = await db.execute(top_favorites_stmt)
    top_favorites = [{"name": r[0], "value": r[1]} for r in top_favorites_result.all()]

    return StatisticsResponse(
        total_materials=total_materials,
        total_processes=total_processes,
        total_specimens=total_specimens,
        total_notes=total_notes,
        total_plans=total_plans,
        total_images=total_images,
        total_posts=total_posts,
        total_likes=total_likes,
        total_duration_hours=total_duration_hours,
        total_cost=total_cost,
        materials_by_category=materials_by_category,
        specimens_by_category=specimens_by_category,
        methods_usage=methods_usage,
        monthly_processes=monthly_processes,
        top_favorites=top_favorites
    )


@router.get("/trend")
async def get_trend(db: AsyncSession = Depends(get_db)):
    now = datetime.now()
    days = []
    for i in range(14, -1, -1):
        day = now - timedelta(days=i)
        day_str = day.strftime("%Y-%m-%d")

        m_count_stmt = select(func.count(FlowerMaterial.id)).where(
            cast(FlowerMaterial.created_at, String).like(f"{day_str}%")
        )
        s_count_stmt = select(func.count(Specimen.id)).where(
            cast(Specimen.created_at, String).like(f"{day_str}%")
        )

        m_count = await db.scalar(m_count_stmt) or 0
        s_count = await db.scalar(s_count_stmt) or 0

        days.append({
            "date": day_str,
            "materials": m_count,
            "specimens": s_count
        })

    return {"trend": days}
