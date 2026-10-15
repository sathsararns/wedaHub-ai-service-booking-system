"""Manual requirement extraction check; requires the configured LLM."""
from app.agents.requirements_agent import get_requirements_agent


def main():
    print(get_requirements_agent().invoke({"input": "I need an electrician in Galle tomorrow to fix a light"}))


if __name__ == "__main__":
    main()
