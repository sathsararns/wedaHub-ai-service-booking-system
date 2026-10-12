import logging
from copy import deepcopy

from app.memory.store import memory
from app.graph.workflow import graph

logger = logging.getLogger(__name__)


def clear_chat_session(session_id):
    memory.clear(session_id)


def chat(session_id=None, customer_id=None, user_input=None, message=None):
    text = user_input if user_input is not None else message
    text = (text or "").strip()

    if not session_id:
        session_id = customer_id or "guest"

    previous_state = memory.get(session_id) or {}
    state = deepcopy(previous_state)

    state["session_id"] = session_id
    state["customer_id"] = customer_id
    state["user_input"] = text

    state.setdefault("requirements", previous_state.get("requirements") or {})
    state.setdefault("booking", previous_state.get("booking") or {})
    state.setdefault("providers", previous_state.get("providers") or [])
    state.setdefault("recommendations", previous_state.get("recommendations") or {})
    state.setdefault("recommended_providers", previous_state.get("recommended_providers") or [])
    state.setdefault("booking_result", previous_state.get("booking_result"))
    state.setdefault("booking_error", previous_state.get("booking_error"))

    logger.info("session=%s chat start | input=%r", session_id, text)
    logger.debug("session=%s state_before_graph=%s", session_id, state)

    result = graph.invoke(state)

    logger.debug("session=%s result_from_graph=%s", session_id, result)

    memory.save(session_id, result)

    logger.info("session=%s chat done", session_id)

    return result
