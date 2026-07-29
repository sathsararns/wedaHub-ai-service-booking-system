from collections import defaultdict


class ConversationMemory:

    def __init__(self):
        self.sessions = defaultdict(dict)

    def get(self, session_id: str):

        return self.sessions.get(session_id, {})

    def save(self, session_id: str, state: dict):

        self.sessions[session_id] = state

    def clear(self, session_id: str):

        if session_id in self.sessions:
            del self.sessions[session_id]