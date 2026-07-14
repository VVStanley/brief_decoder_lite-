import logging
import sys


def setup_logging() -> None:
    """Configure structured logging for the backend application."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] [%(name)s] %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)],
        force=True,  # Overrides any existing default handler configurations
    )

    # Set appropriate logging levels for external libraries to prevent spam
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    logging.getLogger("dynaconf").setLevel(logging.WARNING)
    logging.getLogger("pydantic_ai").setLevel(logging.INFO)
