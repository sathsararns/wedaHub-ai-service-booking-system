from langgraph.graph import StateGraph, END

from app.graph.state import GraphState

from app.graph.nodes.requirement_node import requirement_node
from app.graph.nodes.planner_node import planner_node
from app.graph.nodes.search_agent_node import search_agent_node

from app.graph.nodes.booking_agent_node import booking_agent_node
from app.graph.nodes.booking_confirmation_node import booking_confirmation_node
from app.graph.nodes.booking_create_node import booking_create_node

from app.graph.nodes.booking_status_node import booking_status_node
from app.graph.nodes.response_node import response_node

from app.graph.router import (
    router,
    booking_router,
)

workflow = StateGraph(GraphState)

# =========================================================
# Nodes
# =========================================================

workflow.add_node(
    "requirements",
    requirement_node,
)

workflow.add_node(
    "planner",
    planner_node,
)

workflow.add_node(
    "search",
    search_agent_node,
)

workflow.add_node(
    "booking_agent",
    booking_agent_node,
)

workflow.add_node(
    "booking_confirmation",
    booking_confirmation_node,
)

workflow.add_node(
    "booking_create",
    booking_create_node,
)

workflow.add_node(
    "booking_status",
    booking_status_node,
)

workflow.add_node(
    "response",
    response_node,
)

# =========================================================
# Entry
# =========================================================

workflow.set_entry_point("requirements")

# =========================================================
# Requirements -> Planner
# =========================================================

workflow.add_edge(
    "requirements",
    "planner",
)

# =========================================================
# Planner Router
# =========================================================

workflow.add_conditional_edges(
    "planner",
    router,
    {
        "search": "search",
        "booking": "booking_agent",
        "booking_status": "booking_status",
        "response": "response",
    },
)

# =========================================================
# Search Flow
# =========================================================
# search_agent_node itself decides (via tool-calling) whether to call
# search_providers only, or search_providers then recommend_providers —
# both happen inside that one node now, not as separate graph edges.

workflow.add_edge(
    "search",
    "response",
)

# =========================================================
# Booking Agent
# =========================================================

workflow.add_conditional_edges(
    "booking_agent",
    booking_router,
    {
        "confirm": "booking_confirmation",
        "response": "response",
    },
)

# =========================================================
# Confirmation Router
# =========================================================

def confirmation_router(state):
    """
    booking_confirmation -> booking_create / response
    """

    if state.get("booking_confirmed"):
        return "create"

    return "response"


workflow.add_conditional_edges(
    "booking_confirmation",
    confirmation_router,
    {
        "create": "booking_create",
        "response": "response",
    },
)

# =========================================================
# Booking Create
# =========================================================

workflow.add_edge(
    "booking_create",
    "response",
)

# =========================================================
# Booking Status
# =========================================================

workflow.add_edge(
    "booking_status",
    "response",
)

# =========================================================
# Finish
# =========================================================

workflow.add_edge(
    "response",
    END,
)

graph = workflow.compile()
