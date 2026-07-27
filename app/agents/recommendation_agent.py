from langchain_core.output_parsers import PydanticOutputParser

from app.core.llm import llm

from app.prompts.recommendation_prompt import recommendation_prompt

from app.models.recommendation import RecommendationResponse

parser = PydanticOutputParser(
    pydantic_object=RecommendationResponse
)

recommendation_agent = (

    recommendation_prompt

    | llm

    | parser

)