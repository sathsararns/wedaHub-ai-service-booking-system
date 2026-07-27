from app.agents.booking_agent import booking_agent

result = booking_agent.invoke({
    "input": "Book provider 1 tomorrow at 10 AM"
})

print(result)