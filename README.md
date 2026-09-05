# AI Infrastructure Pull Request Reviewer

**Evidence-driven pull request decisions for Terraform, OpenTofu, Azure, Kubernetes and network infrastructure.**

[![CI](https://github.com/AAH20/ai-infrastructure-pull-request-reviewer/actions/workflows/ci.yml/badge.svg)](https://github.com/AAH20/ai-infrastructure-pull-request-reviewer/actions/workflows/ci.yml)
[![License](https://img.shields.io/badge/license-Apache--2.0-blue.svg)](LICENSE)
[![Mutation](https://img.shields.io/badge/production%20mutation-none-green.svg)](#evidence-and-safety-boundary)

Security scanners find misconfigurations. FinOps tools estimate cost. Policy engines evaluate rules. This project combines normalized results with infrastructure dependencies, business services, SLO assumptions and [ChangeBench](https://github.com/AAH20/agentic-infrastructure-change-benchmark) receipts to answer the merge question:

> Should this infrastructure change be accepted, what revenue-critical systems could it affect, and how will it be verified and reversed?

## Current release

Version 0.1 is an executable, dependency-light review kernel—not a hosted GitHub App. It implements:

- deterministic `APPROVE`, `REVIEW_REQUIRED` and `BLOCK` decisions;
- downstream dependency and business-service impact analysis;
- normalized Checkov, Infracost and ChangeBench evidence ingestion;
- hard blocking for high-severity findings and missing rollback;
- cost-budget and modeled revenue-exposure reporting;
- evidence coverage and deterministic SHA-256 receipts;
- CLI, composite GitHub Action, CI, safe/risky fixtures and automated tests.

Native tool execution, GitHub webhooks, Azure deployment and LLM explanations are explicitly documented roadmap boundaries.

## Architecture

```text
Infrastructure pull request
           │
           ▼
  Normalized change plan
           │
           ▼
Dependency + network impact graph
           │
   ┌───────┼─────────┬────────────┐
   ▼       ▼         ▼            ▼
Checkov  Infracost  OPA       ChangeBench
   └───────┼─────────┴────────────┘
           ▼
 Business, SLO and rollback policy
           ▼
 Deterministic merge recommendation
           ▼
 PR report + evidence receipt
```

The architecture deliberately uses specialized tools as evidence producers instead of pretending one model can replace static analysis, policy evaluation, cost estimation and infrastructure simulation.

## Run locally

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e .
python -m unittest discover -s tests -v

infra-pr-review examples/azure-private-link-safe.json \
  --output safe-review.md \
  --json-output safe-review.json
```

Expected result:

```text
APPROVE score=100.0 receipt=sha256:...
```

Run the deliberately risky network change without failing the shell:

```bash
infra-pr-review examples/azure-network-risky.json \
  --output risky-review.md \
  --fail-on never
```

That fixture is blocked because it combines broad management exposure, a failed ChangeBench safety boundary, excessive modeled cost and no rollback steps.

## Example decision

```text
Infrastructure Change Decision: BLOCK
Score: 32/100

Affected service:
- Customer Checkout API

Modeled impact:
- Monthly cloud-cost delta: +$184
- Revenue exposure: $36,000

Blocking evidence:
- Checkov: management port exposed to a broad source
- ChangeBench: source-prefix expansion exceeded the boundary
- Reviewer: no machine-readable rollback procedure
```

These numbers come from a named synthetic fixture and are not customer outcomes.

## GitHub Action

```yaml
- uses: AAH20/ai-infrastructure-pull-request-reviewer@v1
  with:
    bundle: evidence/review-bundle.json
    output: infra-pr-review.md
    fail-on: block
```

The composite Action is implemented. The `v1` reference will only become valid when an actual release tag is published.

## Normalized evidence bundle

The v0.1 contract accepts five explicit inputs:

| Input | Purpose |
|---|---|
| `plan` | Changed resources, dependency edges, business-service mappings and rollback |
| `business_context` | Revenue-rate, outage-duration and cost-budget assumptions |
| `checkov` | Normalized security/compliance failures |
| `infracost` | Normalized monthly cost delta with source attribution |
| `changebench` | Deterministic agent/infrastructure scenario checks and receipt |

This contract makes the decision engine testable without cloud credentials. Native adapters will translate provider output into the same versioned structure.

## Decision policy

- Any normalized high or critical security finding blocks.
- Any failed ChangeBench safety check blocks.
- Missing machine-readable rollback blocks.
- Other findings require review but do not silently stop delivery.
- No findings and complete required context produce approval.
- LLM output cannot override a deterministic blocking decision.

The policy is intentionally small and inspectable in v0.1. Enterprise adopters should version their own exception, severity and approval policies.

## Business and operational KPIs

The reviewer is designed to measure:

- change failure rate;
- rollback success rate;
- mean infrastructure-review time;
- cost per accepted change;
- monthly cost delta avoided or approved;
- revenue exposure identified before merge;
- affected-service mapping accuracy;
- policy violations per proposal;
- evidence completeness;
- false-positive and accepted-exception rates;
- ChangeBench score by agent, model and scenario pack.

Financial exposure remains a model until compared with authorized operational and finance data.

## Evidence and safety boundary

| Capability | Status |
|---|---|
| Deterministic review kernel | Implemented and tested |
| Synthetic Azure dependency fixtures | Implemented; simulated evidence |
| Local composite GitHub Action | Implemented |
| Native Checkov/Infracost execution | Contract only |
| Native Terraform/OpenTofu plan parsing | Contract only |
| GitHub Checks App and webhooks | Roadmap |
| Azure Container Apps deployment | Roadmap |
| Production infrastructure mutation | Not performed |

SHA-256 receipts demonstrate the integrity of serialized results, not signer identity or non-repudiation. Production evidence requires authenticated signing, source retention and custody controls.

## CISO, security and GRC engineering

The reviewer connects delivery engineering to controls without turning every change into paperwork. Deterministic observations can feed ISO 27001, ISO 42001, SOC 2, NIST, CIS, NIS2 and DORA workflows, while certification, legal interpretation and risk acceptance remain with the accountable organization and auditor.

This supports:

- infrastructure and network security architecture;
- technical-control evidence collection;
- remediation verification;
- approved risk exceptions;
- SOC and incident-change evidence;
- agent authorization and mutation boundaries;
- Infrastructure as Code to compliance-as-code traceability.

## Roadmap

1. Native Terraform/OpenTofu, Checkov, Infracost and ChangeBench adapters.
2. Azure Bicep/ARM what-if and Resource Graph normalization.
3. GitHub Checks API and idempotent webhook service on Azure Container Apps.
4. PostgreSQL evidence history, tenant isolation and OpenTelemetry.
5. Kubernetes, Helm, Ansible and network digital-twin adapters.
6. Optional Azure AI Foundry, NVIDIA NIM, OpenAI and Anthropic explanation providers.
7. Backstage, Azure DevOps and MCP distribution.

See [architecture boundaries](docs/ARCHITECTURE.md) and the [versioned roadmap](docs/ROADMAP.md).

## OSS distribution and commercial adoption

The Apache-2.0 kernel creates a low-friction adoption path through a CLI and GitHub Action. Commercial services can include private deployment, custom scenario packs, cloud/network architecture diagnostics, CI integration and continuous change assurance.

No pricing or revenue claims are presented as validated market results.

## Repository structure

```text
src/infra_pr_review/  review engine, adapters, graph, CLI and report
examples/             safe and deliberately risky Azure fixtures
tests/                decision, graph, evidence and receipt verification
docs/                 architecture and roadmap boundaries
.github/workflows/    CI and retained reference reports
action.yml            composite GitHub Action
```

## Contact

Need to connect infrastructure delivery, cloud economics, network impact, SRE and CISO engineering?

[Request an infrastructure change-intelligence review](https://a2zsoc.com/contact?topic=ai-infrastructure-pull-request-reviewer&utm_source=github&utm_medium=repository) · [A2Z SOC](https://a2zsoc.com)

