from langgraph.graph import StateGraph, END

from app.state import GraphState

from app.graph.requirement_node import requirement_node
from app.graph.planner_node import planner_node
from app.graph.search_node import search_node
from app.graph.recommendation_node import recommendation_node
from app.graph.booking_agent_node import booking_agent_node
from app.graph.booking_node import booking_node
from app.graph.booking_status_node import booking_status_node
from app.graph.response_node import response_node

from app.graph.router import (
    router,
    booking_router,
)

workflow = StateGraph(GraphState)

# -----------------------------
# Nodes
# -----------------------------

workflow.add_node("requirements", requirement_node)
workflow.add_node("planner", planner_node)

workflow.add_node("search", search_node)
workflow.add_node("recommend", recommendation_node)

workflow.add_node("booking_agent", booking_agent_node)
workflow.add_node("booking", booking_node)

workflow.add_node("booking_status", booking_status_node)

workflow.add_node("response", response_node)

# -----------------------------
# Entry
# -----------------------------

workflow.set_entry_point("requirements")

# -----------------------------
# Requirements -> Planner
# -----------------------------

workflow.add_edge(
    "requirements",
    "planner",
)

# -----------------------------
# Planner Router
# -----------------------------

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

# -----------------------------
# Recommendation Flow
# -----------------------------

workflow.add_edge(
    "search",
    "recommend",
)

workflow.add_edge(
    "recommend",
    "response",
)

# -----------------------------
# Booking Flow
# -----------------------------

workflow.add_conditional_edges(
    "booking_agent",
    booking_router,
    {
        "booking": "booking",
        "response": "response",
    },
)

workflow.add_edge(
    "booking",
    "response",
)

# -----------------------------
# Booking Status Flow
# -----------------------------

workflow.add_edge(
    "booking_status",
    "response",
)

# -----------------------------
# Finish
# -----------------------------

workflow.add_edge(
    "response",
    END,
)

graph = workflow.compile()