from app.graph.workflow import travel_graph

result = travel_graph.invoke(

    {

        "user_input": "Book 1 tomorrow 10 AM",

        "requirements": {

            "service": "Electrician",

            "location": "Matara",

            "date": "tomorrow",

            "time": "10 AM"

        },

        "providers": [

            {

                "_id": "6860xxxxxxxx",

                "firstName": "Tommy",

                "lastName": "Perera"

            }

        ],

        "booking": {

            "provider_index": 0,

            "date": "tomorrow",

            "time": "10 AM"

        }

    }

)

print(

    result["response"]

)