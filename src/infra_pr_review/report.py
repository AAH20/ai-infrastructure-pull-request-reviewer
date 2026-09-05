from __future__ import annotations

from .models import Review


def markdown(review: Review) -> str:
    finding_rows = "\n".join(
        f"| {item.severity.upper()} | {item.source} | {item.finding_id} | {item.title} | {item.resource or '—'} |"
        for item in review.findings
    ) or "| — | — | — | No findings | — |"
    services = ", ".join(review.affected_services) or "None mapped"
    resources = "\n".join(f"- `{item}`" for item in review.affected_resources) or "- None"
    recommendations = "\n".join(f"- {item}" for item in review.recommendations)
    return f"""# Infrastructure Change Decision: {review.decision}

**Score:** {review.score:.1f}/100  
**Confidence:** {review.confidence:.1f}%  
**Evidence class:** {review.evidence_class}  
**Integrity receipt:** `{review.receipt}`

## Business impact

- Affected services: {services}
- Monthly cloud-cost delta: ${review.metrics['monthly_cost_delta_usd']:,.2f}
- Modeled revenue exposure: ${review.metrics['modeled_revenue_exposure_usd']:,.2f}
- Evidence coverage: {review.metrics['evidence_coverage_percent']:.1f}%

## Findings

| Severity | Source | ID | Finding | Resource |
|---|---|---|---|---|
{finding_rows}

## Affected dependency closure

{resources}

## Required review actions

{recommendations}

> Financial values are scenario assumptions, not measured customer outcomes. The receipt proves serialized-output integrity, not identity or non-repudiation.
"""

