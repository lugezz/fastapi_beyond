from fastapi import APIRouter

from app.api.v1.endpoints.books import router as books_router
from app.api.v1.endpoints.others import router as others_router
from app.core.config import settings

router = APIRouter(prefix=settings.api_v1_prefix)
router.include_router(books_router)
router.include_router(others_router)
