from app.graph.workflow import travel_graph

result = travel_graph.invoke(
    {
        "user_input": "I need an electrician in Matara tomorrow at 10 AM"
    }
)

print(result["response"])