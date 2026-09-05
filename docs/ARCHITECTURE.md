# Architecture and trust boundaries

The reviewer uses normalized evidence from specialized tools and makes a deterministic merge recommendation. It does not replace those tools and does not grant an LLM authority over production infrastructure.

## Implemented in v0.1

- Normalized plan, dependency, business-context, Checkov, Infracost and ChangeBench contracts
- Downstream dependency closure
- Severity and mutation-boundary decision policy
- Cost-budget and rollback gates
- Business-service and revenue-exposure reporting
- Deterministic integrity receipt
- CLI and composite GitHub Action

## Integration contracts, not current live capabilities

- Native Terraform/OpenTofu plan parser
- Azure Bicep/ARM what-if
- Kubernetes server-side dry run
- GitHub Checks API application
- Live Checkov, Infracost and ChangeBench execution
- Azure Container Apps webhook service
- MCP and model-provider explanation adapters

Adapters must preserve raw source artifacts, identify tool versions and normalize output without silently changing severity. An LLM may summarize or propose remediation only after the deterministic decision is complete.

