import requests

from app.config import EXPRESS_API


class ProviderTool:

    @staticmethod
    def search(service, location):

        response = requests.get(

            f"{EXPRESS_API}/providers/search",

            params={
                "service": service,
                "location": location,
            },

            timeout=20

        )

        response.raise_for_status()

        return response.json()