from app.tools.provider_tool import ProviderTool


def search_agent(requirement):

    print("Searching...")

    print(requirement.service)
    print(requirement.location)

    providers = ProviderTool.search(
        service=requirement.service,
        location=requirement.location,
    )

    return providers