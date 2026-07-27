conversation_memory = {}


def load_state(session_id: str):

    return conversation_memory.get(session_id)


def save_state(session_id: str, state):

    conversation_memory[session_id] = state