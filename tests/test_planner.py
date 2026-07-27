from app.agents.planner_agent import planner_agent

response = planner_agent.invoke(
{
    "requirements": """
    Service: Photographer
    Location: Galle
    Date: Tomorrow
    Time: 10 AM
    """
}
)

print(response)

print(response.next_action)