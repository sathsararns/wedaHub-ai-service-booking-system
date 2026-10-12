import unittest
from unittest.mock import patch

import requests

from app.clients.backend_client import BackendClient
from app.services.booking_status_service import get_booking_status


class BackendClientTests(unittest.TestCase):
    def setUp(self):
        self.client = BackendClient("http://backend:3000/", "http://backend:3000/api/")

    @patch("app.clients.backend_client.requests.get")
    def test_search_preserves_backend_query_contract(self, get):
        get.return_value.json.return_value = [{"_id": "provider-1"}]
        self.assertEqual(self.client.search_providers("Electrician", "Galle"), [{"_id": "provider-1"}])
        get.assert_called_once_with(
            "http://backend:3000/api/providers/search",
            params={"service": "Electrician", "location": "Galle"}, timeout=20,
        )
        get.return_value.raise_for_status.assert_called_once()

    def test_api_url_defaults_to_backend_api_prefix(self):
        self.assertEqual(BackendClient("http://backend:3000/", None).api_url, "http://backend:3000/api")

    @patch("app.clients.backend_client.requests.post")
    def test_booking_preserves_payload_and_forwards_authorization(self, post):
        post.return_value.status_code = 201
        post.return_value.json.return_value = {"booking": {"_id": "booking-1"}}
        result = self.client.create_booking("provider-1", "customer-1", "Electrician", "Galle", "Tomorrow", "Fix light", "token")
        self.assertEqual(result["booking"]["_id"], "booking-1")
        post.assert_called_once_with(
            "http://backend:3000/api/bookings/ai",
            json={"providerId": "provider-1", "customerId": "customer-1", "service": "Electrician", "city": "Galle", "description": "Fix light", "date": "tomorrow"},
            headers={"Content-Type": "application/json", "Authorization": "Bearer token"}, timeout=20,
        )

    @patch("app.clients.backend_client.requests.post")
    def test_booking_reports_non_json_backend_error(self, post):
        post.return_value.status_code = 502
        post.return_value.json.side_effect = ValueError("not JSON")
        post.return_value.text = "Backend unavailable"
        with self.assertRaisesRegex(RuntimeError, "Backend unavailable"):
            self.client.create_booking("p", "c", "Electrician", "Galle", "Tomorrow", "Fix light")

    @patch("app.clients.backend_client.requests.get")
    def test_booking_status_lookup_has_a_timeout(self, get):
        get.return_value.status_code = 200
        get.return_value.json.return_value = {"_id": "booking-1", "status": "pending"}
        self.assertEqual(self.client.get_booking("booking-1")["status"], "pending")
        get.assert_called_once_with("http://backend:3000/api/bookings/booking-1", timeout=20)

    @patch("app.services.booking_status_service.backend_client.get_booking")
    def test_status_service_preserves_failure_contract(self, get_booking):
        get_booking.side_effect = requests.Timeout("Backend timed out")
        with self.assertLogs("app.services.booking_status_service", level="ERROR"):
            result = get_booking_status("booking-1")
        self.assertEqual(result, {"success": False, "error": "Backend timed out"})
