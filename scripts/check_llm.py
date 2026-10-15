"""Manual check; run explicitly with python -m from the service root."""


def main():
    from app.core.llm import get_llm

    response = get_llm().invoke("Say hello")

    print(response.content)


if __name__ == "__main__":
    main()
