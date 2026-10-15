import unittest
from unittest.mock import patch

from app.models.recommendation import Recommendation, RecommendationResponse
from app.tools.factory import make_tools


class ToolTests(unittest.TestCase):
    @patch("app.tools.providers.semantic_search", return_value=[])
    def test_search_uses_the_current_requirements_over_model_arguments(self, search):
        context = {"requirements": {"service": "Carpenter", "location": "Matara"}}
        make_tools(context)["search_providers"].invoke({"service": "Electrician", "location": "Galle"})
        search.assert_called_once_with("Carpenter in Matara", service="Carpenter")

    @patch("app.tools.providers.semantic_search")
    def test_provider_tools_do_not_share_request_context(self, search):
        search.return_value = [({"_id": "provider-1"}, 0.9)]
        first, second = {}, {}
        one = make_tools(first)
        make_tools(second)
        one["search_providers"].invoke({"service": "Electrician", "location": "Galle"})
        self.assertEqual(first["providers"], [{"_id": "provider-1"}])
        self.assertNotIn("providers", second)

    @patch("app.tools.providers.keyword_search")
    @patch("app.tools.providers.semantic_search", return_value=None)
    def test_search_falls_back_when_semantic_index_is_unavailable(self, semantic, keyword):
        keyword.return_value = [{"_id": "provider-1"}]
        context = {}
        make_tools(context)["search_providers"].invoke({"service": "Electrician", "location": "Galle"})
        self.assertEqual(keyword.call_args.args[0].location, "Galle")
        self.assertEqual(context["providers"], keyword.return_value)

    @patch("app.tools.providers.keyword_search")
    @patch("app.tools.providers.semantic_search", return_value=[])
    def test_no_semantic_matches_remains_an_empty_result(self, semantic, keyword):
        context = {}
        make_tools(context)["search_providers"].invoke({"service": "Electrician", "location": "Galle"})
        self.assertEqual(context["providers"], [])
        keyword.assert_not_called()

    @patch("app.tools.providers.get_recommendation_agent")
    def test_empty_recommendations_do_not_initialize_the_llm(self, agent):
        context = {"providers": []}
        make_tools(context)["recommend_providers"].invoke({})
        self.assertEqual(context["recommended_providers"], [])
        agent.assert_not_called()

    @patch("app.tools.providers.get_recommendation_agent")
    def test_recommendations_resolve_real_records_and_reject_invalid_indices(self, agent):
        agent.return_value.invoke.return_value = RecommendationResponse(recommendations=[
            Recommendation(provider_index=-1, business_name="Invented", reason="Invalid"),
            Recommendation(provider_index=9, business_name="Invented", reason="Invalid"),
            Recommendation(provider_index=0, business_name="Invented", reason="Good match"),
        ])
        context = {"providers": [{"_id": "provider-1", "businessName": "Real business"}]}
        make_tools(context)["recommend_providers"].invoke({})
        recommended = context["recommended_providers"]
        self.assertEqual(len(recommended), 1)
        self.assertEqual(recommended[0]["provider_index"], 0)
        self.assertEqual(recommended[0]["provider_id"], "provider-1")
        self.assertEqual(recommended[0]["provider_name"], "Real business")

    @patch("app.tools.bookings.backend_client.create_booking")
    def test_incomplete_booking_cannot_call_the_backend(self, create):
        context = {"booking": {"provider_id": "provider-1"}}
        make_tools(context)["create_booking"].invoke({})
        self.assertIn("missing", context["booking_rejection_reason"])
        create.assert_not_called()

    @patch("app.tools.bookings.fetch_booking_status")
    def test_status_uses_the_booking_id_from_context(self, status):
        status.return_value = {"success": True, "booking": {"_id": "booking-1", "status": "pending"}}
        for booking_result in ({"booking_id": "booking-1"}, {"booking": {"_id": "booking-1"}}):
            with self.subTest(booking_result=booking_result):
                context = {"booking_result": booking_result}
                make_tools(context)["get_booking_status"].invoke({})
                self.assertEqual(context["booking_status_result"]["_id"], "booking-1")
        self.assertEqual(status.call_count, 2)
        status.assert_called_with("booking-1")
