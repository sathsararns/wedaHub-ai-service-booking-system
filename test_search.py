from app.agents.search_agent import search_agent
from app.models.requirements import Requirement

req = Requirement(

    service="Photographer",

    location="Galle",

)

providers = search_agent(req)

print(providers)