
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.router import api_router
from app.core.config import settings
from app.core.exceptions import register_all_errors
from app.core.middleware import register_middleware


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup code
    yield
    # Shutdown code


app = FastAPI(
    title=settings.api_title,
    version=settings.api_version,
    description=settings.api_description,
    lifespan=lifespan
)
register_all_errors(app)
register_middleware(app)
app.include_router(api_router)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
        access_log=False,
    )
