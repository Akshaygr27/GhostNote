from contextlib import asynccontextmanager
from time import perf_counter
from app.routers import auth
from app.routers import messages
from pymongo.errors import ConnectionFailure
from fastapi.exceptions import RequestValidationError

from fastapi import FastAPI, Request

from app.core.exceptions import MessageNotFoundException

from app.core.exception_handlers import (
    database_exception_handler,
    validation_exception_handler,
    message_not_found_handler,
    unexpected_exception_handler
)

from app.core.config import settings
from app.core.database import (
    connect_to_mongodb,
    close_mongodb
)
from app.core.logging_config import setup_logging, logger

from app.routers import health


# Configure logging
setup_logging(settings.LOG_LEVEL)


# Application lifecycle
@asynccontextmanager
async def lifespan(app: FastAPI):

    logger.info("Starting application")

    # Connect MongoDB during startup
    await connect_to_mongodb()

    yield

    # Close MongoDB during shutdown
    await close_mongodb()

    logger.info("Application stopped")


# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    debug=settings.DEBUG,
    lifespan=lifespan
)

# Centralized exception handlers

app.add_exception_handler(
    ConnectionFailure,
    database_exception_handler
)

app.add_exception_handler(
    RequestValidationError,
    validation_exception_handler
)

app.add_exception_handler(
    MessageNotFoundException,
    message_not_found_handler
)

app.add_exception_handler(
    Exception,
    unexpected_exception_handler
)

# Register routers
app.include_router(health.router)
app.include_router(auth.router)
app.include_router(messages.router)

# Request logging middleware
@app.middleware("http")
async def request_logging(request: Request, call_next):

    start_time = perf_counter()

    try:

        response = await call_next(request)

        duration = (perf_counter() - start_time) * 1000

        if response.status_code >= 400:
            logger.warning(
                "%s %s | Status: %s | %.2f ms",
                request.method,
                request.url.path,
                response.status_code,
                duration
            )
        else:
            logger.info(
                "%s %s | Status: %s | %.2f ms",
                request.method,
                request.url.path,
                response.status_code,
                duration
            )

        return response

    except Exception:

        logger.exception(
            "Request failed: %s %s",
            request.method,
            request.url.path
        )

        raise


@app.get("/")
async def root():

    return {
        "message": "Welcome to FastAPI Backend"
    }