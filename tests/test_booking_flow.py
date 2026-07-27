from app.services.chat_service import chat

print(
    chat(
        "abc123",
        "I need an electrician in Matara tomorrow"
    )
)

print("--------------------------------")

print(
    chat(
        "abc123",
        "Book 1 tomorrow 10 AM"
    )
)