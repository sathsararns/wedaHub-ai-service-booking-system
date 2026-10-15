from copy import deepcopy
import unittest
from unittest.mock import patch

from app.graph.workflow import graph
from app.models.requirements import Requirement


class WorkflowTests(unittest.TestCase):
    def setUp(self):
        self.state = {
            "session_id": "test-session", "customer_id": "customer-1",
            "user_input": "yes",
            "requirements": {"service": "Electrician", "location": "Galle", "date": "Tomorrow", "description": "Fix light"},
            "booking": {"provider_id": "provider-1", "provider_name": "Test provider", "service": "Electrician", "city": "Galle", "date": "Tomorrow", "description": "Fix light"},
        }
        self.extraction = patch("app.graph.nodes.requirement_node.get_requirements_agent")
        self.requirements_agent = self.extraction.start().return_value
        self.requirements_agent.invoke.return_value = Requirement()
        self.addCleanup(self.extraction.stop)

    @patch("app.tools.bookings.backend_client.create_booking")
    @patch("app.graph.nodes.booking_create_node.run_tool_agent")
    def test_confirmed_booking_reaches_creation_through_the_real_graph(self, runner, create):
        create.return_value = {"booking": {"_id": "booking-1", "status": "pending"}}

        def run_tools(session_id, system_prompt, human_prompt, tools):
            tools[0].invoke({})
            return ["create_booking"]

        runner.side_effect = run_tools
        result = graph.invoke(deepcopy(self.state))
        self.assertTrue(result["booking_confirmed"])
        self.assertTrue(result["booking_created"])
        self.assertEqual(result["booking_result"]["booking_id"], "booking-1")
        create.assert_called_once()

    @patch("app.tools.bookings.backend_client.create_booking")
    @patch("app.graph.nodes.booking_create_node.run_tool_agent")
    def test_cancellation_never_reaches_creation(self, runner, create):
        self.state["user_input"] = "no"
        result = graph.invoke(deepcopy(self.state))
        self.assertFalse(result["booking_confirmed"])
        runner.assert_not_called()
        create.assert_not_called()

    @patch("app.graph.nodes.booking_create_node.run_tool_agent")
    def test_complete_booking_still_waits_for_confirmation(self, runner):
        self.state["user_input"] = "Here are my details"
        result = graph.invoke(deepcopy(self.state))
        self.assertFalse(result["booking_confirmed"])
        self.assertIn("confirm", result["response"].lower())
        runner.assert_not_called()

    @patch("app.graph.nodes.booking_create_node.run_tool_agent")
    def test_previous_confirmation_cannot_bypass_the_current_reply(self, runner):
        self.state["booking_confirmed"] = True
        self.state["user_input"] = "no"
        result = graph.invoke(deepcopy(self.state))
        self.assertFalse(result["booking_confirmed"])
        runner.assert_not_called()

    @patch("app.graph.nodes.booking_create_node.run_tool_agent")
    @patch("app.graph.nodes.search_agent_node.run_tool_agent")
    def test_door_description_keeps_the_selected_electrician_even_if_model_reclassifies_it(self, search_runner, create_runner):
        self.state["user_input"] = "i wanna repair my door"
        self.requirements_agent.invoke.return_value = Requirement(service="Carpenter", description="repair my door")
        for providers in ([{"_id": "provider-1", "category": "Electrician"}], []):
            with self.subTest(providers=providers):
                self.state["providers"] = providers
                self.state["booking_confirmed"] = True
                result = graph.invoke(deepcopy(self.state))
                self.assertEqual(result["requirements"]["service"], "Electrician")
                self.assertEqual(result["booking"]["service"], "Electrician")
                self.assertEqual(result["booking"]["provider_id"], "provider-1")
                self.assertEqual(result["booking"]["description"], "repair my door")
                self.assertEqual(result["booking"]["date"], "Tomorrow")
                self.assertFalse(result["booking_confirmed"])
                self.assertIsNone(result["service_change"])
                self.assertIn("Service : Electrician", result["response"])
                self.assertNotIn("Carpenter", result["response"])
        search_runner.assert_not_called()
        create_runner.assert_not_called()
        self.requirements_agent.invoke.assert_called_with({"input": "i wanna repair my door", "selected_service": "Electrician"})

    @patch("app.graph.nodes.booking_create_node.run_tool_agent")
    @patch("app.graph.nodes.search_agent_node.run_tool_agent", return_value=[])
    def test_category_can_change_before_a_provider_is_selected(self, search, create):
        self.state["booking"] = {}
        self.state["user_input"] = "I need a carpenter instead"
        self.requirements_agent.invoke.return_value = Requirement(service="Carpenter")
        result = graph.invoke(deepcopy(self.state))
        self.assertEqual(result["requirements"]["service"], "Carpenter")
        self.assertEqual(result["planner"]["next_action"], "search_services")
        search.assert_called_once()
        create.assert_not_called()

    @patch("app.graph.nodes.booking_create_node.run_tool_agent")
    def test_new_carpenter_selection_reuses_date_and_description(self, create_runner):
        self.state["booking"] = {}
        self.state["user_input"] = "book 1"
        self.state["requirements"].update(service="Carpenter", description="repair my door")
        self.state["providers"] = [{"_id": "carpenter-1", "category": "Carpenter"}]
        self.state["recommended_providers"] = [{"provider_index": 0, "provider_id": "carpenter-1", "provider_name": "Real carpenter"}]
        result = graph.invoke(deepcopy(self.state))
        self.assertEqual(result["booking"]["provider_id"], "carpenter-1")
        self.assertEqual(result["booking"]["provider_name"], "Real carpenter")
        self.assertEqual(result["booking"]["service"], "Carpenter")
        self.assertEqual(result["booking"]["date"], "Tomorrow")
        self.assertEqual(result["booking"]["description"], "repair my door")
        self.assertFalse(result["booking_confirmed"])
        create_runner.assert_not_called()

    @patch("app.graph.nodes.booking_create_node.run_tool_agent")
    @patch("app.graph.nodes.search_agent_node.run_tool_agent", return_value=[])
    def test_existing_mislabeled_draft_is_restored_to_the_selected_provider_category(self, search, create):
        self.state["user_input"] = "repair my electrical door"
        self.state["requirements"].update(service="Carpenter", description="repair my door")
        self.state["booking"].update(service="Carpenter", description="repair my door")
        self.state["providers"] = [{"_id": "provider-1", "category": "Electrician"}]
        result = graph.invoke(deepcopy(self.state))
        self.assertEqual(result["booking"]["service"], "Electrician")
        self.assertEqual(result["requirements"]["service"], "Electrician")
        self.assertEqual(result["booking"]["provider_id"], "provider-1")
        self.assertIn("Service : Electrician", result["response"])
        create.assert_not_called()
        search.assert_not_called()

    @patch("app.graph.nodes.booking_create_node.run_tool_agent")
    def test_a_previous_success_is_not_reported_again_on_the_next_turn(self, runner):
        self.state["user_input"] = "thanks"
        self.state["booking_status"] = "success"
        self.state["booking_created"] = True
        self.state["booking_result"] = {"booking_id": "old-booking"}
        result = graph.invoke(deepcopy(self.state))
        self.assertFalse(result["booking_created"])
        self.assertNotIn("Booking Created", result["response"])
        self.assertEqual(result["booking_result"]["booking_id"], "old-booking")
        runner.assert_not_called()
