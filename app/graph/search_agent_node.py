"""
Search + recommend, via LLM tool-calling, backed by semantic retrieval.

Replaces the old search_node.py + recommendation_node.py pair, which
always ran both operations in a fixed Python sequence
(search_agent(...) then recommendation_agent.invoke(...) unconditionally
back to back). Here, an LLM holding exactly two tools —
search_providers and recommend_providers — decides whether/when to call
each, based on the conversation. In practice it always calls
search_providers first (that's the only thing it can usefully do with a
service+location), then decides whether the results are worth ranking —
if search finds nothing, it correctly stops without calling
recommend_providers at all (verified live; see the AI service README).

search_providers itself now retrieves candidates semantically
(app/rag/provider_index.py) rather than by exact category/district
matching alone — see app/tools/agent_tools.py for the retrieval +
fallback logic. This node's only job regarding that is to hand the raw
user message through `context`, so the tool can build a richer
retrieval query than just "service in location".
"""

import logging

from app.core.tracing import trace_node
from app.graph.tool_agent import run_tool_agent
from app.tools.agent_tools import make_tools

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """
You are WedaHub's provider-search agent.

You have two tools:
- search_providers(service, location): search real providers in WedaHub's database.
- recommend_providers(): rank the providers search_providers just found and pick the best matches.

Call search_providers first, using exactly the service and location you are given.
If it finds providers, call recommend_providers next to rank them.
If it finds none, do not call recommend_providers.

Only call tools. Never answer in prose.
"""


@trace_node("search_agent_node")
def search_agent_node(state):
    session_id = state.get("session_id")
    requirements = state.get("requirements") or {}

    context = {
        "requirements": requirements,
        "user_input": state.get("user_input"),
        "providers": [],
        "recommendations": {"recommendations": []},
        "recommended_providers": [],
    }

    tools = make_tools(context, session_id=session_id)
    search_tools = [tools["search_providers"], tools["recommend_providers"]]

    human_prompt = (
        f"service: {requirements.get('service', '')}\n"
        f"location: {requirements.get('location', '')}"
    )

    called = run_tool_agent(session_id, SYSTEM_PROMPT, human_prompt, search_tools)

    state.pop("booking_error", None)
    state.pop("booking_result", None)

    state["providers"] = context.get("providers", [])
    state["recommendations"] = context.get("recommendations", {"recommendations": []})
    state["recommended_providers"] = context.get("recommended_providers", [])

    logger.info(
        "session=%s tools_called=%s providers_found=%d recommended=%d",
        session_id,
        called,
        len(state["providers"]),
        len(state["recommended_providers"]),
    )

    return state
