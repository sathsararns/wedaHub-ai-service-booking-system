from app.agents.recommendation_agent import recommendation_agent

requirements = """
Wedding Photographer
Location : Galle
"""

providers = """
[
{
"id":"1",
"business_name":"ABC Studio",
"rating":4.9,
"price":25000
},
{
"id":"2",
"business_name":"Photo House",
"rating":4.7,
"price":20000
},
{
"id":"3",
"business_name":"Dream Lens",
"rating":5.0,
"price":28000
}
]
"""

response = recommendation_agent.invoke({

"requirements":requirements,

"providers":providers

})

print(response)