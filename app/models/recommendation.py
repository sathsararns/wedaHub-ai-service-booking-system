from pydantic import BaseModel
from typing import List


class RecommendedProvider(BaseModel):
    provider_id: str
    business_name: str
    reason: str


class RecommendationResult(BaseModel):
    recommendations: List[RecommendedProvider]