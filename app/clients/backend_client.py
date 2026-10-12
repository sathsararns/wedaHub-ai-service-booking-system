"""HTTP adapter for the Express backend; shared by services and retrieval."""
import logging

import requests

from app.core.config import BACKEND_URL, EXPRESS_API

logger = logging.getLogger(__name__)
REQUEST_TIMEOUT_SECONDS = 20


class BackendClient:
    def __init__(self, base_url=BACKEND_URL, api_url=EXPRESS_API):
        self.base_url = base_url.rstrip("/")
        self.api_url = (api_url or f"{self.base_url}/api").rstrip("/")

    def search_providers(self, service, location):
        response = requests.get(
            f"{self.api_url}/providers/search",
            params={"service": service, "location": location},
            timeout=REQUEST_TIMEOUT_SECONDS,
        )
        response.raise_for_status()
        return response.json()

    def create_booking(
        self, provider_id, customer_id, service, city, date, description,
        auth_token=None,
    ):
        payload = {
            "providerId": provider_id,
            "customerId": customer_id,
            "service": service,
            "city": city,
            "description": description,
            "date": str(date).lower() if date else "",
        }
        headers = {"Content-Type": "application/json"}
        if auth_token:
            headers["Authorization"] = (
                auth_token if auth_token.lower().startswith("bearer ")
                else f"Bearer {auth_token}"
            )

        response = requests.post(
            f"{self.base_url}/api/bookings/ai",
            json=payload,
            headers=headers,
            timeout=REQUEST_TIMEOUT_SECONDS,
        )
        try:
            data = response.json()
        except ValueError:
            data = {"message": response.text}

        logger.info("Booking request completed, status=%s", response.status_code)
        if response.status_code >= 400:
            message = data.get("message") if isinstance(data, dict) else str(data)
            raise RuntimeError(message or "Booking request failed.")
        return data

    def get_booking(self, booking_id):
        response = requests.get(
            f"{self.base_url}/api/bookings/{booking_id}",
            timeout=REQUEST_TIMEOUT_SECONDS,
        )
        if response.status_code != 200:
            raise RuntimeError(response.text)
        return response.json()


backend_client = BackendClient()
