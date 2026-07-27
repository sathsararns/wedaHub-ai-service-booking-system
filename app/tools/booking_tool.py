import requests

from app.config import EXPRESS_API


class BookingTool:

    @staticmethod
    def create_booking(data):

        response = requests.post(
            f"{EXPRESS_API}/bookings",
            json=data,
            timeout=20
        )

        response.raise_for_status()

        return response.json()