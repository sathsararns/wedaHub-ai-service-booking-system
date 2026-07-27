from app.agents.search_agent import search_agent
from app.models.requirements import Requirement


def search_node(state):

    requirement = Requirement(**state["requirements"])

    print("===== SEARCH INPUT =====")
    print(requirement)

    providers = search_agent(requirement)

    print("===== SEARCH RESULT =====")
    print(providers)

    state["providers"] = providers

    return state