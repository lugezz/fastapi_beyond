
from fastapi import FastAPI

from app.api.router import api_router
from app.core.config import settings

app = FastAPI()
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
