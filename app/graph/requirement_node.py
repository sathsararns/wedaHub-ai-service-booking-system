from app.agents.requirements_agent import requirements_agent

# ==========================================================
# Sri Lankan Locations
# ==========================================================

LOCATIONS = {
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
    "kegalle": "Kegalle",
}


def requirement_node(state):

    print("\n========== REQUIREMENT NODE ==========")

    message = state.get("user_input", "").strip()

    if not message:
        return state

    lower = message.lower()

    print("MESSAGE :", message)

    requirements = dict(
        state.get("requirements") or {}
    )

    booking = state.get("booking") or {}

    # =====================================================
    # Skip only pure "Book X"
    # =====================================================

    if lower.startswith("book"):

        words = lower.split()

        if (
            len(words) == 2
            and words[1].isdigit()
        ):
            print("Provider selection detected.")
            state["requirements"] = requirements
            return state

    # =====================================================
    # LLM Extraction
    # =====================================================

    extracted = {}

    try:

        result = requirements_agent.invoke(
            {
                "input": message
            }
        )

        if hasattr(result, "model_dump"):
            extracted = result.model_dump()

        elif hasattr(result, "dict"):
            extracted = result.dict()

        print("LLM :", extracted)

    except Exception as e:

        print("Requirement Agent Error :", e)

    # =====================================================
    # Merge
    # =====================================================

    for key, value in extracted.items():

        if value is None:
            continue

        if isinstance(value, str):

            value = value.strip()

            if value == "":
                continue

        requirements[key] = value

    # =====================================================
    # Manual Location
    # =====================================================

    for key, city in LOCATIONS.items():

        if key in lower:

            requirements["location"] = city
            break

    # =====================================================
    # Service Detection
    # =====================================================

    electrician_words = [
        "electrician",
        "electric",
        "wire",
        "wiring",
        "socket",
        "switch",
        "light",
        "lighting",
        "fan",
        "ceiling fan",
        "power",
        "plug",
        "breaker",
        "fuse",
    ]

    plumber_words = [
        "plumber",
        "pipe",
        "tap",
        "water",
        "sink",
        "toilet",
        "drain",
        "leak",
    ]

    carpenter_words = [
        "carpenter",
        "door",
        "window",
        "cupboard",
        "wood",
        "table",
        "chair",
    ]

    cleaner_words = [
        "clean",
        "cleaner",
        "cleaning",
    ]

    if (
        not requirements.get("service")
    ):

        if any(
            word in lower
            for word in electrician_words
        ):
            requirements["service"] = "Electrician"

        elif any(
            word in lower
            for word in plumber_words
        ):
            requirements["service"] = "Plumber"

        elif any(
            word in lower
            for word in carpenter_words
        ):
            requirements["service"] = "Carpenter"

        elif any(
            word in lower
            for word in cleaner_words
        ):
            requirements["service"] = "Cleaner"

    # =====================================================
    # Description
    # =====================================================

    description_words = [
        "repair",
        "fix",
        "replace",
        "install",
        "broken",
        "damage",
        "issue",
        "problem",
        "maintenance",
        "not working",
    ]

    if any(
        word in lower
        for word in description_words
    ):

        requirements["description"] = message

    # =====================================================
    # Booking Sync
    # =====================================================

    if booking:

        booking.setdefault(
            "service",
            requirements.get("service")
        )

        booking.setdefault(
            "city",
            requirements.get("location")
        )

        if (
            requirements.get("description")
            and not booking.get("description")
        ):
            booking["description"] = requirements["description"]

        state["booking"] = booking

    # =====================================================
    # Save
    # =====================================================

    state["requirements"] = requirements

    print("\nFINAL REQUIREMENTS")
    print(requirements)

    return state