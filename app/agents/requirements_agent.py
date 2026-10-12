"""Structured extraction of service booking requirements."""
from functools import lru_cache

from app.core.llm import get_llm
from app.models.requirements import Requirement
from app.prompts.requirements_prompt import requirements_prompt


@lru_cache(maxsize=1)
def get_requirements_agent():
    return requirements_prompt | get_llm().with_structured_output(Requirement)
