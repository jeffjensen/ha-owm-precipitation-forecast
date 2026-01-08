from __future__ import annotations

from typing import Any


def _normalize(value: float | list[Any] | None) -> list[float]:
    if value is None:
        return []
    if isinstance(value, list):
        return [float(v) for v in value]
    return [float(value)]


def parse_precip(data: dict[str, Any]) -> dict[str, float]:
    rain = sum(_normalize(data.get("rain")))
    snow = sum(_normalize(data.get("snow")))
    return {"rain": rain, "snow": snow}
