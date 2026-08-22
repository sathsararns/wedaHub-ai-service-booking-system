from traceback import print_exc

from app.agents.planner_agent import planner_agent


def planner_node(state):
    """
    Planner Node

    Responsible only for deciding
    the next workflow.
    """

    print("\n========== PLANNER NODE ==========")
    print(state)

    # =====================================================
    # Clear stale planner state
    # =====================================================

    state.pop("planner_error", None)
    state.pop("booking_error", None)
    state.pop("booking_result", None)
    state.pop("booking_status", None)

    # =====================================================
    # Execute planner
    # =====================================================

    try:
        result = planner_agent(state)

    except Exception as e:

        print_exc()

        state["planner_error"] = str(e)

        state["planner"] = {
            "next_action": "response",
            "missing_fields": [],
            "message": "",
        }

        return state

    print("\n========== PLANNER RESULT ==========")
    print(result)

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

        print(
            "Unknown planner action:",
            planner["next_action"],
        )

        planner["next_action"] = "response"

    # =====================================================
    # Save planner
    # =====================================================

    state["planner"] = planner

    print("\n========== SAVED PLANNER ==========")
    print(planner)

    return state