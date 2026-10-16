import json
import threading
import unittest
from concurrent.futures import ThreadPoolExecutor
from unittest.mock import patch

from fastapi.testclient import TestClient

from app.memory.store import memory
from main import app


class ChatApiTests(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)
        self.addCleanup(self.client.close)

    def test_health_does_not_call_the_model_or_backend(self):
        with patch("app.api.chat.chat") as chat:
            response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "ok"})
        chat.assert_not_called()

    @patch("app.api.chat.chat")
    def test_chat_keeps_the_frontend_request_and_response_contract(self, chat):
        chat.return_value = {"response": "Hello", "recommended_providers": [], "booking": {}}
        response = self.client.post("/chat", json={"message": "hi", "customerId": "customer-1", "sessionId": "session-1"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"response": "Hello", "recommendations": [], "booking": None})
        chat.assert_called_once_with(session_id="session-1", customer_id="customer-1", user_input="hi")

    @patch("app.api.chat.chat")
    def test_stream_keeps_sse_chunks_and_final_metadata(self, chat):
        chat.return_value = {"response": "One two three four five six", "recommended_providers": [{"provider_id": "provider-1"}], "booking": None}
        response = self.client.post("/chat/stream", json={"message": "hi", "customer_id": "customer-1"})
        self.assertEqual(response.status_code, 200)
        events = [json.loads(line[6:]) for line in response.text.splitlines() if line.startswith("data: ")]
        self.assertEqual("".join(event["text"] for event in events if event["type"] == "chunk"), chat.return_value["response"])
        self.assertEqual(events[-1], {"type": "done", "recommendations": [{"provider_id": "provider-1"}], "booking": None})

    @patch("app.api.chat.chat", side_effect=RuntimeError("private model credentials"))
    def test_stream_failure_is_an_explicit_error_not_a_successful_empty_reply(self, chat):
        response = self.client.post("/chat/stream", json={"message": "hi"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers["x-accel-buffering"], "no")
        events = [json.loads(line[6:]) for line in response.text.splitlines() if line.startswith("data: ")]
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0]["type"], "error")
        self.assertNotIn("private model credentials", response.text)

    def test_health_remains_responsive_while_a_chat_workflow_is_waiting(self):
        started = threading.Event()
        release = threading.Event()

        def slow_chat(**kwargs):
            started.set()
            release.wait(timeout=3)
            return {"response": "Hello"}

        with patch("app.api.chat.chat", side_effect=slow_chat):
            with self.client, ThreadPoolExecutor(max_workers=2) as pool:
                reply = pool.submit(self.client.post, "/chat/stream", json={"message": "hi"})
                try:
                    self.assertTrue(started.wait(timeout=2))
                    health = pool.submit(self.client.get, "/health").result(timeout=1)
                    self.assertEqual(health.status_code, 200)
                finally:
                    release.set()
                self.assertIn('"type": "done"', reply.result(timeout=2).text)

    @patch("app.api.chat.chat")
    def test_draft_bookings_never_appear_as_created_in_json_or_stream(self, chat):
        chat.return_value = {
            "response": "Please describe the work you need.",
            "booking": {"provider_id": "provider-1", "service": "Electrician", "date": "tomorrow"},
            "booking_created": False,
        }
        response = self.client.post("/chat", json={"message": "tomorrow"})
        self.assertIsNone(response.json()["booking"])
        stream = self.client.post("/chat/stream", json={"message": "tomorrow"})
        events = [json.loads(line[6:]) for line in stream.text.splitlines() if line.startswith("data: ")]
        self.assertIsNone(events[-1]["booking"])

    @patch("app.api.chat.chat")
    def test_successful_creation_includes_the_persisted_booking(self, chat):
        booking = {"booking_id": "booking-1", "provider_id": "provider-1", "service": "Electrician"}
        chat.return_value = {"response": "Booking created", "booking_created": True, "booking_result": booking}
        response = self.client.post("/chat", json={"message": "yes"})
        self.assertEqual(response.json()["booking"], booking)
        stream = self.client.post("/chat/stream", json={"message": "yes"})
        events = [json.loads(line[6:]) for line in stream.text.splitlines() if line.startswith("data: ")]
        self.assertEqual(events[-1]["booking"], booking)

    def test_reset_clears_only_the_requested_session(self):
        memory.save("reset-test", {"response": "old"})
        memory.save("other-test", {"response": "keep"})
        self.addCleanup(memory.clear, "reset-test")
        self.addCleanup(memory.clear, "other-test")
        response = self.client.post("/chat/reset", json={"sessionId": "reset-test"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(memory.get("reset-test"), {})
        self.assertEqual(memory.get("other-test"), {"response": "keep"})
