from fastapi import APIRouter
from sqlalchemy import text

from app.db.session import AsyncSessionLocal
from app.services.cache import get_redis

router = APIRouter(tags=["health"])


@router.get("/health")
async def health() -> dict:
    return {"status": "ok", "service": "api-gateway"}


@router.get("/ready")
async def ready() -> dict:
    async with AsyncSessionLocal() as db:
        await db.execute(text("select 1"))
    redis = get_redis()
    try:
        await redis.ping()
    finally:
        await redis.aclose()
    return {"status": "ready", "dependencies": ["postgres", "redis"]}
