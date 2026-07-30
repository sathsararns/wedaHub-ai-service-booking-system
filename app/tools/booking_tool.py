import requests
from datetime import datetime, timedelta

from app.config import EXPRESS_API


class BookingTool:

    @staticmethod
    def normalize_date(date_value):

        if not date_value:
            return None

        value = str(date_value).strip().lower()

        if value == "today":
            return datetime.now().strftime("%Y-%m-%d")

        if value == "tomorrow":
            return (
                datetime.now() + timedelta(days=1)
            ).strftime("%Y-%m-%d")

        try:
            datetime.strptime(value, "%Y-%m-%d")
            return value
        except:
            pass

        try:
            return datetime.fromisoformat(value).strftime("%Y-%m-%d")
        except:
            return value

    @staticmethod
    def create_booking(
        provider_id,
        service,
        date,
        description,
        customer_id=None,
    ):

        date = BookingTool.normalize_date(date)

        print("===== BOOKING REQUEST =====")

        print({

            "providerId": provider_id,

            "customerId": customer_id,

            "service": service,

            "description": description,

            "date": date,

        })

        payload = {

            "providerId": provider_id,

            "customerId": customer_id,

            "service": service,

            "description": description,

            "date": date,

        }

        url = f"{EXPRESS_API}/bookings/ai"

        print("===== URL =====")

        print(url)

        response = requests.post(

            url,

            json=payload,

            timeout=20,

        )

        print("===== STATUS =====")

        print(response.status_code)

        print("===== RESPONSE =====")

        print(response.text)

        response.raise_for_status()

        return response.json()