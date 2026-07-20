import logging
from datetime import UTC, datetime, timedelta

import sentry_sdk
from sqlalchemy import update

from app.core.config import settings
from app.core.errors import SAFE_ERRORS
from app.db.session import async_session
from app.models.brief import Brief
from app.schemas.api import BriefStatus

logger = logging.getLogger("app.cleanup")


class CleanupService:
    """Service to recover zombie tasks that are stuck in processing status."""

    @staticmethod
    async def fail_abandoned_briefs(timeout_minutes: int | None = None) -> None:
        """Finds briefs stuck in 'processing' status for too long and marks them as failed."""
        if timeout_minutes is None:
            timeout_minutes = settings.CLEANUP_TIMEOUT_MINUTES

        cutoff_time = datetime.now(UTC) - timedelta(minutes=timeout_minutes)

        async with async_session() as session:
            try:
                # Update abandoned briefs and get their IDs
                stmt = (
                    update(Brief)
                    .where(Brief.status == BriefStatus.PROCESSING.value)
                    .where(Brief.started_at < cutoff_time)
                    .values(
                        status=BriefStatus.FAILED.value,
                        finished_at=datetime.now(UTC),
                        error_code="TaskAbandoned",
                        error_message=SAFE_ERRORS["TaskAbandoned"],
                    )
                    .returning(Brief.id)
                )
                result = await session.execute(stmt)
                updated_ids = [row[0] for row in result.all()]

                if updated_ids:
                    await session.commit()
                    for brief_id in updated_ids:
                        msg = f"Task {brief_id} was marked as abandoned (stuck in processing)"
                        logger.warning(msg)
                        sentry_sdk.capture_message(msg, level="warning")
                else:
                    logger.debug("No abandoned tasks found.")

            except Exception as e:
                await session.rollback()
                logger.error(f"Error during cleaning up abandoned briefs: {e}", exc_info=True)
                sentry_sdk.capture_exception(e)
