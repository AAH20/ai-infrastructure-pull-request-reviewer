import unittest
import json
from pathlib import Path

from infra_pr_review.engine import ReviewContractError, review
from infra_pr_review.report import markdown


ROOT = Path(__file__).parents[1]


def fixture(name):
    return json.loads((ROOT / "examples" / name).read_text(encoding="utf-8"))


class ReviewTests(unittest.TestCase):
    def test_safe_change_is_approved(self):
        result = review(fixture("azure-private-link-safe.json"))
        self.assertEqual(result.decision, "APPROVE")
        self.assertEqual(result.score, 100)
        self.assertIn("Customer Checkout API", result.affected_services)

    def test_risky_change_is_blocked(self):
        result = review(fixture("azure-network-risky.json"))
        self.assertEqual(result.decision, "BLOCK")
        self.assertGreaterEqual(result.metrics["blocking_findings"], 2)
        self.assertIn("Customer Checkout API", result.affected_services)
        self.assertIn("Define and test a machine-readable rollback before merge", result.recommendations)

    def test_receipt_is_deterministic_and_tamper_evident(self):
        bundle = fixture("azure-private-link-safe.json")
        first = review(bundle).receipt
        self.assertEqual(first, review(bundle).receipt)
        bundle["infracost"]["monthly_cost_delta_usd"] = 13
        self.assertNotEqual(first, review(bundle).receipt)

    def test_missing_contract_is_rejected(self):
        with self.assertRaisesRegex(ReviewContractError, "business_context"):
            review({"plan": {}})

    def test_report_has_decision_and_business_impact(self):
        report = markdown(review(fixture("azure-network-risky.json")))
        self.assertIn("Infrastructure Change Decision: BLOCK", report)
        self.assertIn("Modeled revenue exposure: $36,000.00", report)
        self.assertIn("Management port exposed", report)


if __name__ == "__main__":
    unittest.main()
