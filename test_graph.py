from app.graph.workflow import travel_graph

result = travel_graph.invoke({

    "user_input":"I need an electrician in Matara tomorrow"

})

print(result["response"])