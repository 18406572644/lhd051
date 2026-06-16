from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager

from app.config import settings
from app.database import init_db
from app.routers import (
    materials, drying_processes, specimens, technique_notes,
    design_plans, product_images, share_posts, favorites,
    consumptions, statistics, uploads
)
from app.models.seed import seed_demo_data


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    await seed_demo_data()
    yield


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="干花制作与标本留存全栈系统 - 清新花艺风格的干花管理平台",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")


@app.get("/api/health")
async def health_check():
    return {
        "status": "ok",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION
    }


app.include_router(materials.router)
app.include_router(drying_processes.router)
app.include_router(specimens.router)
app.include_router(technique_notes.router)
app.include_router(design_plans.router)
app.include_router(product_images.router)
app.include_router(share_posts.router)
app.include_router(favorites.router)
app.include_router(consumptions.router)
app.include_router(statistics.router)
app.include_router(uploads.router)
