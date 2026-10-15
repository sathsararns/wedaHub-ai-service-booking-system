import logging
from collections import defaultdict
from copy import deepcopy

logger = logging.getLogger(__name__)


class ConversationMemory:
    def __init__(self):
        self.sessions = defaultdict(dict)

    def get(self, session_id):
        logger.debug(
            "memory get session=%s (active_sessions=%d)",
            session_id,
            len(self.sessions),
        )
        return deepcopy(self.sessions.get(session_id, {}))

    def save(self, session_id, state):
        logger.debug("memory save session=%s", session_id)
        self.sessions[session_id] = deepcopy(state or {})

    def clear(self, session_id):
        logger.info("memory clear session=%s", session_id)
        self.sessions.pop(session_id, None)
