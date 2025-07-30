# Copilot Instructions for incident-command

## Project Architecture
- **Serverless API** for incident management (volunteers, activity logs, ICS-214 periods, organizations, units, incidents)
- **AWS Lambda** functions in `lambda/` (one handler per resource)
- **Shared code** in `shared/` (models, utils, feature flags, auth, etc.)
- **Infrastructure as code** in `terraform/` (DynamoDB, Lambda, API Gateway)
- **CI/CD**: Layer/package build and artifact upload via Makefile and GitHub Actions

## Key Patterns & Conventions
- **All Lambda handlers** import shared code via Lambda Layer; use `from shared.models.<resource> import ...` and `from shared.utils.response import build_response`
- **CORS headers**: Each handler defines its own `cors_headers` and passes them to `build_response(headers=...)`
- **Auth**: JWT-based, with user info in claims; `check_auth` in `shared/client/auth.py` is used in all protected handlers
- **Feature flags**: Use `shared/launchdarkly/flags.py` and always pass user/org context
- **DynamoDB**: All tables are scoped by `org_id` (partition key); most have a resource-specific sort key (e.g., `volunteerId`, `periodId`, etc.)
- **GSIs**: Used for secondary queries (e.g., `email-index` on volunteers, `VolunteerIdIndex` on activity logs, `incidentId-index` and `unitId-index` on periods)
- **Model methods**: Each model in `shared/models/` provides CRUD and GSI query helpers (e.g., `Volunteer.get_or_create_by_email`, `ActivityLog.list_by_volunteer`, `Period.list_by_unit`)
- **Response utility**: Use `build_response` from `shared/utils/response.py` for all Lambda responses
- **Handler structure**: Each handler starts with auth, parses method/path, and routes to model methods; always returns via `build_response`

## Additional Copilot Rules for Consistency and Production-Readiness

### Lambda Handler and Model Imports
- Always use `from models.<resource> import ...` and `from utils.response import build_response` in Lambda handlers. Never use relative or local imports for shared code.

### Handler and Model Method Signatures
- Handlers and models must use the same method signatures and data shapes as existing resources (e.g., `create(org_id, item: dict)`, `update(org_id, id, item: dict)`, `list(org_id)`).
- All CRUD handlers must use `pathParameters` for resource IDs and parse JSON bodies for POST/PUT.

### Environment Variables
- Only add environment variables to Lambda functions if they are actually used in the handler or model code. Do not add unused variables.

### Terraform Resource Patterns
- Lambda function resources must go in `lambda.tf`.
- DynamoDB table resources must go in `dynamodb.tf`.
- All API Gateway resources for a model must go in their own `api_gateway_{model}.tf` file and not be mixed with other models.
- All DynamoDB tables must be included in the Lambda IAM policy with both table ARN and `/index/*` for GSI access.
- When generating Terraform, always examine the existing Terraform files to identify and use the correct resource names. Never reference a resource name that does not exist in the codebase.

### CORS and Response Consistency
- All handlers must use the same `cors_headers` pattern and always return responses via `build_response`.

### No Unused Boilerplate
- Do not generate unused code, variables, or Terraform resources. Only include what is required for the resource.

### Testing and Validation
- Generated code should be ready to deploy and test, with no manual refactoring needed to match project conventions.

### Error Handling
- All handlers must return consistent error responses (e.g., 400 for missing IDs, 404 for not found, 405 for method not allowed).

### Shared Code Usage
- Always use shared utility functions and models; do not duplicate logic in handlers.

### Documentation and Comments
- Add comments only where they clarify non-obvious logic, not for standard patterns or boilerplate.

## Developer Workflows
- **Build Lambda Layer**: `make install-deps` (see Makefile)
- **Local dev venv**: `make dev-venv` (installs shared code as editable)
- **Deploy**: `terraform apply` in `terraform/`
- **CI/CD**: Artifacts built and uploaded via GitHub Actions (see workflow YAML)

## Integration Points
- **LaunchDarkly**: Feature flag checks in `shared/launchdarkly/flags.py` (requires SDK key in env)
- **DynamoDB**: Table and GSI names must match Terraform definitions; all model queries use correct keys/indexes
- **JWT**: All handlers expect JWT in `Authorization` header; claims are used for org scoping

## Examples
- To add a new resource, create a model in `shared/models/`, a handler in `lambda/`, and update Terraform for table/indexes
- To add a new GSI query, add the index in Terraform and a method in the model (see `list_by_volunteer` in `ActivityLog`)
- To change CORS, update the `cors_headers` dict in each handler

## Key Files/Dirs
- `shared/models/` — All data models (CRUD, GSI helpers)
- `shared/utils/response.py` — Standard Lambda response builder
- `lambda/<resource>/handler.py` — Lambda entrypoints
- `terraform/` — Infrastructure definitions
- `Makefile` — Build/dev workflow
- `README.md` — API and model docs

---
If you are unsure about a pattern, check for similar usage in other handlers/models. When adding new features, follow the structure and naming conventions in the existing codebase.
