# Terraform Layout (Azure Production)

This folder contains the production IaC skeleton for Azure deployment.

## Structure

- `envs/prod`: root module wiring all child modules.
- `modules/*`: reusable modules for network, compute, data, streaming, and observability.

## Next Steps

1. Fill module resources.
2. Configure remote state (Azure Storage backend).
3. Add CI plan/apply workflow with manual approval gates.
