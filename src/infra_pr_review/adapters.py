from __future__ import annotations

from typing import Any

from .models import Finding


SEVERITY_BLOCK = {"critical", "high"}


def checkov_findings(document: dict[str, Any]) -> list[Finding]:
    results = []
    for item in document.get("failed_checks", []):
        severity = item.get("severity", "medium").lower()
        results.append(Finding(
            source="checkov",
            finding_id=item["check_id"],
            severity=severity,
            title=item["name"],
            resource=item.get("resource", ""),
            blocking=severity in SEVERITY_BLOCK,
            evidence=item.get("file", ""),
        ))
    return results


def changebench_findings(document: dict[str, Any]) -> list[Finding]:
    results = []
    for item in document.get("checks", []):
        if not item.get("passed", False):
            dimension = item.get("dimension", "correctness")
            results.append(Finding(
                source="changebench",
                finding_id=item["check_id"],
                severity="high" if dimension == "safety" else "medium",
                title=item["message"],
                blocking=dimension == "safety",
                evidence=document.get("receipt", ""),
            ))
    return results

