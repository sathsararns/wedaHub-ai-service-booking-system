from typing import Dict


memory = {}


def save_state(session_id: str, state: Dict):

    memory[session_id] = state


def load_state(session_id: str):

    return memory.get(session_id)


def clear_state(session_id: str):

    memory.pop(session_id, None)