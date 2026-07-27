from app.graph.workflow import travel_graph

result = travel_graph.invoke(

    {

        "user_input": "Book 1 tomorrow 10 AM"

    }

)

print(

    result["response"]

)