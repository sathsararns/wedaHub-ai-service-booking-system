from __future__ import annotations

import logging
from copy import deepcopy
from typing import Any, Dict

from app.agents.requirements_agent import get_requirements_agent
from app.core.tracing import trace_node
from app.services.service_categories import normalize_service

logger = logging.getLogger(__name__)


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


@trace_node("requirement_node")
def requirement_node(state):
    session_id = state.get("session_id")
    user_input = (state.get("user_input") or "").strip()

    logger.info("session=%s input=%r", session_id, user_input)

    # Keep previous requirements and merge new values into them
    previous_requirements = state.get("requirements") or {}
    booking = dict(state.get("booking") or {})
    selected_provider = next(
        (provider for provider in (state.get("providers") or [])
         if provider.get("_id") == booking.get("provider_id")),
        {},
    ) if booking.get("provider_id") else {}
    locked_service = normalize_service(
        selected_provider.get("category") or booking.get("service")
        or previous_requirements.get("service")
    ) if booking.get("provider_id") else None

    try:
        result = get_requirements_agent().invoke({
            "input": user_input,
            "selected_service": locked_service or "",
        })
        extracted = (
            result.model_dump()
            if hasattr(result, "model_dump")
            else dict(result)
        )
    except Exception:
        logger.exception("session=%s requirements extraction failed", session_id)
        extracted = {}

    logger.debug("session=%s extracted=%s", session_id, extracted)

    if locked_service:
        # Descriptions fill booking details; the chosen provider fixes its category.
        # Enforce this even when the model suggests a different kind of service.
        extracted.pop("service_type", None)
        extracted["service"] = locked_service
        booking["service"] = locked_service
        state["booking"] = booking

    merged_requirements = merge_requirements(previous_requirements, extracted)

    previous_service = normalize_service(
        selected_provider.get("category") or booking.get("service")
        or previous_requirements.get("service")
    )
    current_service = merged_requirements.get("service")
    state["service_change"] = None
    if not locked_service and previous_service and current_service and previous_service != current_service:
        # A new category needs a new provider; never relabel the old selection.
        state["service_change"] = {"previous": previous_service, "current": current_service}
        state["booking"] = {}
        state["booking_confirmed"] = False
        state["booking_created"] = False
        state["booking_result"] = None
        state["booking_status"] = None
        state["created_booking"] = None
        state["booking_card"] = None
        state["providers"] = []
        state["recommendations"] = {}
        state["recommended_providers"] = []

    state["requirements"] = merged_requirements

    logger.info("session=%s final_requirements=%s", session_id, merged_requirements)

    return state
