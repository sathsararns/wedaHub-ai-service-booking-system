from app.memory.memory import memory
from app.graph.workflow import graph


def chat(session_id, customer_id, user_input):
    # Get previous conversation state
    state = memory.get(session_id)

    if not state:
        state = {}

    # Update current request
    state["session_id"] = session_id
    state["customer_id"] = customer_id
    state["user_input"] = user_input

    print("===== STATE BEFORE GRAPH =====")
    print(state)

    # Run LangGraph workflow
    result = graph.invoke(state)

    print("===== RESULT FROM GRAPH =====")
    print(result)

    # Save updated state
    memory.save(session_id, result)

    print("===== MEMORY AFTER SAVE =====")
    print(memory.sessions)

    return result