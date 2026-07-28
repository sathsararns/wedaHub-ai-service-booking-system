from app.agents.recommendation_agent import recommendation_agent


def recommendation_node(state):

    print("===== PROVIDERS BEFORE AI =====")
    print(state["providers"])

    result = recommendation_agent.invoke(
        {
            "requirements": state["requirements"],
            "providers": state["providers"]
        }
    )

    print("===== AI RECOMMENDATION =====")
    print(result)

    state["recommendations"] = result.model_dump()

    # save recommendation list for future booking
    state["recommended_providers"] = []

    for item in result.recommendations:

        provider = state["providers"][item.provider_index]

        state["recommended_providers"].append(
            {
                "provider_index": item.provider_index,
                "provider_id": provider["_id"],
                "provider_name": (
                    provider.get("businessName")
                    or (
                        provider.get("firstName", "")
                        + " "
                        + provider.get("lastName", "")
                    ).strip()
                )
            }
        )

    return state