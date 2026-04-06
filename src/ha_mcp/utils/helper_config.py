"""Utility helpers for input helper configuration validation."""

from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)


def validate_helper_field(field_name: str, value: Any, required: bool = False) -> bool:
    """Validate a single helper configuration field."""
    if required and not value:
        logger.warning(f"Required field '{field_name}' is missing or empty")
        return False
    return True


def build_update_payload(
    helper_type: str,
    helper_id: str,
    name: str | None = None,
    icon: str | None = None,
    options: list[str] | None = None,
    min_value: float | None = None,
    max_value: float | None = None,
) -> dict[str, Any] | None:
    """Build WebSocket update payload for a storage-based input helper.

    Returns the update message dict, or None if validation fails.
    """
    if not helper_id:
        return {"error": "helper_id is required", "success": False}

    payload: dict[str, Any] = {
        "type": f"{helper_type}/update",
        f"{helper_type}_id": helper_id,
    }

    if name:
        payload["name"] = name
    if icon:
        payload["icon"] = icon

    if helper_type == "input_select":
        if options:
            payload["options"] = options

    elif helper_type == "input_number":
        if min_value is not None:
            payload["min"] = min_value
        if max_value is not None:
            payload["max"] = max_value

    return payload


def read_helper_schema(schema_path: str) -> dict[str, Any]:
    """Load helper schema definition from a JSON file."""
    with open(schema_path) as f:
        import json
        return json.load(f)


def apply_defaults(
    config: dict[str, Any],
    defaults: dict[str, Any],
) -> dict[str, Any]:
    """Merge defaults into a config dict, preserving existing values."""
    result = dict(defaults)
    for key, value in config.items():
        if value:
            result[key] = value
    return result


def fetch_and_update_helpers(
    client: Any,
    helper_ids: list[str],
    updates: dict[str, Any],
) -> list[dict[str, Any]]:
    """Apply the same update to multiple helpers.

    Returns a list of results.
    """
    results = []
    for helper_id in helper_ids:
        try:
            result = client.update_helper(helper_id, updates)
            results.append(result)
        except Exception as e:
            logger.error(f"Failed to update helper {helper_id}: {e}")
            results.append({"error": str(e), "success": False})
    return results
