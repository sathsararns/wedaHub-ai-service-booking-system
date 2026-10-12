"""Manual check; run explicitly with python -m from the service root."""


def main():
    from app.graph.workflow import graph

    result = graph.invoke(
        {
            "user_input": "I need an electrician in Matara tomorrow at 10 AM"
        }
    )

    print(result["response"])


if __name__ == "__main__":
    main()
