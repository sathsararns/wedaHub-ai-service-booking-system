import logging

import requests
from app.core.config import EXPRESS_API

logger = logging.getLogger(__name__)


class ProviderTool:

    @staticmethod
    def search(service, location):

        response = requests.get(
            f"{EXPRESS_API}/providers/search",
            params={
                "service": service,
                "location": location,
            },
            timeout=20,
        )

        logger.info("Provider search -> %s", response.url)

        response.raise_for_status()

        data = response.json()

        logger.debug("Provider search <- %s", data)

        return data