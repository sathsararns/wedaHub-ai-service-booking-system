from langgraph.graph import StateGraph
from langgraph.graph import END

from app.state import GraphState

from app.graph.requirement_node import requirement_node
from app.graph.planner_node import planner_node
from app.graph.search_node import search_node
from app.graph.recommendation_node import recommendation_node
from app.graph.response_node import response_node
from app.graph.booking_agent_node import booking_agent_node
from app.graph.booking_node import booking_node
from app.graph.router import planner_router

graph = StateGraph(GraphState)

# Add nodes
graph.add_node(
    "requirements",
    requirement_node
)

graph.add_node(
    "planner",
    planner_node
)

graph.add_node(
    "search",
    search_node
)

graph.add_node(
    "recommend",
    recommendation_node
)

graph.add_node(
    "booking_agent",
    booking_agent_node
)

graph.add_node(
    "booking",
    booking_node
)

graph.add_node(
    "response",
    response_node
)

# Set entry point
graph.set_entry_point("requirements")

# Add edges
graph.add_edge(
    "requirements",
    "planner"
)

# Conditional edge from planner based on router logic
graph.add_conditional_edges(
    "planner",
    planner_router,
    {
        "search": "search",
        "booking_agent": "booking_agent",
        "response": "response"
    }
)

graph.add_edge(
    "search",
    "recommend"
)

graph.add_edge(
    "recommend",
    "response"
)

graph.add_edge(
    "booking_agent",
    "booking"
)

graph.add_edge(
    "booking",
    "response"
)

graph.add_edge(
    "response",
    END
)

# Compile the graph
travel_graph = graph.compile()