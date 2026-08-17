from app.agents.requirements_agent import requirements_agent


def requirement_node(state):
    """
    Extract booking requirements while preserving previous values.
    """

    # --------------------------------------------------
    # Current message
    # --------------------------------------------------
    message = state.get("user_input", "").strip()
    lower_message = message.lower()

    # --------------------------------------------------
    # Current booking state
    # --------------------------------------------------
    booking = state.get("booking") or {}

    # --------------------------------------------------
    # Don't modify requirements during booking flow
    # --------------------------------------------------
    if booking.get("provider_id"):
        print("Booking flow detected. Skipping requirement extraction.")
        return state

    # --------------------------------------------------
    # Skip extraction when user is selecting provider
    # Example:
    # Book 1
    # Book 2
    # --------------------------------------------------
    if lower_message.startswith("book"):
        print("Booking command detected. Skipping requirement extraction.")
        return state

    # --------------------------------------------------
    # Existing requirements
    # --------------------------------------------------
    requirements = state.get("requirements", {}).copy()

    print("\n========== OLD REQUIREMENTS ==========")
    print(requirements)

    # --------------------------------------------------
    # Extract with LLM
    # --------------------------------------------------
    try:
        result = requirements_agent.invoke(
            {
                "input": message
            }
        )

        extracted = result.model_dump()

        print("\n========== REQUIREMENT AGENT ==========")
        print(extracted)

    except Exception as e:
        print("\n========== REQUIREMENT AGENT ERROR ==========")
        print(e)
        extracted = {}

    # --------------------------------------------------
    # Merge extracted values
    # --------------------------------------------------
    for key, value in extracted.items():
        if value not in (None, "", []):
            requirements[key] = value

    # --------------------------------------------------
    # Location fallback
    # --------------------------------------------------
    locations = {
        "colombo": "Colombo",
        "galle": "Galle",
        "matara": "Matara",
        "kandy": "Kandy",
        "jaffna": "Jaffna",
        "kurunegala": "Kurunegala",
        "negombo": "Negombo",
        "anuradhapura": "Anuradhapura",
        "badulla": "Badulla",
        "hambantota": "Hambantota",
        "gampaha": "Gampaha",
        "kalutara": "Kalutara",
        "ratnapura": "Ratnapura",
        "trincomalee": "Trincomalee",
        "batticaloa": "Batticaloa",
        "ampara": "Ampara",
        "monaragala": "Monaragala",
        "nuwara eliya": "Nuwara Eliya",
        "polonnaruwa": "Polonnaruwa",
        "matale": "Matale",
        "puttalam": "Puttalam",
        "vavuniya": "Vavuniya",
        "kilinochchi": "Kilinochchi",
        "mannar": "Mannar",
        "mullaitivu": "Mullaitivu",
        "kegalle": "Kegalle"
    }

    if lower_message in locations:
        requirements["location"] = locations[lower_message]

    # --------------------------------------------------
    # Save merged requirements
    # --------------------------------------------------
    state["requirements"] = requirements

    print("\n========== FINAL REQUIREMENTS ==========")
    print(state["requirements"])

    return state