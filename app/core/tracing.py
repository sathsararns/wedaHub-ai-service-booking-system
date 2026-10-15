"""
Structured tracing for the LangGraph workflow.

LangSmith itself needs no code here — LangChain/LangGraph pick up
LANGCHAIN_TRACING_V2 / LANGCHAIN_API_KEY / LANGCHAIN_PROJECT straight from
the environment for every LLM call already in this codebase
(ChatGroq, ChatPromptTemplate, .with_structured_output(), etc.). See
README.md for the two env vars needed to turn it on.

That covers LLM calls. It does not cover the plain-Python graph nodes
(the planner's deterministic branches, the booking slot-filling logic,
the response formatter) — none of those are LangChain objects, so
LangSmith never sees them. trace_node() below is the fallback structured
tracing for those: a decorator that logs one line when a node starts and
one when it finishes (or raises), with the session id, elapsed time, and
the resulting planner action — enough to reconstruct which nodes a given
request passed through purely from the logs, with or without LangSmith.
"""

import functools
import logging
import time

logger = logging.getLogger("ai_service.trace")


def trace_node(node_name):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(state, *args, **kwargs):
            session_id = (state or {}).get("session_id", "unknown")
            start = time.perf_counter()

            logger.info(
                "TRACE start node=%s session=%s",
                node_name,
                session_id,
            )

            try:
                result = func(state, *args, **kwargs)
            except Exception:
                elapsed_ms = (time.perf_counter() - start) * 1000

                logger.exception(
                    "TRACE error node=%s session=%s elapsed_ms=%.1f",
                    node_name,
                    session_id,
                    elapsed_ms,
                )

                raise

            elapsed_ms = (time.perf_counter() - start) * 1000
            planner = (result or {}).get("planner") or {}

            logger.info(
                "TRACE end   node=%s session=%s elapsed_ms=%.1f next_action=%s",
                node_name,
                session_id,
                elapsed_ms,
                planner.get("next_action", "-"),
            )

            return result

        return wrapper

    return decorator
