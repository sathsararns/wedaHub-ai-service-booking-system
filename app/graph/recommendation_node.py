from app.agents.recommendation_agent import recommendation_agent


def recommendation_node(state):

    print("===== PROVIDERS BEFORE AI =====")
    print(state["providers"])

    result = recommendation_agent.invoke(
        {
            "requirements": str(state["requirements"]),
            "providers": str(state["providers"])
        }
    )

    print("===== AI RECOMMENDATION =====")
    print(result)

    state["recommendations"] = result.model_dump()

    return state