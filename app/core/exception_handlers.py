from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from pymongo.errors import ConnectionFailure

from app.core.exceptions import MessageNotFoundException
from app.core.logging_config import logger


# 1. DATABASE CONNECTION ERROR

async def database_exception_handler(
    request: Request,
    exc: ConnectionFailure
):

    logger.error(
        "MongoDB connection failure: %s %s",
        request.method,
        request.url.path,
        exc_info=(type(exc), exc, exc.__traceback__)
    )

    return JSONResponse(
        status_code=503,
        content={
            "success": False,
            "error_code": "DATABASE_UNAVAILABLE",
            "message": "Database is temporarily unavailable"
        },
        headers={"Retry-After": "5"}
    )


# 2. VALIDATION ERROR

async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError
):

    logger.warning(
        "Validation failed: %s %s",
        request.method,
        request.url.path
    )

    # Avoid returning submitted input values,
    # which might contain passwords or sensitive data.

    errors = [
        {
            "field": ".".join(
                str(part) for part in error["loc"]
            ),
            "message": error["msg"],
            "type": error["type"]
        }
        for error in exc.errors()
    ]

    return JSONResponse(
        status_code=422,
        content={
            "success": False,
            "error_code": "VALIDATION_ERROR",
            "message": "Request validation failed",
            "errors": errors
        }
    )


# 3. CUSTOM BUSINESS ERROR

async def message_not_found_handler(
    request: Request,
    exc: MessageNotFoundException
):

    logger.warning(
        "Requested message was not found"
    )

    return JSONResponse(
        status_code=404,
        content={
            "success": False,
            "error_code": "MESSAGE_NOT_FOUND",
            "message": "Message not found"
        }
    )


# 4. UNEXPECTED ERROR

async def unexpected_exception_handler(
    request: Request,
    exc: Exception
):

    logger.error(
        "Unexpected application error: %s %s",
        request.method,
        request.url.path,
        exc_info=(type(exc), exc, exc.__traceback__)
    )

    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error_code": "INTERNAL_SERVER_ERROR",
            "message": "An unexpected error occurred"
        }
    )