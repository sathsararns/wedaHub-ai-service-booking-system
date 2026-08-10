from app.memory.memory import memory
from app.graph.workflow import graph


def chat(session_id, customer_id, user_input):

    state = memory.get(session_id)

    if state is None:
        state = {}

    # Always refresh request values
    state["session_id"] = session_id
    state["customer_id"] = customer_id
    state["user_input"] = user_input

    print("\n===== STATE BEFORE GRAPH =====")
    print(state)

    result = graph.invoke(state)

    # Ensure IDs are never lost
    result["session_id"] = session_id
    result["customer_id"] = customer_id

    print("\n===== RESULT FROM GRAPH =====")
    print(result)

    memory.save(session_id, result)

    print("\n===== MEMORY AFTER SAVE =====")
    print(memory.sessions)

    return result