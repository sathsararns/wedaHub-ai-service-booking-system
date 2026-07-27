from app.agents.planner_agent import planner_agent

def planner_node(state):

    result = planner_agent.invoke(
        {
            "requirements": str(state["requirements"])
        }
    )

    print("===== PLANNER =====")
    print(result)

    state["planner"] = result.model_dump()

    return state