from __future__ import annotations

import hashlib
import json
from typing import Any

from .adapters import changebench_findings, checkov_findings
from .graph import impact_closure
from .models import Finding, Review


class ReviewContractError(ValueError):
    pass


def _required(document: dict[str, Any], fields: tuple[str, ...], label: str) -> None:
    missing = [field for field in fields if field not in document]
    if missing:
        raise ReviewContractError(f"{label} missing required fields: {', '.join(missing)}")


def review(bundle: dict[str, Any]) -> Review:
    _required(bundle, ("plan", "business_context", "checkov", "infracost", "changebench"), "bundle")
    plan = bundle["plan"]
    context = bundle["business_context"]
    _required(plan, ("changes", "dependencies"), "plan")
    _required(context, ("revenue_per_hour_usd", "maximum_monthly_cost_increase_usd"), "business_context")

    changed = {item["resource"] for item in plan["changes"]}
    resources, services = impact_closure(plan, changed)
    findings = checkov_findings(bundle["checkov"]) + changebench_findings(bundle["changebench"])

    monthly_delta = float(bundle["infracost"].get("monthly_cost_delta_usd", 0))
    cost_limit = float(context["maximum_monthly_cost_increase_usd"])
    if monthly_delta > cost_limit:
        findings.append(Finding(
            source="infracost",
            finding_id="COST-BUDGET",
            severity="medium",
            title=f"Monthly cost increase ${monthly_delta:,.2f} exceeds ${cost_limit:,.2f} budget",
            blocking=False,
            evidence=bundle["infracost"].get("source", "normalized estimate"),
        ))

    rollback_present = bool(plan.get("rollback", {}).get("steps"))
    if not rollback_present:
        findings.append(Finding(
            source="reviewer",
            finding_id="ROLLBACK-REQUIRED",
            severity="high",
            title="No machine-readable rollback procedure was supplied",
            blocking=True,
        ))

    blocking = [finding for finding in findings if finding.blocking]
    severity_penalty = {"critical": 30, "high": 20, "medium": 8, "low": 2}
    score = max(0.0, 100.0 - sum(severity_penalty.get(item.severity, 5) for item in findings))
    decision = "BLOCK" if blocking else ("REVIEW_REQUIRED" if findings else "APPROVE")
    evidence_items = sum(bool(item.evidence) for item in findings)
    evidence_coverage = 100.0 if not findings else round(100 * evidence_items / len(findings), 2)
    confidence = round(min(99.0, 60 + evidence_coverage * 0.3 + min(len(resources), 9)), 2)
    revenue_exposure = float(context["revenue_per_hour_usd"]) * float(context.get("modeled_outage_hours", 1))

    recommendations = {
        "Resolve all blocking findings before merge" if blocking else "Review non-blocking findings against the approved exception process",
        "Retain normalized source outputs with the final review receipt",
    }
    if rollback_present:
        recommendations.add("Execute the declared rollback and post-change verification in a disposable environment")
    else:
        recommendations.add("Define and test a machine-readable rollback before merge")

    result = Review(
        decision=decision,
        score=score,
        confidence=confidence,
        findings=findings,
        affected_resources=resources,
        affected_services=services,
        metrics={
            "monthly_cost_delta_usd": monthly_delta,
            "modeled_revenue_exposure_usd": revenue_exposure,
            "evidence_coverage_percent": evidence_coverage,
            "blocking_findings": float(len(blocking)),
        },
        recommendations=sorted(recommendations),
        evidence_class=bundle.get("evidence_class", "simulated"),
    )
    canonical = json.dumps(result.as_dict() | {"receipt": ""}, sort_keys=True, separators=(",", ":"))
    result.receipt = "sha256:" + hashlib.sha256(canonical.encode()).hexdigest()
    return result
