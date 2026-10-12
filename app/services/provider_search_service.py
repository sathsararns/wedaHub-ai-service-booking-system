import logging

from app.clients.backend_client import backend_client

logger = logging.getLogger(__name__)


def search_providers(requirement):
    logger.info(
        "Searching providers | service=%r location=%r",
        requirement.service,
        requirement.location,
    )

    providers = backend_client.search_providers(
        service=requirement.service,
        location=requirement.location,
    )

    if providers is None:
        providers = []

    logger.info("Providers found: %d", len(providers))
    logger.debug("Providers: %s", providers)

    return providers
