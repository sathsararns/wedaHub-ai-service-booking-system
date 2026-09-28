import logging

import requests

from app.core.config import BACKEND_URL

logger = logging.getLogger(__name__)


class BookingTool:
    BASE_URL = BACKEND_URL

    @staticmethod
    def create_booking(
        provider_id,
        customer_id,
        service,
        city,
        date,
        description,
        auth_token=None,
    ):
        url = f"{BookingTool.BASE_URL}/api/bookings/ai"

        payload = {
            "providerId": provider_id,
            "customerId": customer_id,
            "service": service,
            "city": city,
            "description": description,
            "date": str(date).lower() if date else "",
        }

        headers = {
            "Content-Type": "application/json",
        }

        if auth_token:
            if auth_token.lower().startswith("bearer "):
                headers["Authorization"] = auth_token
            else:
                headers["Authorization"] = f"Bearer {auth_token}"

        logger.info("Booking request -> %s | payload=%s", url, payload)

        response = requests.post(
            url,
            json=payload,
            headers=headers,
            timeout=20,
        )

        try:
            data = response.json()
        except Exception:
            data = {"message": response.text}

        logger.info(
            "Booking request <- status=%s response=%s",
            response.status_code,
            data,
        )

        if response.status_code >= 400:
            message = data.get("message") if isinstance(data, dict) else str(data)
            logger.error("Booking request failed: %s", message)
            raise Exception(message or "Booking request failed.")

        return data