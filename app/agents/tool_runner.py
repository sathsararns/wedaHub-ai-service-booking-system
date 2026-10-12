"""
Generic, bounded LLM tool-calling loop shared by the search/recommend,
booking-creation, and booking-status graph nodes.

This is the actual agentic mechanism: instead of a Python if/else
calling the underlying functions directly, the LLM is bound to a
specific, narrow set of tools (chosen per node — see factory.py) via
llm.bind_tools(), and DECIDES whether/which one to call. Tool execution
results are fed back as ToolMessages so the model can decide whether it
needs to call another tool next (e.g. call search_providers, see there
are results, then decide to call recommend_providers) — a real, if
intentionally short and narrowly-scoped, ReAct loop.

Each node only exposes the 1-2 tools relevant to that step (least
privilege) and keeps its own directive system prompt — this file just
runs whatever tool list and prompt it's given.
"""

import logging

from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage

from app.core.llm import get_llm

logger = logging.getLogger(__name__)

MAX_TOOL_ITERATIONS = 4


def run_tool_agent(session_id, system_prompt, human_prompt, tools):
    """
    Runs one bounded tool-calling loop against `tools` (a list of
    @tool-decorated callables). Returns the list of tool names that were
    actually called, in order.

    The tools' real, structured results live in whatever `context` dict
    they were built with (app.tools.factory.make_tools) — the caller
    reads results from there, never from the LLM's own text.
    """

    tools_by_name = {t.name: t for t in tools}
    bound_llm = get_llm().bind_tools(tools)

    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=human_prompt),
    ]

    called = []

    for iteration in range(MAX_TOOL_ITERATIONS):
        response = bound_llm.invoke(messages)
        messages.append(response)

        tool_calls = getattr(response, "tool_calls", None) or []

        if not tool_calls:
            logger.info(
                "session=%s agent stopped after %d tool call(s), no further calls requested",
                session_id, len(called),
            )
            break

        for call in tool_calls:
            name = call["name"]
            args = call.get("args") or {}

            logger.info(
                "session=%s agent chose tool=%s args=%s (iteration=%d)",
                session_id, name, args, iteration,
            )

            tool_fn = tools_by_name.get(name)

            if not tool_fn:
                logger.warning("session=%s agent requested unknown tool=%s", session_id, name)
                result_text = f"Unknown tool: {name}"
            else:
                try:
                    result_text = tool_fn.invoke(args)
                except Exception:
                    logger.exception("session=%s tool=%s raised", session_id, name)
                    result_text = f"Tool {name} failed."

            called.append(name)

            messages.append(
                ToolMessage(content=str(result_text), tool_call_id=call["id"])
            )
    else:
        logger.warning(
            "session=%s agent hit MAX_TOOL_ITERATIONS=%d without stopping on its own",
            session_id, MAX_TOOL_ITERATIONS,
        )

    return called
