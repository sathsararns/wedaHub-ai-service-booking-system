import requests
from app.config import EXPRESS_API


class BookingTool:

    @staticmethod
    def create_booking(
        provider_id,
        service,
        date,
        time,
        customer_id=None,
    ):

        response = requests.post(
            f"{EXPRESS_API}/bookings/ai",
            json={
                "providerId": provider_id,
                "customerId": customer_id,
                "service": service,
                "date": date,
                "time": time,
            },
            timeout=20,
        )

        response.raise_for_status()

        return response.json()