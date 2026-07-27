from app.agents.recommendation_agent import recommendation_agent


def recommendation_node(state):

    result = recommendation_agent.invoke({

        "requirements": str(state["requirements"]),

        "providers": str(state["providers"])

    })

    state["recommendations"] = result.model_dump()

    return state