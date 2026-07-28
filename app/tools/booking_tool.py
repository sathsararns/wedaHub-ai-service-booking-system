import requests

from app.config import EXPRESS_API


class BookingTool:

    @staticmethod
    def create_booking(

        provider_id,

        date,

        time,

    ):

        response = requests.post(

            f"{EXPRESS_API}/bookings/ai",

            json={

                "providerId": provider_id,

                "date": date,

                "time": time,

            },

            timeout=20,

        )

        response.raise_for_status()

        return response.json()