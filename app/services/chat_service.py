from app.memory.memory import memory
from app.graph.workflow import graph


def chat(session_id, customer_id, user_input):

    state = memory.get(session_id)

    if state is None:
        state = {}

    state["session_id"] = session_id
    state["customer_id"] = customer_id
    state["user_input"] = user_input

    print("\n========== BEFORE ==========")
    print(state)

    result = graph.invoke(state)

    result["session_id"] = session_id
    result["customer_id"] = customer_id

    print("\n========== AFTER ==========")
    print(result)

    memory.save(session_id, result)

    print("\n========== MEMORY ==========")
    print(memory.sessions)

    return result