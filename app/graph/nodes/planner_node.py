import logging

from app.agents.planner_agent import planner_agent
from app.core.tracing import trace_node

logger = logging.getLogger(__name__)


@trace_node("planner_node")
def planner_node(state):
    """
    Planner Node

    Responsible only for deciding
    the next workflow.
    """

    session_id = state.get("session_id")

    # =====================================================
    # Clear stale planner state
    # =====================================================

    state.pop("planner_error", None)
    state["booking_error"] = None
    state["booking_status"] = None
    state["booking_created"] = False
    state["booking_card"] = None
    state["created_booking"] = None

    # =====================================================
    # Execute planner
    # =====================================================

    try:
        result = planner_agent(state)

    except Exception as e:

        logger.exception("session=%s planner_agent raised", session_id)

        state["planner_error"] = str(e)

        state["planner"] = {
            "next_action": "response",
            "missing_fields": [],
            "message": "",
        }

        return state

    logger.debug("session=%s planner_result=%s", session_id, result)

    # =====================================================
    # No result
    # =====================================================

    if result is None:

        state["planner_error"] = "Planner returned no result."

        state["planner"] = {
            "next_action": "response",
            "missing_fields": [],
            "message": "",
        }

        return state

    # =====================================================
    # Convert to dict
    # =====================================================

    if hasattr(result, "model_dump"):
        planner = result.model_dump()

    elif hasattr(result, "dict"):
        planner = result.dict()

    elif isinstance(result, dict):
        planner = result

    else:

        planner = {
            "next_action": "response",
            "missing_fields": [],
            "message": "",
        }

    # =====================================================
    # Normalize planner
    # =====================================================

    planner.setdefault("next_action", "response")
    planner.setdefault("missing_fields", [])
    planner.setdefault("message", "")

    valid_actions = {
        "general_chat",
        "search_services",
        "book_provider",
        "await_confirmation",
        "confirm_booking",
        "create_booking",
        "booking_status",
        "ask_login",
        "ask_more_information",
        "response",
        "stop",
    }

    if planner["next_action"] not in valid_actions:

        logger.warning(
            "session=%s unknown planner action=%s, defaulting to response",
            session_id,
            planner["next_action"],
        )

        planner["next_action"] = "response"

    # =====================================================
    # Save planner
    # =====================================================

    state["planner"] = planner

    logger.info("session=%s next_action=%s", session_id, planner["next_action"])

    return state
