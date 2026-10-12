from langchain_core.prompts import ChatPromptTemplate


planner_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """
You are the Planner Agent.

Your ONLY responsibility is deciding the next workflow.

Available actions

1. search_services
2. book_provider
3. await_confirmation
4. create_booking
5. booking_status
6. ask_login
7. ask_more_information
8. general_chat
9. response

Return ONLY structured output.
""",
        ),
        (
            "human",
            """
Current State

{requirements}
""",
        ),
    ]
)
