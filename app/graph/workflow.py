from langgraph.graph import StateGraph
from langgraph.graph import END

from app.state import GraphState

from app.graph.requirement_node import requirement_node
from app.graph.planner_node import planner_node
from app.graph.search_node import search_node
from app.graph.recommendation_node import recommendation_node
from app.graph.response_node import response_node
from app.graph.booking_node import booking_node

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
    "booking",
    booking_node
)

graph.add_node(
    "response",
    response_node
)

# Set entry point
graph.set_entry_point("requirements")

# Add edges - Sequential flow
graph.add_edge(
    "requirements",
    "planner"
)

graph.add_edge(
    "planner",
    "search"
)

graph.add_edge(
    "search",
    "recommend"
)

graph.add_edge(
    "recommend",
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