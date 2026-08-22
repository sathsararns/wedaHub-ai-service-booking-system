import requests
from datetime import datetime, timedelta

from app.config import EXPRESS_API


class BookingTool:

    @staticmethod
    def normalize_date(date_value):
        """
        Normalize supported date formats.
        """

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
            return datetime.strptime(
                value,
                "%Y-%m-%d"
            ).strftime("%Y-%m-%d")

        except ValueError:
            pass

        try:
            return datetime.fromisoformat(
                value
            ).strftime("%Y-%m-%d")

        except ValueError:
            return value

    @staticmethod
    def create_booking(
        provider_id,
        service,
        city,
        date,
        description,
        customer_id=None,
    ):
        """
        Send booking request to Express API.
        """

        provider_id = str(provider_id)

        if customer_id:
            customer_id = str(customer_id)

        service = service.strip()
        city = city.strip() if city else ""
        description = description.strip()

        date = BookingTool.normalize_date(date)

        payload = {
            "providerId": provider_id,
            "customerId": customer_id,
            "service": service,
            "city": city,
            "description": description,
            "date": date,
        }

        print("\n========== BOOKING REQUEST ==========")
        print(payload)

        url = f"{EXPRESS_API}/bookings/ai"

        print("\n========== REQUEST URL ==========")
        print(url)

        try:

            response = requests.post(
                url,
                json=payload,
                timeout=20,
            )

            print("\n========== STATUS ==========")
            print(response.status_code)

            print("\n========== RESPONSE ==========")
            print(response.text)

            response.raise_for_status()

            try:
                result = response.json()

            except ValueError:
                raise Exception(
                    "Invalid JSON response received from booking service."
                )

            print("\n========== RESPONSE JSON ==========")
            print(result)

            return result

        except requests.exceptions.Timeout:

            raise Exception(
                "Booking service timed out."
            )

        except requests.exceptions.ConnectionError:

            raise Exception(
                "Unable to connect to booking service."
            )

        except requests.exceptions.HTTPError:

            try:
                error = response.json()

                message = (
                    error.get("message")
                    or error.get("error")
                    or response.text
                )

            except Exception:

                message = response.text

            raise Exception(message)

        except requests.exceptions.RequestException as e:

            raise Exception(str(e))