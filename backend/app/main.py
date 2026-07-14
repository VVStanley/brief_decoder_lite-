import asyncio
import logging
from contextlib import asynccontextmanager

import sentry_sdk
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import api_router
from app.core.config import settings
from app.core.logging_config import setup_logging
from app.services.cleanup_service import CleanupService

logger = logging.getLogger("app.main")


async def periodic_cleanup_worker() -> None:
    """Background worker that periodically marks timed out processing tasks as failed."""
    logger.info("Starting periodic cleanup worker...")
    while True:
        try:
            await CleanupService.fail_abandoned_briefs()
        except Exception as e:
            logger.error(f"Error in cleanup worker loop: {e}", exc_info=True)
        try:
            await asyncio.sleep(60)
        except asyncio.CancelledError:
            break


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Start the periodic background task
    cleanup_task = asyncio.create_task(periodic_cleanup_worker())
    yield
    # Cancel the task on shutdown
    cleanup_task.cancel()
    try:
        await cleanup_task
    except asyncio.CancelledError:
        logger.info("Cleanup worker stopped successfully.")


def create_app() -> FastAPI:
    setup_logging()

    if settings.SENTRY_DSN:
        sentry_sdk.init(
            dsn=settings.SENTRY_DSN,
            traces_sample_rate=settings.SENTRY_TRACES_SAMPLE_RATE,
        )

    app = FastAPI(
        title="AI Brief Decoder Lite",
        description="FastAPI service for decoding and analyzing client briefs",
        version="0.1.0",
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan,
    )

    # CORS configuration
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # For extension development
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include centralized router
    app.include_router(api_router)

    return app


app = create_app()
