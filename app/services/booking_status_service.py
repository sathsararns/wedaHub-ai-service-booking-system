import logging

import requests

from app.core.config import BACKEND_URL

logger = logging.getLogger(__name__)


def get_booking_status(booking_id: str):

    try:

        url = f"{BACKEND_URL}/api/bookings/{booking_id}"

        logger.info("Booking status lookup -> %s", url)

        response = requests.get(url)

        logger.info(
            "Booking status lookup <- status=%s",
            response.status_code,
        )

        if response.status_code != 200:

            logger.warning(
                "Booking status lookup failed: %s",
                response.text,
            )

            return {
                "success": False,
                "error": response.text
            }

        return {
            "success": True,
            "booking": response.json()
        }

    except Exception as e:

        logger.exception("Booking status lookup errored")

        return {
            "success": False,
            "error": str(e)
        }