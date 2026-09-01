import logging
import time

from fastapi import FastAPI
from fastapi.requests import Request
from fastapi.responses import Response


logger = logging.getLogger(__name__)


def register_middleware(app: FastAPI) -> None:
    """Register middleware for the FastAPI application."""
    from fastapi.middleware.cors import CORSMiddleware

    from app.core.config import settings

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.middleware("http")
    async def custom_logging_middleware(
        request: Request,
        call_next: callable[[Request], Response]
    ) -> Response:
        # Log the request details
        logger.info(f"Request: {request.method} {request.url}")
        start_time = time.time()

        response = await call_next(request)

        # Log the response details
        process_time = time.time() - start_time
        logger.info(f"Response: {response.status_code} - Process time: {process_time:.4f} seconds")

        return response
