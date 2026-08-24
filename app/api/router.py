from fastapi import APIRouter

from app.api.v1.router import router as v1_router
from app.core.config import settings

api_router = APIRouter(prefix=settings.api_prefix)
api_router.include_router(v1_router)
