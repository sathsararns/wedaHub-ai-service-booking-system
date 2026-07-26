from app.core.llm import llm

response = llm.invoke("Say hello")

print(response.content)