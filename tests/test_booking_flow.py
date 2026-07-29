from app.services.chat_service import chat

session = "abc123"

print(
    chat(
        session,
        "I need an electrician in Matara tomorrow 10 AM"
    )
)

print("--------------------------------")

print(
    chat(
        session,
        "Book 1"
    )
)

print("--------------------------------")

print(
    chat(
        session,
        "What's the booking status?"
    )
)