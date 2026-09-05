from __future__ import annotations

from collections import defaultdict, deque
from typing import Any


def impact_closure(plan: dict[str, Any], changed: set[str]) -> tuple[list[str], list[str]]:
    """Return deterministic downstream resource and business-service impact."""
    edges: dict[str, list[str]] = defaultdict(list)
    for edge in plan.get("dependencies", []):
        edges[edge["from"]].append(edge["to"])

    seen = set(changed)
    queue = deque(sorted(changed))
    while queue:
        node = queue.popleft()
        for child in sorted(edges[node]):
            if child not in seen:
                seen.add(child)
                queue.append(child)

    services = sorted(
        service["name"]
        for service in plan.get("business_services", [])
        if service.get("resource") in seen
    )
    return sorted(seen), services

