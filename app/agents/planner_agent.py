from langchain_core.prompts import ChatPromptTemplate

from app.core.llm import llm
from app.models.planner import PlannerDecision

prompt = ChatPromptTemplate.from_messages(
[
(
"system",
"""
You are the Planner Agent.

Your job is to decide the next step.

Rules:

If service is missing
→ ask_more_information

If location is missing
→ ask_more_information

If everything required exists
→ search_services

Return structured output only.
"""
),
("human","{requirements}")
]
)

planner_agent = prompt | llm.with_structured_output(PlannerDecision)