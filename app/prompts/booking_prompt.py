from langchain_core.prompts import ChatPromptTemplate

booking_prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        """
You are Booking Agent.

The user has already received provider recommendations.

Extract:

- provider_index
- date
- time

Return ONLY JSON.

Example:

{{
    "provider_index": 0,
    "date": "tomorrow",
    "time": "10 AM"
}}
"""
    ),
    ("human", "{input}")
])