from langchain_core.prompts import ChatPromptTemplate

from app.core.llm import llm
from app.models.requirements import Requirement

prompt = ChatPromptTemplate.from_messages(
[
(
"system",
"""
You are a Requirements Agent.

Extract the booking requirements.

Return structured data.
"""
),
("human","{input}")
]
)

requirements_agent = prompt | llm.with_structured_output(Requirement)