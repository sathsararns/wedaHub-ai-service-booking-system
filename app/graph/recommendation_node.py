from app.agents.recommendation_agent import recommendation_agent


def recommendation_node(state):

    providers = state.get("providers") or []

    print("===== PROVIDERS BEFORE AI =====")
    print(providers)

    # No providers -> skip AI
    if not providers:
        state["recommendations"] = {
            "recommendations": []
        }
        state["recommended_providers"] = []
        return state

    result = recommendation_agent.invoke(
        {
            "requirements": state["requirements"],
            "providers": providers,
        }
    )

    print("===== AI RECOMMENDATION =====")
    print(result)

    state["recommendations"] = result.model_dump()

    state["recommended_providers"] = []

    for item in result.recommendations:

        if item.provider_index >= len(providers):
            continue

        provider = providers[item.provider_index]

        state["recommended_providers"].append(
            {
                "provider_index": item.provider_index,
                "provider_id": provider.get("_id"),
                "provider_name": (
                    provider.get("businessName")
                    or (
                        provider.get("firstName", "")
                        + " "
                        + provider.get("lastName", "")
                    ).strip()
                ),
            }
        )

    return state