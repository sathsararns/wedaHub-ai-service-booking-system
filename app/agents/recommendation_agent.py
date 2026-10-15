"""Rank retrieved providers using structured model output."""
from functools import lru_cache

from langchain_core.output_parsers import PydanticOutputParser

from app.core.llm import get_llm
from app.models.recommendation import RecommendationResponse
from app.prompts.recommendation_prompt import recommendation_prompt


@lru_cache(maxsize=1)
def get_recommendation_agent():
    parser = PydanticOutputParser(pydantic_object=RecommendationResponse)
    return recommendation_prompt | get_llm() | parser
