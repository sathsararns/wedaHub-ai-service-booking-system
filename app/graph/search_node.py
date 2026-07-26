from app.agents.search_agent import search_agent
from app.models.requirements import Requirement


def search_node(state):

    requirement = Requirement(
        **state["requirements"]
    )

    providers = search_agent(requirement)

    state["providers"] = providers

    return state