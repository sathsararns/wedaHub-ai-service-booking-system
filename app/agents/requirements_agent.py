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

Fields to extract:

- service
- location
- date
- description

If any field is missing, return null for that field.

Return structured data only.
"""
),
("human","{input}")
]
)

requirements_agent = prompt | llm.with_structured_output(Requirement)