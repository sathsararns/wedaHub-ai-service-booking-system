"""Manual check; run explicitly with python -m from the service root."""


def main():
    from groq import Groq
    from dotenv import load_dotenv
    import os

    load_dotenv()

    client = Groq(api_key=os.getenv("GROQ_API_KEY"))

    print("Available models:")

    models = client.models.list()

    for m in models.data:
        print("-", m.id)


if __name__ == "__main__":
    main()
