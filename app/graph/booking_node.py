import requests
from app.config import EXPRESS_API

def booking_node(state):
    booking = state["booking"]
    providers = state["providers"]
    provider = providers[booking["provider_index"]]

    try:
        response = requests.post(
            f"{EXPRESS_API}/bookings/ai-booking",
            json={
                "providerId": provider["_id"],
                "date": booking["date"],
                "time": booking["time"]
            },
            timeout=20
        )
        response.raise_for_status()
        state["booking_result"] = response.json()
        
    except requests.exceptions.RequestException as e:
        state["booking_error"] = str(e)
        state["booking_result"] = None
        
    return state