import unittest

from app.agents.planner_agent import planner_agent
from app.graph.nodes.requirement_node import merge_requirements
from app.memory.conversation_memory import ConversationMemory
from evals.dataset import PLANNER_CASES


class ConversationTests(unittest.TestCase):
    def test_memory_isolates_sessions_and_returns_copies(self):
        memory = ConversationMemory()
        state = {"booking": {"date": "Tomorrow"}}
        memory.save("one", state)
        state["booking"]["date"] = "Friday"
        loaded = memory.get("one")
        loaded["booking"]["date"] = "Monday"
        self.assertEqual(memory.get("one")["booking"]["date"], "Tomorrow")
        self.assertEqual(memory.get("two"), {})
        memory.clear("one")
        self.assertEqual(memory.get("one"), {})

    def test_requirements_keep_previous_values_when_extraction_is_empty(self):
        previous = {"service": "plumber", "location": "galle", "date": "Tomorrow"}
        result = merge_requirements(previous, {"service": "", "location": "", "description": " Fix sink "})
        self.assertEqual(result, {"service": "Plumbing", "location": "Galle", "date": "Tomorrow", "description": "Fix sink"})
        self.assertEqual(previous["service"], "plumber")

    def test_deterministic_planner_cases(self):
        for case in PLANNER_CASES:
            with self.subTest(case=case["name"]):
                result = planner_agent(case["state"])
                self.assertEqual(result["next_action"], case["expected_action"])
                if "expected_missing" in case:
                    self.assertEqual(set(result["missing_fields"]), case["expected_missing"])
