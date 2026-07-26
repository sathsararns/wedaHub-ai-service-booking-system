import requests

from app.config import EXPRESS_API


def search_providers(service, location):

    response = requests.get(
        f"{EXPRESS_API}/providers/search",
        params={
            "service": service,
            "location": location,
        },
        timeout=20,
    )

    response.raise_for_status()

    return response.json()