"""Exercise a deterministic planner branch without calling the LLM."""
from app.agents.planner_agent import planner_agent


def main():
    print(planner_agent({"user_input": "I need a plumber", "requirements": {"service": "Plumbing", "location": "Galle"}}))


if __name__ == "__main__":
    main()
