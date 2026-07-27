from app.agents.search_agent import search_agent
from app.models.requirements import Requirement


def search_node(state):

    requirement = Requirement(**state["requirements"])

    providers = search_agent(requirement)

    cleaned = []

    for p in providers:
        cleaned.append({
            "id": str(p["_id"]),
            "business_name": f"{p['firstName']} {p['lastName']}",
            "category": p.get("category"),
            "rating": p.get("rating", 0),
            "reviews": p.get("reviews", 0),
            "district": p.get("district"),
            "city": p.get("city"),
            "description": p.get("description", "")
        })

    state["providers"] = cleaned

    return state