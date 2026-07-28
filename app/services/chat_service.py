from app.graph.workflow import travel_graph

from app.memory.conversation_memory import (
    load_state,
    save_state,
)


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

    # Booking agent එක මෙතන call කරන්න එපා.
    # booking_agent_node එක graph එක ඇතුළේ automatically run වෙනවා.

    print("===== STATE BEFORE GRAPH =====")
    print(state)

    result = travel_graph.invoke(state)

    save_state(session_id, result)

    return result["response"]