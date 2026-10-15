"""Shared service names for extraction and provider-category matching."""
from typing import Any


SERVICE_MAP = {
    "electrician": "Electrician",
    "electrician service": "Electrician",
    "plumber": "Plumbing",
    "plumbing": "Plumbing",
    "ac repair": "AC Repair",
    "air conditioner repair": "AC Repair",
    "ac service": "AC Repair",
    "ac service & repair": "AC Repair",
    "cleaner": "Home Cleaning",
    "home cleaning": "Home Cleaning",
    "cleaning": "Home Cleaning",
    "pest control": "Pest Control",
    "carpenter": "Carpenter",
    "carpentry": "Carpenter",
    "painter": "Painting",
    "painting": "Painting",
    "appliance repair": "Appliance Repair",
}


def normalize_service(value: Any) -> Any:
    if not isinstance(value, str):
        return value
    cleaned = value.strip()
    if not cleaned:
        return cleaned
    if cleaned.lower() in SERVICE_MAP:
        return SERVICE_MAP[cleaned.lower()]
    if cleaned.isupper():
        return cleaned
    return cleaned[0].upper() + cleaned[1:]
