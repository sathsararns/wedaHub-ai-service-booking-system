import logging

from app.tools.provider_tool import ProviderTool

logger = logging.getLogger(__name__)


def search_agent(requirement):
    logger.info(
        "Searching providers | service=%r location=%r",
        requirement.service,
        requirement.location,
    )

    providers = ProviderTool.search(
        service=requirement.service,
        location=requirement.location,
    )

    if providers is None:
        providers = []

    logger.info("Providers found: %d", len(providers))
    logger.debug("Providers: %s", providers)

    return providers