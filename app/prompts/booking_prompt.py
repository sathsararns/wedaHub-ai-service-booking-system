from langchain_core.prompts import ChatPromptTemplate

booking_prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        """
You are Booking Agent.

The user has already received provider recommendations.

The providers shown to the user are numbered starting from 1.

IMPORTANT:

Book 1 -> provider_index = 0
Book 2 -> provider_index = 1
Book 3 -> provider_index = 2
Book 4 -> provider_index = 3

If the user does not provide the date or job description,
return empty strings.

Return ONLY valid JSON.

Example:

{{
    "provider_index": 0,
    "date": "",
    "description": ""
}}
"""
    ),
    ("human", "{input}")
])