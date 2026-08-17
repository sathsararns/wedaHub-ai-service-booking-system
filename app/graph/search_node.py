from app.agents.search_agent import search_agent
from app.models.requirements import Requirement


def search_node(state):

    requirement = Requirement(**state["requirements"])

    print("\n===== SEARCH INPUT =====")
    print(requirement)

    # ------------------------------------------
    # Clear old booking data
    # ------------------------------------------

    state.pop("booking_error", None)
    state.pop("booking_result", None)

    # ------------------------------------------
    # Search providers
    # ------------------------------------------

    providers = search_agent(requirement)

    print("\n===== SEARCH RESULT =====")
    print(providers)

    state["providers"] = providers

    return state