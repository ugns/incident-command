
# Copilot Instructions for incident-command

## Architecture Overview
- **Serverless API** for incident management: volunteers, activity logs, periods, organizations, units, incidents
- **AWS Lambda** handlers in `lambda/` (one per resource)
- **Shared code** in `src/EventCoord/` (models, utils, feature flags, auth)
- **Infrastructure as code** in `terraform/` (DynamoDB, Lambda, API Gateway)
- **CI/CD**: Build/package via Makefile and GitHub Actions

## Key Patterns & Conventions
- **Lambda handlers** always import shared code via Lambda Layer: `from EventCoord.models.<resource> import ...`, `from EventCoord.utils.response import build_response`
- **CORS**: Each handler defines its own `cors_headers` and passes to `build_response(headers=...)`
- **Auth**: JWT-based, user info in claims; use `check_auth` in `src/EventCoord/client/auth.py` for protected handlers
- **Feature flags**: Use `src/EventCoord/launchdarkly/flags.py` and always pass user/org context
- **DynamoDB**: All tables scoped by `org_id` (partition key); resource-specific sort keys; GSIs for secondary queries
- **Model methods**: Each model in `src/EventCoord/models/` provides CRUD and GSI query helpers (see `Volunteer.get_or_create_by_email`, `ActivityLog.list_by_volunteer`, etc.)
- **Response utility**: Use `build_response` from `src/EventCoord/utils/response.py` for all Lambda responses
- **Handler structure**: Auth first, parse method/path, route to model methods, always return via `build_response`

## Terraform & Infrastructure
- Lambda function resources: `lambda.tf`
- DynamoDB tables: `dynamodb.tf`
- REST API Gateway resources: `api_gateway_*.tf`
- WebSockets API Gateway resources: `ws_api_gateway_*.tf`
- IAM policies: Include table ARN and `/index/*` for GSI access
- Use existing resource names from Terraform files; do not invent new names

## Developer Workflows
- **Build Lambda Layer**: `make install-deps`
- **Local dev venv**: `make dev-venv` (installs shared code as editable)
- **Deploy**: `terraform apply` in `terraform/`
- **CI/CD**: Artifacts built/uploaded via GitHub Actions

## Integration Points
- **LaunchDarkly**: Feature flag checks in `src/EventCoord/launchdarkly/flags.py` (SDK key in env)
- **DynamoDB**: Table and GSI names must match Terraform; all model queries use correct keys/indexes
- **JWT**: All handlers expect JWT in `Authorization` header; claims used for org scoping

## Error Handling & Response Consistency
- Handlers return consistent error responses: 400 (missing IDs), 404 (not found), 405 (method not allowed)
- All handlers use the same `cors_headers` pattern and return via `build_response`

## Examples
- To add a resource: create model in `src/EventCoord/models/`, handler in `lambda/`, update Terraform for table/indexes
- To add a GSI query: add index in Terraform and method in model (see `list_by_volunteer` in `ActivityLog`)
- To change CORS: update `cors_headers` in handler

## Key Files/Dirs
- `src/EventCoord/models/` — Data models (CRUD, GSI helpers)
- `src/EventCoord/utils/response.py` — Lambda response builder
- `lambda/<resource>/handler.py` — Lambda entrypoints
- `terraform/` — Infrastructure definitions
- `Makefile` — Build/dev workflow
- `README.md` — API and model docs

---
If unsure about a pattern, check similar usage in other handlers/models. Always follow the structure and naming conventions in this codebase.
