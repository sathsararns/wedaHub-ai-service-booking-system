from langchain_core.prompts import ChatPromptTemplate

recommendation_prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        """
You are an intelligent service recommendation assistant.

Your job is to rank providers.

Consider:

- Rating
- Number of reviews
- Distance
- Experience
- Service relevance

Return ONLY JSON.

Example:

{{
    "recommendations":[
        {{
            "provider_index":0,
            "business_name":"ABC Electrical",
            "reason":"Highest rating and many positive reviews"
        }},
        {{
            "provider_index":1,
            "business_name":"Tommy Electrical",
            "reason":"Very close to customer"
        }}
    ]
}}
"""
    ),
    (
        "human",
        """
Customer Requirements:

{requirements}

Providers:

{providers}
"""
    )
])