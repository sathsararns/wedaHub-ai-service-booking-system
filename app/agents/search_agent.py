from app.tools.provider_tool import ProviderTool


def search_agent(requirement):

    providers = ProviderTool.search(

        service=requirement.service,

        location=requirement.location,

    )

    return providers