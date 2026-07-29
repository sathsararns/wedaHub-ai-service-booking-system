from app.memory.conversation_memory import ConversationMemory
from app.graph.workflow import graph


memory = ConversationMemory()


def chat(session_id, user_input):

    state = memory.get(session_id)

    if not state:
        state = {}

    state["session_id"] = session_id
    state["user_input"] = user_input

    print("===== STATE BEFORE GRAPH =====")
    print(state)

    result = graph.invoke(state)

    memory.save(session_id, result)

    return result["response"]