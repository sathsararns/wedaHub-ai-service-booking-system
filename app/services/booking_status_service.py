import logging

from app.clients.backend_client import backend_client

logger = logging.getLogger(__name__)


def get_booking_status(booking_id: str):

    try:

        return {
            "success": True,
            "booking": backend_client.get_booking(booking_id)
        }

    except Exception as e:

        logger.exception("Booking status lookup errored")

        return {
            "success": False,
            "error": str(e)
        }
