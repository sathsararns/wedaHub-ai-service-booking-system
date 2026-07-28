from app.graph.workflow import travel_graph

from app.memory.conversation_memory import (
    load_state,
    save_state,
)

from app.agents.booking_agent import booking_agent


def chat(session_id: str, message: str):

    old_state = load_state(session_id)

    if old_state is None:

        state = {
            "session_id": session_id,
            "user_input": message,
        }

    else:

        state = old_state

        state["user_input"] = message

    # -----------------------------
    # Detect booking intent
    # -----------------------------

    if message.lower().startswith("book"):

        booking = booking_agent.invoke(
            {
                "input": message
            }
        )

        state["booking"] = booking.model_dump()

    print("===== STATE BEFORE GRAPH =====")
    print(state)

    result = travel_graph.invoke(state)

    save_state(session_id, result)

    return result["response"]