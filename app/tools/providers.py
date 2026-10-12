"""Request-scoped provider search and recommendation tools."""
import logging

from langchain_core.tools import tool
from pydantic import BaseModel, Field

from app.agents.recommendation_agent import get_recommendation_agent
from app.models.requirements import Requirement
from app.rag.provider_index import semantic_search
from app.services.provider_search_service import search_providers as keyword_search

logger = logging.getLogger(__name__)


class SearchProvidersInput(BaseModel):
    service: str = Field(description="Service category to search for, e.g. Electrician")
    location: str = Field(description="City/location to search in, e.g. Kandy")


def make_provider_tools(context: dict, session_id: str | None = None):
    @tool("search_providers", args_schema=SearchProvidersInput)
    def search_providers(service: str, location: str) -> str:
        """Search WedaHub's real provider database for a service in a location."""

        requirements = context.get("requirements") or {}
        service = requirements.get("service") or service
        location = requirements.get("location") or location

        logger.info(
            "session=%s TOOL CALL search_providers(service=%r, location=%r)",
            session_id, service, location,
        )

        query = f"{service} in {location}".strip()
        user_input = context.get("user_input")
        if user_input:
            query = f"{query}. Customer request: {user_input}"

        retrieval_mode = "semantic"
        results = semantic_search(query, service=service)

        if results is None:
            # Embedding model unavailable — fall back to the exact/regex path.
            retrieval_mode = "keyword_fallback"
            requirement = Requirement(service=service, location=location)
            providers = keyword_search(requirement)
        elif results:
            providers = [provider for provider, _score in results]
        else:
            # Semantic retrieval ran but nothing cleared the relevance
            # threshold — a real "no good match", not an unavailable index.
            providers = []

        context["providers"] = providers

        logger.info(
            "session=%s TOOL RESULT search_providers -> %d provider(s) via %s",
            session_id, len(providers), retrieval_mode,
        )

        if not providers:
            return f"No providers found for {service} in {location}."

        return (
            f"Found {len(providers)} provider(s) for {service} in {location} "
            f"(retrieval={retrieval_mode})."
        )


    @tool("recommend_providers")
    def recommend_providers() -> str:
        """
        Rank the providers search_providers just found and select the
        best matches. Only call this after search_providers has run in
        this turn and found at least one provider.
        """

        providers = context.get("providers") or []

        logger.info(
            "session=%s TOOL CALL recommend_providers (providers_available=%d)",
            session_id, len(providers),
        )

        if not providers:
            context["recommendations"] = {"recommendations": []}
            context["recommended_providers"] = []
            return "No providers available to rank — call search_providers first."

        result = get_recommendation_agent().invoke(
            {
                "requirements": context.get("requirements", {}),
                "providers": providers,
            }
        )

        recommended = []
        for item in result.recommendations:
            if not 0 <= item.provider_index < len(providers):
                continue

            provider = providers[item.provider_index]
            recommended.append(
                {
                    "provider_index": item.provider_index,
                    "provider_id": provider.get("_id"),
                    "provider_name": (
                        provider.get("businessName")
                        or (
                            provider.get("firstName", "")
                            + " "
                            + provider.get("lastName", "")
                        ).strip()
                    ),
                    "provider": provider,
                    "rating": provider.get("rating"),
                    "city": provider.get("city") or provider.get("district"),
                    "reason": item.reason,
                }
            )

        context["recommendations"] = result.model_dump()
        context["recommended_providers"] = recommended

        logger.info(
            "session=%s TOOL RESULT recommend_providers -> ranked %d of %d",
            session_id, len(recommended), len(providers),
        )

        return f"Ranked and selected {len(recommended)} provider(s)."


    return {"search_providers": search_providers, "recommend_providers": recommend_providers}
