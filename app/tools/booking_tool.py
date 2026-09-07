import os
import requests


class BookingTool:
    BASE_URL = os.getenv("BACKEND_URL", "http://localhost:3000")

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

        print("\n========== BOOKING REQUEST ==========")
        print(payload)
        print("\n========== REQUEST URL ==========")
        print(url)

        response = requests.post(
            url,
            json=payload,
            headers=headers,
            timeout=20,
        )

        print("\n========== STATUS ==========")
        print(response.status_code)

        try:
            data = response.json()
        except Exception:
            data = {"message": response.text}

        print("\n========== RESPONSE ==========")
        print(data)

        if response.status_code >= 400:
            message = data.get("message") if isinstance(data, dict) else str(data)
            raise Exception(message or "Booking request failed.")

        return data