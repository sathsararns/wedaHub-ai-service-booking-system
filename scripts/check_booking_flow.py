"""Manual check; run explicitly with python -m from the service root."""


def main():
    from app.services.chat_service import chat

    session = "abc123"

    print(
        chat(
            session,
            user_input="I need an electrician in Matara tomorrow 10 AM"
        )
    )

    print("--------------------------------")

    print(
        chat(
            session,
            user_input="Book 1"
        )
    )

    print("--------------------------------")

    print(
        chat(
            session,
            user_input="What's the booking status?"
        )
    )


if __name__ == "__main__":
    main()
