"""Manual check; run explicitly with python -m from the service root."""


def main():
    from app.services.chat_service import chat

    print(

        chat(

            "abc123",

            user_input="I need an electrician in Matara tomorrow"

        )

    )

    print("--------------------------------")

    print(

        chat(

            "abc123",

            user_input="Book 1 tomorrow 10 AM"

        )

    )


if __name__ == "__main__":
    main()
