from __future__ import annotations

from copy import deepcopy
from typing import Any, Dict

from app.agents.requirements_agent import requirements_agent


SERVICE_MAP = {
    "electrician": "Electrician",
    "electrician service": "Electrician",
    "plumber": "Plumbing",
    "plumbing": "Plumbing",
    "ac repair": "AC Repair",
    "air conditioner repair": "AC Repair",
    "ac service": "AC Repair",
    "ac service & repair": "AC Repair",
    "home cleaning": "Home Cleaning",
    "cleaning": "Home Cleaning",
    "pest control": "Pest Control",
    "carpentry": "Carpentry",
    "painting": "Painting",
    "appliance repair": "Appliance Repair",
}


def normalize_service(value: Any) -> Any:
    if not isinstance(value, str):
        return value

    cleaned = value.strip()
    if not cleaned:
        return cleaned

    lower = cleaned.lower()
    if lower in SERVICE_MAP:
        return SERVICE_MAP[lower]

    # Keep acronym-like words intact (AC Repair, TV Repair, etc.)
    if cleaned.isupper():
        return cleaned

    return cleaned[0].upper() + cleaned[1:]


def normalize_location(value: Any) -> Any:
    if not isinstance(value, str):
        return value
    cleaned = value.strip()
    if not cleaned:
        return cleaned
    return cleaned.title()


def merge_requirements(
    previous: Dict[str, Any] | None,
    extracted: Dict[str, Any] | None,
) -> Dict[str, Any]:
    previous = previous or {}
    extracted = extracted or {}

    merged = deepcopy(previous)

    for key, value in extracted.items():
        if key == "service_type":
            key = "service"

        if isinstance(value, str):
            value = value.strip()

        if value in (None, "", [], {}):
            continue

        merged[key] = value

    if "service" in merged:
        merged["service"] = normalize_service(merged["service"])

    if "location" in merged:
        merged["location"] = normalize_location(merged["location"])

    if isinstance(merged.get("date"), str):
        merged["date"] = merged["date"].strip()

    if isinstance(merged.get("description"), str):
        merged["description"] = merged["description"].strip()

    # remove empties
    merged = {
        k: v for k, v in merged.items()
        if v not in (None, "", [], {})
    }

    return merged


def requirement_node(state):
    print("\n========== REQUIREMENT NODE ==========")

    user_input = (state.get("user_input") or "").strip()
    print("MESSAGE :", user_input)

    # Keep previous requirements and merge new values into them
    previous_requirements = state.get("requirements") or {}

    try:
        result = requirements_agent.invoke({"input": user_input})
        extracted = (
            result.model_dump()
            if hasattr(result, "model_dump")
            else dict(result)
        )
    except Exception as e:
        print("Requirements Agent Error:", e)
        extracted = {}

    print("LLM :", extracted)

    merged_requirements = merge_requirements(previous_requirements, extracted)

    state["requirements"] = merged_requirements

    print("\nFINAL REQUIREMENTS")
    print(state["requirements"])

    return state