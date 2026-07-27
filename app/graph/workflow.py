from langgraph.graph import StateGraph
from langgraph.graph import END

from app.state import GraphState

from app.graph.requirement_node import requirement_node
from app.graph.planner_node import planner_node
from app.graph.search_node import search_node
from app.graph.recommendation_node import recommendation_node  # ✅ Correct import
from app.graph.response_node import response_node


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
    "recommend",  # ✅ Node name changed to "recommend"
    recommendation_node  # ✅ Uses the imported function
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

graph.add_edge(
    "planner",
    "search"
)

graph.add_edge(
    "search",
    "recommend"  # ✅ Edge from search → recommend
)

graph.add_edge(
    "recommend",  # ✅ Edge from recommend → response
    "response"
)

graph.add_edge(
    "response",
    END
)

# Compile the graph
travel_graph = graph.compile()