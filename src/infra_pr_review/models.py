from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass(frozen=True)
class Finding:
    source: str
    finding_id: str
    severity: str
    title: str
    resource: str = ""
    blocking: bool = False
    evidence: str = ""


@dataclass
class Review:
    decision: str
    score: float
    confidence: float
    findings: list[Finding]
    affected_resources: list[str]
    affected_services: list[str]
    metrics: dict[str, float]
    recommendations: list[str]
    evidence_class: str = "simulated"
    receipt: str = ""

    def as_dict(self) -> dict[str, Any]:
        return {
            "decision": self.decision,
            "score": self.score,
            "confidence": self.confidence,
            "findings": [asdict(item) for item in self.findings],
            "affected_resources": self.affected_resources,
            "affected_services": self.affected_services,
            "metrics": self.metrics,
            "recommendations": self.recommendations,
            "evidence_class": self.evidence_class,
            "receipt": self.receipt,
        }

