from app.tools.provider_tool import ProviderTool


def search_agent(requirement):
    print("========== SEARCH AGENT ==========")

    print("Service :", requirement.service)
    print("Location:", requirement.location)

    providers = ProviderTool.search(
        service=requirement.service,
        location=requirement.location,
    )

    if providers is None:
        providers = []

    print(f"Providers Found: {len(providers)}")
    print(providers)

    return providers