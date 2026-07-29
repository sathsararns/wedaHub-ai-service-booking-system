import requests


BACKEND_URL = "http://localhost:3000/api"


def get_booking_status(booking_id: str):

    try:

        url = f"{BACKEND_URL}/bookings/{booking_id}"

        print("===== BOOKING STATUS URL =====")
        print(url)

        response = requests.get(url)

        print("===== STATUS =====")
        print(response.status_code)

        print("===== RESPONSE =====")
        print(response.text)

        if response.status_code != 200:

            return {
                "success": False,
                "error": response.text
            }

        return {
            "success": True,
            "booking": response.json()
        }

    except Exception as e:

        return {
            "success": False,
            "error": str(e)
        }