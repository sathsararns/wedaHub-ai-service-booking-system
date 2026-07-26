from langchain_core.prompts import ChatPromptTemplate

from app.core.llm import llm
from app.models.recommendation import RecommendationResult

prompt = ChatPromptTemplate.from_messages(
[
(
"system",
"""
You are a Recommendation Agent.

Choose the best providers.

Consider

- Rating
- Experience
- Price
- Distance

Recommend only the best providers.

Return structured output.
"""
),

(
"human",
"""
Customer Requirements

{requirements}

Providers

{providers}
"""
)

]
)

recommendation_agent = prompt | llm.with_structured_output(
    RecommendationResult
)