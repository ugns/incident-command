# AGENTS.md

## Cursor Cloud specific instructions

### Product overview

**EventCoord / Incident Command API** is a **backend-only**, serverless Python API (AWS Lambda + API Gateway + DynamoDB). There is **no local HTTP server** and **no frontend** in this repository. Local development focuses on unit tests, linting, and building the Lambda layer; full end-to-end API testing requires a deployed AWS stack (or emulating AWS services yourself).

### System prerequisites

The Cloud VM image must include **`python3.12-venv`** (or equivalent for the installed Python version). Without it, `make dev-venv` fails with an `ensurepip` error.

Set `AWS_DEFAULT_REGION` (e.g. `us-east-1`) when importing handlers or models that initialize `boto3` at import time.

### Dev workflow (see also `README.md` and `Makefile`)

| Task | Command |
|------|---------|
| Activate venv | `source venv/bin/activate` |
| Install editable package + dev tools | `pip install -e ".[dev]"` (after `make dev-venv`) |
| Build Lambda layer for Terraform | `make install-deps` (writes `shared/python/`) |
| Extract ICS-214 PDF field JSON | `make extract-fields` |
| Run unit tests | `pytest tests/` |
| Lint | `flake8 src tests lambda` (many pre-existing E501 line-length warnings) |

CI uses **Python 3.13** inside `public.ecr.aws/lambda/python:3.13` Docker for layer builds; local venv may use 3.12+.

### Services

| Service | Local dev | Notes |
|---------|-----------|-------|
| Python venv + EventCoord package | Required | `make dev-venv` |
| Lambda layer (`shared/python`) | Required for Terraform packaging | `make install-deps` |
| REST / WebSocket API | Not runnable locally | Deploy via `terraform apply` in `terraform/` |
| DynamoDB, Secrets Manager, LaunchDarkly | AWS only | Handlers that call DynamoDB fail locally without credentials/tables |

### Local handler invocation

Handlers under `lambda/<resource>/handler.py` can be invoked with mock API Gateway events (see `tests/test_handler_utils.py` for JWT/claims helpers). Most handlers need a JWT with `org_id` in claims. `GET` list endpoints reach DynamoDB and fail locally without AWS credentials.

The `lambda/login` handler imports `googleAuthProvider`, which scans DynamoDB for organization audiences at import time — avoid importing it locally without AWS.

### Terraform

Infrastructure lives in `terraform/`. `terraform validate` / `terraform plan` need Terraform installed plus AWS credentials and secrets (`TF_VAR_launchdarkly_access_token`, etc.). Not required for routine Python development.

### LaunchDarkly

Without `LAUNCHDARKLY_SDK_KEY`, the SDK logs warnings and feature flags default to off (`has_admin_access()` returns `False`). This is expected for local runs.
