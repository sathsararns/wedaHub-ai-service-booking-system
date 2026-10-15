"""
Central logging setup for the AI service.

Call configure_logging() once, as early as possible (main.py does this at
import time). Every other module just does:

    import logging
    logger = logging.getLogger(__name__)

and logs at the appropriate level — no module should call print() for
anything meant to be inspected later.

Level guide used across this service:
    DEBUG    - full state/payload dumps, only useful when actively debugging
    INFO     - one line per meaningful step (node entered, request sent,
               decision made) - what you'd want visible by default
    WARNING  - something unexpected but recoverable (unknown planner
               action, empty result, etc.)
    ERROR    - a request-level failure that produced a user-facing error
    EXCEPTION - use inside an except block; logs the level of ERROR plus
               the full traceback automatically
"""

import logging
import os

_CONFIGURED = False


def configure_logging():
    global _CONFIGURED

    if _CONFIGURED:
        return

    level_name = os.getenv("LOG_LEVEL", "INFO").upper()
    level = getattr(logging, level_name, logging.INFO)

    logging.basicConfig(
        level=level,
        format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%H:%M:%S",
    )

    # Third-party libraries are noisy at INFO/DEBUG; keep them at WARNING
    # unless the whole service is explicitly set to DEBUG.
    if level > logging.DEBUG:
        for noisy in ("httpx", "httpcore", "urllib3"):
            logging.getLogger(noisy).setLevel(logging.WARNING)

    _CONFIGURED = True

    logger = logging.getLogger(__name__)
    logger.info("Logging configured (level=%s)", level_name)

    # LangSmith activates purely from these two env vars — LangChain reads
    # them directly, no code wiring needed. This just makes it visible
    # whether tracing is actually on for this run.
    tracing_enabled = os.getenv("LANGCHAIN_TRACING_V2", "false").lower() == "true"

    if tracing_enabled:
        logger.info(
            "LangSmith tracing ENABLED (project=%s)",
            os.getenv("LANGCHAIN_PROJECT", "default"),
        )
    else:
        logger.info(
            "LangSmith tracing disabled - set LANGCHAIN_TRACING_V2=true and "
            "LANGCHAIN_API_KEY to enable it (see README)."
        )
