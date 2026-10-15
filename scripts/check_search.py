"""Manual keyword provider search; requires the Express backend."""
from app.models.requirements import Requirement
from app.services.provider_search_service import search_providers


def main():
    print(search_providers(Requirement(service="Electrician", location="Matara")))


if __name__ == "__main__":
    main()
