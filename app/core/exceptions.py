import logging
from collections.abc import Awaitable, Callable
from typing import Any

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse, Response
from sqlalchemy.exc import IntegrityError


ExceptionHandler = Callable[[Request, Exception], Awaitable[Response]]
logger = logging.getLogger(__name__)


class BooklyException(Exception):
    """This is the base class for all bookly errors"""

    pass


# Book related errors
class BookNotFoundError(BooklyException):
    pass


class BookPermissionError(BooklyException):
    pass


# Review related errors
class ReviewNotFoundError(BooklyException):
    pass


# User and Authentication related errors
class UserNotFoundError(BooklyException):
    pass


class UserEmailAlreadyExistsError(BooklyException):
    pass


# Tag related errors
class TagNotFoundError(BooklyException):
    pass


class TagAlreadyExistsError(BooklyException):
    pass


# Exception handler

def create_static_exception_handler(
    status_code: int, detail: dict[str, Any],
) -> ExceptionHandler:
    async def exception_handler(
        _request: Request,
        _exc: Exception,
    ) -> JSONResponse:
        return JSONResponse(
            status_code=status_code,
            content=detail,
        )

    return exception_handler


# Infrastructure errors
async def integrity_error_handler(
    _request: Request,
    _exc: IntegrityError,
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content={
            "detail": "The operation conflicts with existing data.",
        },
    )


async def unexpected_exception_handler(
    _request: Request,
    exc: Exception,
) -> JSONResponse:
    logger.exception("Unhandled exception", exc_info=exc)

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "An unexpected error occurred."},
    )


# Register all errors with the FastAPI app
def register_books_errors(app: FastAPI) -> None:
    app.add_exception_handler(
        BookNotFoundError,
        create_static_exception_handler(
            status.HTTP_404_NOT_FOUND,
            {"detail": "Book not found"},
        ),
    )
    app.add_exception_handler(
        BookPermissionError,
        create_static_exception_handler(
            status.HTTP_403_FORBIDDEN,
            {"detail": "You do not have permission to access this book"},
        ),
    )


def register_reviews_errors(app: FastAPI) -> None:
    app.add_exception_handler(
        ReviewNotFoundError,
        create_static_exception_handler(
            status.HTTP_404_NOT_FOUND,
            {"detail": "Review not found"},
        ),
    )


def register_users_errors(app: FastAPI) -> None:
    app.add_exception_handler(
        UserNotFoundError,
        create_static_exception_handler(
            status.HTTP_404_NOT_FOUND,
            {"detail": "User not found"},
        ),
    )
    app.add_exception_handler(
        UserEmailAlreadyExistsError,
        create_static_exception_handler(
            status.HTTP_409_CONFLICT,
            {"detail": "User with this email already exists"},
        ),
    )


def register_tags_errors(app: FastAPI) -> None:
    app.add_exception_handler(
        TagNotFoundError,
        create_static_exception_handler(
            status.HTTP_404_NOT_FOUND,
            {"detail": "Tag not found"},
        ),
    )
    app.add_exception_handler(
        TagAlreadyExistsError,
        create_static_exception_handler(
            status.HTTP_409_CONFLICT,
            {"detail": "Tag already exists"},
        ),
    )


# Register external errors
def register_infrastructure_errors(app: FastAPI) -> None:
    app.add_exception_handler(
        IntegrityError,
        integrity_error_handler,
    )


def register_generic_errors(app: FastAPI) -> None:
    app.add_exception_handler(
        Exception,
        unexpected_exception_handler,
    )


def register_all_errors(app: FastAPI) -> None:
    register_books_errors(app)
    register_reviews_errors(app)
    register_users_errors(app)
    register_tags_errors(app)

    # Register infrastructure and generic errors
    register_infrastructure_errors(app)
    register_generic_errors(app)
