from langgraph.graph import StateGraph
from langgraph.graph import END

from app.state import GraphState

from app.graph.requirement_node import requirement_node
from app.graph.planner_node import planner_node
from app.graph.search_node import search_node
from app.graph.recommendation_node import recommendation_node
from app.graph.response_node import response_node


graph = StateGraph(GraphState)

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
    "recommendation",
    recommendation_node
)

graph.add_node(
    "response",
    response_node
)

graph.set_entry_point("requirements")

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
    "recommendation"
)

graph.add_edge(
    "recommendation",
    "response"
)

graph.add_edge(
    "response",
    END
)

travel_graph = graph.compile()