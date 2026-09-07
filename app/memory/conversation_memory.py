from collections import defaultdict
from copy import deepcopy


class ConversationMemory:
    def __init__(self):
        self.sessions = defaultdict(dict)

    def get(self, session_id):
        print("MEMORY GET:", self.sessions)
        return deepcopy(self.sessions.get(session_id, {}))

    def save(self, session_id, state):
        print("MEMORY SAVE:", session_id)
        self.sessions[session_id] = deepcopy(state or {})

    def clear(self, session_id):
        self.sessions.pop(session_id, None)