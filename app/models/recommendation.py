from pydantic import BaseModel

class Recommendation(BaseModel):
    provider_index: int
    business_name: str
    reason: str


class RecommendationResponse(BaseModel):
    recommendations: list[Recommendation]