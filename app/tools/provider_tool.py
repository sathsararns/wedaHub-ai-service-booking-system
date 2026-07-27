import requests
from app.config import EXPRESS_API


class ProviderTool:

    @staticmethod
    def search(service, location):

        print("Calling Backend")

        response = requests.get(
            f"{EXPRESS_API}/providers/search",
            params={
                "service": service,
                "location": location,
            },
            timeout=20,
        )

        print(response.url)

        response.raise_for_status()

        data = response.json()

        print(data)

        return data